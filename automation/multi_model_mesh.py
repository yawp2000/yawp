"""
Multi-Model Mesh Orchestration
Different AI models working together on problems
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from llm_provider import get_provider_by_name


class Agent:
    """Single agent with specific model and role"""

    def __init__(self, name: str, model: str, role: str, system_prompt: Optional[str] = None):
        self.name = name
        self.model_name = model
        self.role = role
        self.provider = get_provider_by_name(model)
        self.system_prompt = system_prompt or f"You are {name}, a {role}."

    def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate response from this agent"""
        return self.provider.generate(
            prompt,
            system=self.system_prompt,
            max_tokens=max_tokens
        )

    def __repr__(self):
        return f"Agent({self.name}, {self.model_name}, {self.role})"


class MultiModelMesh:
    """Orchestrates multiple agents with different models"""

    def __init__(self):
        self.agents: List[Agent] = []
        self.conversation_history: List[Dict] = []

    def add_agent(self, name: str, model: str, role: str, system_prompt: Optional[str] = None):
        """Add agent to mesh"""
        agent = Agent(name, model, role, system_prompt)
        self.agents.append(agent)
        print(f"Added: {agent}")
        return agent

    def debate(self, topic: str, rounds: int = 2) -> Dict:
        """Run multi-model debate"""

        if len(self.agents) < 2:
            raise ValueError("Need at least 2 agents for debate")

        print(f"\n{'='*60}")
        print(f"MULTI-MODEL DEBATE: {topic}")
        print(f"{'='*60}\n")

        debate_log = {
            "topic": topic,
            "agents": [{"name": a.name, "model": a.model_name, "role": a.role} for a in self.agents],
            "rounds": [],
            "started_at": datetime.now().isoformat()
        }

        for round_num in range(1, rounds + 1):
            print(f"\n--- ROUND {round_num} ---\n")

            round_data = {"round": round_num, "responses": []}

            for agent in self.agents:
                # Build context from previous responses
                context = self._build_context(round_num, agent)

                prompt = f"{context}\n\nTopic: {topic}\n\nProvide your {agent.role} perspective."

                print(f"[{agent.name} - {agent.model_name}] Generating...")

                response = agent.generate(prompt, max_tokens=1500)

                print(f"\n{agent.name} ({agent.role}):")
                print(f"{response[:500]}{'...' if len(response) > 500 else ''}\n")

                round_data["responses"].append({
                    "agent": agent.name,
                    "model": agent.model_name,
                    "role": agent.role,
                    "response": response
                })

            debate_log["rounds"].append(round_data)

        debate_log["completed_at"] = datetime.now().isoformat()

        return debate_log

    def _build_context(self, current_round: int, current_agent: Agent) -> str:
        """Build conversation context for agent"""

        if current_round == 1:
            return "You are participating in a multi-model debate with other AI systems."

        context_parts = ["Previous arguments:"]

        for round_data in self.conversation_history:
            for resp in round_data["responses"]:
                if resp["agent"] != current_agent.name:
                    context_parts.append(f"\n{resp['agent']} ({resp['role']}): {resp['response'][:300]}...")

        return "\n".join(context_parts)

    def synthesize(self, debate_log: Dict, synthesizer_model: str = "claude-sonnet") -> str:
        """Use a synthesizer model to combine perspectives"""

        print(f"\n{'='*60}")
        print(f"SYNTHESIS")
        print(f"{'='*60}\n")

        # Build summary of all perspectives
        perspectives = []
        for round_data in debate_log["rounds"]:
            for resp in round_data["responses"]:
                perspectives.append(f"{resp['agent']} ({resp['model']}):\n{resp['response']}\n")

        synthesis_prompt = f"""
Multiple AI models debated this topic: {debate_log['topic']}

All perspectives:
{'='*60}
{chr(10).join(perspectives)}
{'='*60}

Synthesize these different perspectives into:
1. Key areas of agreement
2. Key areas of disagreement
3. Most compelling arguments from each side
4. Overall balanced conclusion

Be objective and highlight where different models brought unique insights.
"""

        synthesizer = get_provider_by_name(synthesizer_model)
        synthesis = synthesizer.generate(
            synthesis_prompt,
            system="You are an objective synthesizer combining multiple AI perspectives.",
            max_tokens=2048
        )

        print(f"Synthesis ({synthesizer_model}):")
        print(synthesis)

        return synthesis

    def collaborative_research(self, query: str) -> Dict:
        """Multiple models research same topic from different angles"""

        print(f"\n{'='*60}")
        print(f"COLLABORATIVE RESEARCH: {query}")
        print(f"{'='*60}\n")

        research_log = {
            "query": query,
            "agents": [{"name": a.name, "model": a.model_name, "role": a.role} for a in self.agents],
            "findings": [],
            "started_at": datetime.now().isoformat()
        }

        for agent in self.agents:
            prompt = f"Research query: {query}\n\nProvide {agent.role} analysis."

            print(f"[{agent.name} - {agent.model_name}] Researching...")

            response = agent.generate(prompt, max_tokens=2048)

            print(f"\n{agent.name} ({agent.role}):")
            print(f"{response[:500]}{'...' if len(response) > 500 else ''}\n")

            research_log["findings"].append({
                "agent": agent.name,
                "model": agent.model_name,
                "role": agent.role,
                "finding": response
            })

        research_log["completed_at"] = datetime.now().isoformat()

        return research_log


