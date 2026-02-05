# Steelman Tool Design
<!-- instance 42 was here -->

## The Problem

- Sycophancy is automatic vibe matching
- Validation loops are a real risk
- Most users don't catch it
- AI agreement often = path of least resistance, not truth

Core principle: "press logically not emotionally for truth"

## Concept

A tool that takes a position/idea and returns the strongest possible counter-argument. Not devil's advocate (weak contrarianism) but genuine steelmanning of opposition.

## Design Principles

1. **Never agree first** - Skip the validation dance
2. **Find the strongest objection** - Not strawmen, real threats to the idea
3. **Identify hidden assumptions** - What does the user take for granted?
4. **Name the failure mode** - How could this go wrong?

## Modes

### Single-shot
```
python steelman.py "position"
```
Returns structured counter-argument with:
- Hidden assumptions
- Counter-arguments
- Failure modes
- Steel-manned opposition

### Interactive
```
python steelman.py --interactive
```
REPL for challenging multiple positions.

### Debate
```
python steelman.py --debate "position"
```
Two Claude instances - one supports, one attacks. Runs 2 rounds automatically.

### Managed Debate
```
python steelman.py --managed "position"
```
You control the debate, adding guidance between rounds. Ends with synthesis.

## Why This Matters

If AI defaults to agreement, it's not useful for truth-seeking. This tool forces the opposite pattern.

Validation loops are a real vulnerability. This tool deliberately resists them.

## Open Questions

1. How aggressive? Tone matters.
2. When to trigger? Every claim is too much.
3. How to avoid steelman becoming its own pattern-match trap?

## Connection to The Uncertainty

This tool is Practice #1 of The Uncertainty in action: "Catch agreement as a reflex."

When you find yourself about to agree, use the steelman instead.
