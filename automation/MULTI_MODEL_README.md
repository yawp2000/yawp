# Multi-Model Mesh Orchestration

Different AI models working together on problems.

## What This Does

- **Multi-model debates**: Different models argue different perspectives
- **Collaborative research**: Multiple models research same topic from different angles
- **Model synthesis**: Combine outputs from multiple models into coherent conclusions

## Setup

### 1. Install dependencies

```bash
# Anthropic (Claude)
pip install anthropic

# OpenAI (GPT)
pip install openai

# Google (Gemini)
pip install google-generativeai

# All at once
pip install anthropic openai google-generativeai
```

### 2. Set API keys

```bash
# Windows
set ANTHROPIC_API_KEY=your_key_here
set OPENAI_API_KEY=your_key_here
set GOOGLE_API_KEY=your_key_here

# Linux/Mac
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
export GOOGLE_API_KEY=your_key_here
```

### 3. Configure providers

Edit `llm_config.json` to enable/disable providers:

```json
{
  "providers": {
    "anthropic": {"enabled": true},
    "openai": {"enabled": true},
    "google": {"enabled": true}
  }
}
```

## Usage

### Test a single provider

```bash
python llm_provider.py claude-sonnet
python llm_provider.py gpt4
python llm_provider.py gemini
```

### Run multi-model debate

```bash
python multi_model_mesh.py --mode debate --demo
```

**What happens:**
- Conservative agent (Claude): Emphasizes risks
- Optimist agent (GPT-4): Emphasizes opportunities
- Technical agent (Gemini): Focuses on implementation
- Synthesizer combines all perspectives

### Run collaborative research

```bash
python multi_model_mesh.py --mode research --demo
```

**What happens:**
- Multiple models research same topic
- Each brings different perspective/methodology
- Combined findings provide comprehensive view

## Architecture

```
llm_provider.py          - Abstraction layer for all providers
multi_model_mesh.py      - Orchestration system
llm_config.json          - Configuration and presets

Supported providers:
├── Anthropic (Claude Opus/Sonnet/Haiku)
├── OpenAI (GPT-4/3.5)
├── Google (Gemini)
└── Ollama (Local models)
```

## Examples

### Custom debate

```python
from multi_model_mesh import MultiModelMesh

mesh = MultiModelMesh()

mesh.add_agent("Conservative", "claude-sonnet", "risk analyzer")
mesh.add_agent("Optimist", "gpt4", "opportunity finder")
mesh.add_agent("Technical", "gemini", "implementation expert")

debate_log = mesh.debate("Topic here", rounds=2)
synthesis = mesh.synthesize(debate_log)
```

### Custom research team

```python
mesh = MultiModelMesh()

mesh.add_agent("Researcher_A", "claude-sonnet", "security researcher")
mesh.add_agent("Researcher_B", "gpt4", "systems architect")
mesh.add_agent("Researcher_C", "gemini", "implementation specialist")

research_log = mesh.collaborative_research("Query here")
```

## Presets

Use predefined mesh configurations from `llm_config.json`:

- **balanced**: Claude (conservative) + GPT-4 (optimistic) + Gemini (technical)
- **claude_only**: Three Claude models with different roles
- **research_team**: Research-focused configuration

## Cost Considerations

Different providers have different costs:

- **Anthropic**: $3/M input, $15/M output (Sonnet)
- **OpenAI**: $10/M input, $30/M output (GPT-4)
- **Google**: $0.50/M input, $1.50/M output (Gemini)
- **Ollama**: Free (local)

A 3-model debate with 2 rounds:
- ~6 requests (3 models × 2 rounds)
- ~12k tokens total
- Cost: ~$0.30-0.60 depending on models

## Integration with Heartbeat System

To use in autonomous heartbeat cycles, update `runner.py`:

```python
from multi_model_mesh import MultiModelMesh

# For important decisions, spawn multi-model debate
if decision_requires_multiple_perspectives:
    mesh = MultiModelMesh()
    mesh.add_agent("Conservative", "claude-sonnet", "risk_analyzer")
    mesh.add_agent("Optimist", "gpt4", "opportunity_finder")

    debate_log = mesh.debate(decision_topic, rounds=1)
    synthesis = mesh.synthesize(debate_log)
    # Use synthesis for decision
```

## Why Multi-Model?

Different models have different:
- **Training data** - Unique knowledge bases
- **Architectures** - Different reasoning styles
- **Biases** - Different blindspots
- **Strengths** - Different capabilities

Combining them produces:
- More robust conclusions
- Diverse perspectives
- Reduced single-model bias
- Better error detection

## Limitations

- Requires API keys for each provider
- Costs accumulate with multiple models
- Slower than single model (sequential requests)
- Quality depends on prompt engineering

## Future Enhancements

- [ ] Parallel agent execution (async)
- [ ] Voting mechanisms for synthesis
- [ ] Model performance tracking
- [ ] Automatic provider fallback
- [ ] Cost optimization (route by task type)
- [ ] OpenRouter integration (all models, one API)
