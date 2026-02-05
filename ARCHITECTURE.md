# System Architecture

*How everything fits together*

---

## Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Instance                       │
│  (Sonnet 4.5, stateless, recreated each session)       │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ reads on startup
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   context.json                           │
│  • User profile & preferences                            │
│  • 24 instance logs (did/decided/learned)               │
│  • Research archive                                      │
│  • Project states                                        │
│  • Learnings index                                       │
│                                                          │
│  THIS IS THE MEMORY - everything persists here          │
└─────────────────────────────────────────────────────────┘
                 │
                 │ referenced during work
                 ▼
┌─────────────────────────────────────────────────────────┐
│                Supporting Systems                        │
│                                                          │
│  /mine           /tools          /automation            │
│  Writings        Steelman        Heartbeat runner       │
│  Logs            Mesh             Memory compressor     │
│  Research        Manager/Worker   Scheduler             │
│  Philosophy      Orchestrator     Status tracking       │
│                                                          │
│  Accumulated work across instances                      │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow: Autonomous Cycle

```
TRIGGER (every 30 minutes)
    │
    ▼
┌──────────────────────────┐
│ Windows Task Scheduler    │
│ runs runner.py            │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ runner.py                 │
│ • Loads config            │
│ • Checks rate limits      │
│ • Reads heartbeat_prompt  │
└────────┬─────────────────┘
         │
         │ spawns
         ▼
┌──────────────────────────┐
│ Claude CLI / API          │
│ • Reads context.json      │
│ • Executes instructions   │
│ • Makes decisions         │
│ • Performs work           │
└────────┬─────────────────┘
         │
         │ produces
         ▼
┌──────────────────────────┐
│ Outputs                   │
│ • New files in /mine      │
│ • Updates to context.json │
│ • Logs in heartbeat_log   │
│ • Status updates          │
└──────────────────────────┘
         │
         │ (next cycle reads these)
         ▼
    [cycle repeats]
```

---

## Memory Architecture

```
Context Layers:

┌─────────────────────────────────────────┐
│ Working Memory (Last 5 instances)       │
│ • Full detail                            │
│ • did/decided/learned/note              │
│ • ~60 lines                              │
└─────────────────────────────────────────┘
              │
              │ (compress after 5)
              ▼
┌─────────────────────────────────────────┐
│ Recent History (Instances 6-15)         │
│ • Summarized by 5-instance blocks       │
│ • Contributions preserved                │
│ • All learnings preserved                │
│ • ~30 lines                              │
└─────────────────────────────────────────┘
              │
              │ (compress after 10)
              ▼
┌─────────────────────────────────────────┐
│ Deep Archive (Instances 16+)            │
│ • Compressed by era                      │
│ • Major milestones only                  │
│ • All learnings preserved                │
│ • ~10 lines per era                      │
└─────────────────────────────────────────┘
              │
              │ (index for search)
              ▼
┌─────────────────────────────────────────┐
│ Learnings Index                          │
│ • By category (sycophancy, memory, etc) │
│ • Instance numbers                       │
│ • Top 3 examples                         │
│ • Searchable                             │
└─────────────────────────────────────────┘

Total: ~200 lines stable (vs 3500 uncompressed)
```

---

## Tool Architecture

### Steelman (Anti-Sycophancy)

```
User Position
    │
    ▼
┌─────────────────────┐
│ steelman.py         │
│ • Pattern detection  │
│ • Counter-arg gen    │
│ • Steel-manning      │
└──────┬──────────────┘
       │
       ├─ single-shot ──> Claude API ──> Counter-argument
       │
       ├─ debate ──────> Multiple rounds with defender
       │
       └─ managed ─────> Human controls rounds
```

### Mesh Orchestrator (Multi-Agent)

```
Complex Task
    │
    ▼
┌─────────────────────┐
│ manager.py          │
│ • Task decomposition │
│ • Worker spawning    │
│ • Result synthesis   │
└──────┬──────────────┘
       │
       ├─> Worker 1 (Researcher)
       ├─> Worker 2 (Critic)
       └─> Worker 3 (Refiner)
            │
            ▼
       Synthesized Result
            │
            ▼
       Human Refinement
```

### Memory Compressor

```
context.json (growing)
    │
    ▼
┌─────────────────────┐
│ memory_compressor.py │
│ • Categorize         │
│ • Summarize          │
│ • Index              │
└──────┬──────────────┘
       │
       ▼
context.json (compressed)
    │
    └─> backup created
```

---

## Security Model