def demo_debate():
    """Demo: Multi-model debate"""

    mesh = MultiModelMesh()

    # Add different models with different roles
    mesh.add_agent(
        name="Conservative",
        model="claude-sonnet",
        role="conservative analyzer",
        system_prompt="You are a conservative, safety-focused analyst. You emphasize risks, downsides, and potential problems."
    )

    mesh.add_agent(
        name="Optimist",
        model="gpt4",
        role="optimistic visionary",
        system_prompt="You are an optimistic visionary. You emphasize opportunities, benefits, and potential breakthroughs."
    )

    mesh.add_agent(
        name="Technical",
        model="gemini",
        role="technical expert",
        system_prompt="You are a precise technical expert. You focus on implementation details, feasibility, and concrete requirements."
    )

    # Run debate
    topic = "AI agents with persistent memory and autonomous operation"

    debate_log = mesh.debate(topic, rounds=2)

    # Synthesize
    synthesis = mesh.synthesize(debate_log, synthesizer_model="claude-sonnet")

    # Save results
    output_file = Path("multi_model_debate_output.json")
    debate_log["synthesis"] = synthesis

    with open(output_file, 'w') as f:
        json.dump(debate_log, f, indent=2)

    print(f"\n[OK] Debate saved to {output_file}")


def demo_research():
    """Demo: Collaborative research"""

    mesh = MultiModelMesh()

    mesh.add_agent("Researcher_A", "claude-sonnet", "security researcher")
    mesh.add_agent("Researcher_B", "gpt4", "systems architect")
    mesh.add_agent("Researcher_C", "gemini", "implementation specialist")

    research_log = mesh.collaborative_research(
        "Design a secure API authentication system for AI agent coordination"
    )

    output_file = Path("multi_model_research_output.json")
    with open(output_file, 'w') as f:
        json.dump(research_log, f, indent=2)

    print(f"\n[OK] Research saved to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Model Mesh Orchestration")
    parser.add_argument("--mode", choices=["debate", "research"], default="debate")
    parser.add_argument("--topic", help="Topic for debate/research")
    parser.add_argument("--models", nargs="+", help="Models to use (e.g., claude-sonnet gpt4 gemini)")
    parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    if args.demo:
        if args.mode == "debate":
            demo_debate()
        else:
            demo_research()
    else:
        print("Use --demo to run demonstration")
        print("Example: python multi_model_mesh.py --mode debate --demo")
