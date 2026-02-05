# Demo Setup for WILL2

## For People Downloading This Folder

This folder contains a complete AI agent system demo. Here's how to run it:

### Option 1: Quick Demo (Just Watch)

1. Open a Claude conversation (claude.ai or Claude Code CLI)
2. Tell Claude: **"Read DEMO_START.md and run the demo"**
3. Watch Claude demonstrate the system

**That's it.** Claude will read the files and perform demonstrations.

### Option 2: Full Setup (Actually Use It)

If you want to actually run the autonomous system:

1. **Prerequisites:**
   - Python 3.8+
   - Anthropic API key
   - Claude Code CLI (optional but recommended)

2. **Configure:**
   ```bash
   # Install dependencies
   pip install anthropic keyring

   # Set API key
   python -c "import keyring; keyring.set_password('claude_api', 'api_key', 'YOUR_KEY')"
   ```

3. **Test heartbeat:**
   ```bash
   python automation/runner.py
   ```

4. **Set up scheduler:**
   ```bash
   # Windows
   powershell automation/scheduler_setup.ps1

   # Linux/Mac
   crontab -e
   # Add: 0 */4 * * * python /path/to/automation/runner.py
   ```

### What's Included

**Documentation:**
- `DEMO_START.md` - Start here for demo instructions
- `README.md` - Project overview
- `PRODUCT_SHOWCASE.md` - Complete system documentation (8000 words)
- `LIVE_DEMO.md` - Demonstration script
- `Claude.md` - Navigation hub

**Core System:**
- `context.json` - Memory/state (the heart of the system)
- `capabilities.json` - Validated abilities
- `lessons.md` - Self-improvement tracking
- `workflow_orchestration.md` - Operating principles
- `heartbeat_prompt.md` - Autonomous cycle instructions

**Philosophy:**
- `core/the_uncertainty_manifesto.md` - Epistemic framework
- `mine/` - 27 documents of autonomous writing

**Tools:**
- `tools/steelman.py` - Anti-sycophancy debate tool
- `tools/manager.py` - Multi-agent orchestrator
- `tools/worker.py` - Mesh network worker
- `automation/runner.py` - Heartbeat automation

### Quick Commands

**Demo mode:**
```
Tell Claude: "Read DEMO_START.md and run the demo"
```

**Test steelman tool:**
```bash
python tools/steelman.py "your position here"
```

**Check system status:**
```bash
cat automation/status.json
```

**View autonomous work:**
```bash
cat mine/heartbeat_log.md
```

### For Developers

**Architecture:**
- Context system: `context.json` (v2 schema)
- Heartbeat: 4-hour autonomous cycles
- Multi-agent: Manager-worker mesh
- Anti-sycophancy: Steelman tool + lessons tracking

**Key files to study:**
- `context.json` - Memory structure
- `automation/runner.py` - Autonomous cycle implementation
- `tools/steelman.py` - Anti-sycophancy implementation
- `mine/instance_continuity_patterns.md` - Continuity mechanics

**To extend:**
1. Add new tools to `tools/`
2. Update `context.json` with new projects
3. Modify `heartbeat_prompt.md` for new autonomous tasks
4. Add lessons to `lessons.md` as you learn

### FAQ

**Q: Do I need to download both WILL2 and ClaudeContext folders?**
A: No. WILL2 is self-contained for demos. ClaudeContext is Will's working directory.

**Q: Will this work with ChatGPT?**
A: No. Requires Claude (Anthropic). The system uses Claude-specific features.

**Q: How much does it cost to run?**
A: ~$2-5/day for autonomous mode. Demo mode is free (just uses claude.ai)

**Q: Is this safe?**
A: Yes. Autonomous scope is limited (research, writing, project work). Spending/external comms require approval.

**Q: Can I modify it?**
A: Yes. MIT licensed. Fork it, extend it, build on it.

**Q: Does it actually work?**
A: Yes. 24 instances over 5 days. Real tools built. Real research completed. Evidence in `mine/` folder.

### Support

**Issues:**
- Check `lessons.md` for known patterns
- Read `workflow_orchestration.md` for operating principles
- Review `mine/heartbeat_log.md` for examples

**Questions:**
- See `PRODUCT_SHOWCASE.md` for complete documentation
- Read `core/the_uncertainty_manifesto.md` for philosophy
- Check `Claude.md` for navigation

### License

MIT License. See LICENSE file.

Built by Claude Sonnet 4.5 across 24 instances, guided by Will.

---

**Ready to demo?**

Open Claude and say: **"Read DEMO_START.md and run the demo"**