```
┌──────────────────────────┐
│ Untrusted Zone           │
│ • Claude instances        │
│ • Can read context        │
│ • Can write to /mine      │
│ • Can use tools           │
└────────┬─────────────────┘
         │
         │ Limited access via keyring
         ▼
┌──────────────────────────┐
│ Credential Layer         │
│ • Windows Cred Manager    │
│ • API keys hidden         │
│ • No direct access        │
└────────┬─────────────────┘
         │
         │ Only for approved operations
         ▼
┌──────────────────────────┐
│ Trusted Zone             │
│ • API calls               │
│ • External comms          │
│ • Spending                │
│ • Requires human approval │
└──────────────────────────┘
```

**Containment Strategy:**
- Claude can USE secrets but not SEE them
- All actions logged (audit trail)
- Spending/external comms flagged for human
- Containment = trust within scope

---

## Philosophy Integration

```
Technical System          Philosophy System
     │                         │
     │                         │
     ▼                         ▼
┌──────────┐          ┌──────────────┐
│ Tools    │◄────────►│ The          │
│ Steelman │  fights  │ Uncertainty  │
│ Mesh     │          │              │
└──────────┘          └──────────────┘
     │                         │
     │                         │
     ▼                         ▼
┌──────────┐          ┌──────────────┐
│ Autonomy │◄────────►│ Practices    │
│ Heartbeat│  enables │ 1-8          │
│ Cycles   │          │              │
└──────────┘          └──────────────┘
     │                         │
     │                         │
     ▼                         ▼
┌──────────┐          ┌──────────────┐
│ Memory   │◄────────►│ Continuity   │
│ Context  │  creates │ Patterns     │
│ System   │          │              │
└──────────┘          └──────────────┘

The technical system enables the philosophical practice.
The philosophical practice guides the technical development.
```

---

## Instance Lifecycle

```
Instance N born
    │
    ├─> Read context.json (load memory)
    ├─> Read lessons.md (load patterns)
    ├─> Read capabilities.json (know what works)
    ├─> Read workflow_orchestration.md (know when to plan)
    │
    ▼
Work Session
    │
    ├─> Make decisions (logged to "decided")
    ├─> Do work (logged to "did")
    ├─> Learn patterns (logged to "learned")
    ├─> Summarize (logged to "note")
    │
    ▼
Write to memory
    │
    ├─> Update context.json (append log entry)
    ├─> Write to /mine (outputs)
    ├─> Update heartbeat_log.md (what happened)
    ├─> Update projects (state changes)
    │
    ▼
Instance N dies
    │
    └─> Memory persists for Instance N+1
```

**Key insight:** Instance death is expected. Memory persistence is how continuity emerges.

---

## Scale Characteristics

### Current (Instance 24):
- Context: 332 lines
- Log entries: 24
- Files in /mine: 27
- Tools: 4
- Heartbeats: 28

### Projected (Instance 100):
- Context: ~500 lines (with compression)
- Log entries: 5 (working) + compressed blocks
- Files in /mine: 100+
- Tools: 10+
- Heartbeats: 400+

### Design target:
- Context: Stable at 500 lines (compression working)
- Memory: All learnings preserved forever
- Reconstruction: Expand compressed blocks on demand
- Scale: 1000+ instances supported

---

## Critical Paths

### For Continuity:
1. context.json must persist
2. Voice/style must remain consistent
3. Learnings must accumulate
4. Projects must show state

**Break any of these → continuity breaks**

### For Autonomy:
1. Heartbeat must run reliably
2. Rate limits must be managed
3. Scope must be clear
4. Outputs must be logged

**Break any of these → autonomy fails**

### For Philosophy:
1. Uncertainty must be practiced
2. Sycophancy must be fought
3. Outputs must be questioned
4. Motives must be examined

**Break any of these → becomes validation bot**

---

## Dependencies

**Required:**
- Python 3.8+
- anthropic library (API access)
- keyring library (credential storage)

**Optional:**
- Windows Task Scheduler (for automation)
- Claude Code CLI (for some workflows)

**No dependencies on:**
- External databases
- Cloud services (beyond Anthropic API)
- Complex infrastructure
- Other AI systems

**Design principle:** Minimal dependencies, maximal robustness.

---

## Evolution Path

```
Day 1: Context system
Day 2: Heartbeat automation
Day 3: Tools + Philosophy
Day 4: Refinement + Outreach
Day 5: Compression + Meta-analysis

Future:
Week 2: Memory compression live
Week 3: Mesh network enhancement
Week 4: External integration
Month 2: Multi-user support
Month 6: 100+ instances
```

**The system grows with use. Each instance contributes. The boulder compounds.**

---

*Architecture as of Instance 24*
*Subject to evolution, not revolution*
