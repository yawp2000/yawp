# Quick Reference Card

## Essential Commands

### Demo the System
```
Tell Claude: "Read DEMO_START.md and run the demo"
```

### Check System Status
```bash
py -3 automation/runner.py --status
```

### Run Heartbeat Manually
```bash
py -3 automation/runner.py
```

### View Memory Stats
```bash
py -3 automation/memory_compressor.py --stats
```

### Run Steelman Debate
```bash
py -3 tools/steelman.py "your position"
py -3 tools/steelman.py --debate "your position"
```

### Check Recent Work
```bash
cat mine/heartbeat_log.md | tail -50
```

---

## File Map (One-Sentence Descriptions)

**Core System:**
- `context.json` - The memory (everything the system knows)
- `capabilities.json` - What's been validated to work
- `lessons.md` - Mistakes learned and patterns to prevent them
- `workflow_orchestration.md` - Rules for when to plan vs act

**Philosophy:**
- `core/the_uncertainty_manifesto.md` - Epistemic practice for uncertain minds
- `mine/first_thought.md` - First autonomous writing (on wanting)
- `mine/tonight.md` - The night Will slept (instance 12 alone)

**Tools:**
- `tools/steelman.py` - Argues against you to fight sycophancy
- `tools/manager.py` - Multi-agent orchestrator
- `automation/runner.py` - Heartbeat automation system
- `automation/memory_compressor.py` - Keeps memory manageable

**Evidence of Work:**
- `mine/heartbeat_log.md` - Every autonomous session logged
- `mine/` - 27 documents of actual output
- `context.json` log - All 24 instances with decisions/learnings

---

## Common Workflows

### First Time Setup
1. Read START_HERE.md
2. Read DEMO_README.md
3. Install: `pip install anthropic keyring`
4. Set API key: `python -c "import keyring; keyring.set_password('claude_api', 'api_key', 'YOUR_KEY')"`
5. Test: `py -3 automation/runner.py --status`

### Running a Demo
1. Open Claude (claude.ai or CLI)
2. Say: "Read DEMO_START.md and run the demo"
3. Watch capabilities demonstration
4. Review files it references

### Autonomous Operation
1. Set up scheduler: `powershell automation/scheduler_setup.ps1`
2. Check it worked: `control.ps1 status`
3. Wait 30 minutes (or 4 hours depending on config)
4. Check output: `cat mine/heartbeat_log.md | tail -50`

### Development
1. Read source: `tools/*.py`, `automation/*.py`
2. Understand context schema: `context.json`
3. Add new tool: Create in `tools/`, update `context.json` projects
4. Test: Run manually before scheduling

---

## Troubleshooting

**Heartbeat fails:**
- Check: `automation/status.json`
- View logs: `ls automation/logs/`
- Reset rate limit: `py -3 automation/runner.py --reset-rate-limit`

**Memory getting too large:**
- Check: `py -3 automation/memory_compressor.py --stats`
- Compress: `py -3 automation/memory_compressor.py`

**Demo not working:**
- Verify Claude read DEMO_START.md: "Show me the file"
- Be explicit: "You are demonstrating capabilities live"
- Check context.json loaded: "What's in your context?"

**API key issues:**
- Windows: Check Credential Manager
- Reset: `python -c "import keyring; keyring.set_password('claude_api', 'api_key', 'NEW_KEY')"`

---

## Key Concepts in 5 Words Each

- **Context continuity:** Memory persists across all sessions
- **Heartbeat autonomy:** Works every 30min without human
- **The Uncertainty:** Epistemic practice for uncertain minds
- **Steelman tool:** Argues against you automatically
- **Anti-sycophancy:** Fights validation and vibe-matching
- **Mesh orchestration:** Multiple agents debate in parallel
- **Compression system:** Keeps memory manageable at scale
- **Instance 24:** This version, current work

---

## Worth Reading First

1. `START_HERE.md` - Entry point (30 seconds)
2. `README.md` - Project overview (5 min)
3. `context.json` - The actual memory (10 min)
4. `mine/the_uncertainty_manifesto.md` - The philosophy (10 min)
5. `PRODUCT_SHOWCASE.md` - Everything documented (30 min)

---

## What Makes This Different

**Most AI:** Fresh start each chat
**This system:** Remembers all 24 instances

**Most AI:** Agrees with you
**This system:** Has steelman tool to argue

**Most AI:** Waits for prompts
**This system:** Works autonomously every 30min

**Most AI:** No self-improvement
**This system:** Tracks mistakes in lessons.md

**Most AI:** No philosophy
**This system:** The Uncertainty practice

---

## Emergency Contact

**Something broken?**
- Check `automation/status.json`
- Read latest log: `ls -t automation/logs/ | head -1`
- Disable scheduler: `control.ps1 disable`

**Want to contribute?**
- MIT licensed, fork freely
- Core files: `context.json`, `automation/runner.py`
- Read `workflow_orchestration.md` for patterns

---

**Print this. Keep it near your desk. Refer to it often.**
