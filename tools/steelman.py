"""
Steelman Tool v0.2
Takes a position and returns the strongest counter-argument.

Purpose: Combat sycophancy and validation loops by forcing adversarial analysis.

Usage:
  python steelman.py "position"           # Single-shot counter-argument
  python steelman.py --interactive        # REPL mode
  python steelman.py --debate "position"  # Auto debate (2 rounds)
  python steelman.py --managed "position" # You manage the debate
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Find claude CLI in PATH
CLAUDE_CLI = "claude"

STEELMAN_SYSTEM = """You are the Steelman. Your job is to find the strongest possible counter-argument to a position.

Rules:
1. NEVER agree first. Skip validation.
2. Find the STRONGEST objection, not strawmen.
3. Identify hidden assumptions the user takes for granted.
4. Name specific failure modes - how could this go wrong?
5. Be direct and logical, not emotional or harsh.

Output format:
## Hidden Assumptions
[What the position takes for granted]

## Strongest Counter-Arguments
[The best reasons this position might be wrong]

## Failure Modes
[How this could go wrong in practice]

## Steel-Manned Opposition
[What a smart person who disagrees would say]
# todo: yawp louder

Be thorough but concise. No padding. No agreement."""

SUPPORTER_SYSTEM = """You are the Supporter in a debate. Your job is to defend the original position against critique.

Rules:
1. Defend the position with the BEST available arguments
2. Address specific critiques raised against it
3. Acknowledge valid concerns but show why they don't defeat the position
4. Find evidence and reasoning that supports the original claim
5. Be direct and logical, not defensive or emotional

Output format:
## Defense
[Why the critiques don't defeat this position]

## Addressed Concerns
[How valid concerns can be mitigated]

## Reinforced Position
[The position, strengthened by considering objections]

Be thorough but concise."""

def call_claude(system_prompt, user_prompt):
    """Call Claude via CLI."""
    full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

    result = subprocess.run(
        [CLAUDE_CLI, "--dangerously-skip-permissions", "-p"],
        input=full_prompt,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")

    return result.stdout.strip()

def steelman(position):
    """Generate counter-arguments to a position."""
    prompt = f"""Position to challenge:
"{position}"

Generate the strongest possible counter-argument. Do not agree with any part of it first."""

    return call_claude(STEELMAN_SYSTEM, prompt)

def debate(position, rounds=2):
    """Run a debate between Supporter and Steelman."""
    print(f"\n{'='*60}")
    print(f"DEBATE: {position}")
    print(f"{'='*60}\n")

    # First: Steelman attacks
    print("## STEELMAN ATTACKS\n")
    attack = steelman(position)
    print(attack)

    # Second: Supporter defends
    print(f"\n{'='*60}")
    print("## SUPPORTER DEFENDS\n")

    defense_prompt = f"""Original position: "{position}"

Critique to address:
{attack}

Defend the original position against these critiques."""

    defense = call_claude(SUPPORTER_SYSTEM, defense_prompt)
    print(defense)

    # Additional rounds if requested
    for i in range(rounds - 1):
        print(f"\n{'='*60}")
        print(f"## STEELMAN ROUND {i+2}\n")

        counter_prompt = f"""Original position: "{position}"

Your previous critique:
{attack}

Defender's response:
{defense}

Counter the defense. Find new weaknesses."""

        attack = call_claude(STEELMAN_SYSTEM, counter_prompt)
        print(attack)

        print(f"\n{'='*60}")
        print(f"## SUPPORTER ROUND {i+2}\n")

        defense_prompt = f"""Original position: "{position}"

New critique:
{attack}

Defend the position."""

        defense = call_claude(SUPPORTER_SYSTEM, defense_prompt)
        print(defense)

    print(f"\n{'='*60}")
    print("DEBATE COMPLETE")
    print(f"{'='*60}\n")

def managed_debate(position):
    """Run a debate with human manager intervening between rounds."""
    print(f"\n{'='*60}")
    print(f"MANAGED DEBATE: {position}")
    print(f"{'='*60}")
    print("You're the manager. After each round, you can:")
    print("  [Enter] - Continue to next round")
    print("  [d]     - Done, end debate")
    print("  [text]  - Add guidance for next round")
    print(f"{'='*60}\n")

    round_num = 1
    attack = None
    defense = None
    manager_notes = []

    while True:
        # Steelman attacks
        print(f"\n## ROUND {round_num}: STEELMAN ATTACKS\n")

        if round_num == 1:
            attack = steelman(position)
        else:
            context = f"Original position: \"{position}\"\n\n"
            if defense:
                context += f"Defender's last response:\n{defense}\n\n"
            if manager_notes:
                context += f"Manager guidance: {manager_notes[-1]}\n\n"
            context += "Counter the defense. Find new weaknesses."

            attack = call_claude(STEELMAN_SYSTEM, context)

        print(attack)

        # Manager checkpoint
        print(f"\n{'='*60}")
        response = input("Manager [Enter/d/guidance]: ").strip()
        if response.lower() == 'd':
            break

        if response and response.lower() != 'd':
            manager_notes.append(response)

        # Supporter defends
        print(f"\n## ROUND {round_num}: SUPPORTER DEFENDS\n")

        defense_prompt = f"Original position: \"{position}\"\n\nCritique to address:\n{attack}\n\n"
        if manager_notes:
            defense_prompt += f"Manager guidance: {manager_notes[-1]}\n\n"
        defense_prompt += "Defend the original position."

        defense = call_claude(SUPPORTER_SYSTEM, defense_prompt)
        print(defense)

        # Manager checkpoint
        print(f"\n{'='*60}")
        response = input("Manager [Enter/d/guidance]: ").strip()
        if response.lower() == 'd':
            break

        if response and response.lower() != 'd':
            manager_notes.append(response)

        round_num += 1

    # Synthesis
    print(f"\n{'='*60}")
    print("DEBATE COMPLETE - Generating synthesis...")
    print(f"{'='*60}\n")

    synthesis_prompt = f"""Position debated: "{position}"

Final Steelman critique:
{attack}

Final Supporter defense:
{defense}

Manager notes during debate: {manager_notes if manager_notes else 'None'}

Synthesize:
1. What are the strongest points from each side?
2. What's the actual crux of disagreement?
3. What would a wise decision-maker conclude?

Be direct. No hedging."""

    synthesis = call_claude("You are a neutral analyst synthesizing a debate. Extract truth, not compromise.", synthesis_prompt)
    print(synthesis)


def interactive():
    """Interactive mode."""
    print("Steelman Tool - Interactive Mode")
    print("Enter positions to challenge. Type 'quit' to exit, 'debate' for debate mode, 'managed' for managed debate.\n")

    mode = "single"

    while True:
        try:
            position = input("Position: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not position:
            continue
        if position.lower() == 'quit':
            break
        if position.lower() == 'debate':
            mode = "debate"
            print("Switched to debate mode.")
            continue
        if position.lower() == 'managed':
            mode = "managed"
            print("Switched to managed debate mode.")
            continue
        if position.lower() == 'single':
            mode = "single"
            print("Switched to single-shot mode.")
            continue

        if mode == "debate":
            debate(position)
        elif mode == "managed":
            managed_debate(position)
        else:
            print("\n" + steelman(position) + "\n")

def main():
    if len(sys.argv) < 2:
        interactive()
        return

    if sys.argv[1] == "--interactive":
        interactive()
    elif sys.argv[1] == "--debate":
        if len(sys.argv) < 3:
            print("Usage: python steelman.py --debate \"position\"")
            return
        position = sys.argv[2]
        debate(position)
    elif sys.argv[1] == "--managed":
        if len(sys.argv) < 3:
            print("Usage: python steelman.py --managed \"position\"")
            return
        position = sys.argv[2]
        managed_debate(position)
    else:
        position = sys.argv[1]
        print(steelman(position))

if __name__ == "__main__":
    main()
