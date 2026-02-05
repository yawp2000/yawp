"""
Heartbeat Runner v1.1
Unified automation for Claude autonomous operation.

Modes:
- simple: Single Claude CLI call with heartbeat prompt
- api: Direct Anthropic API with prompt caching (lower cost)
- mesh: Multi-instance orchestration for complex tasks

Features:
- Rate limit detection and exponential backoff
- Health tracking and status updates
- Automatic mode selection based on task type
- Comprehensive logging
- Prompt caching for reduced API costs
"""

import subprocess
import json
import time
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Try to import anthropic SDK for API mode
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Try to import keyring for secure credential storage
try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

def get_api_key():
    """Get API key from secure storage. Never logs or returns the key to callers outside this module."""
    if HAS_KEYRING:
        key = keyring.get_password('claude-heartbeat', 'anthropic-api-key')
        if key:
            return key
    # Fallback to env var
    return os.environ.get('ANTHROPIC_API_KEY')

AUTOMATION_DIR = Path(__file__).parent
CONTEXT_DIR = AUTOMATION_DIR.parent
CONFIG_FILE = AUTOMATION_DIR / "config.json"
STATUS_FILE = AUTOMATION_DIR / "status.json"
CLAUDE_CLI = r"C:\Users\19282\AppData\Roaming\npm\claude.cmd"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_timestamp():
    return datetime.now().isoformat()

def get_log_path(config):
    logs_dir = Path(config["paths"]["logs"])
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return logs_dir / f"heartbeat_{timestamp}.log"

class HeartbeatRunner:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
        self.status = load_json(STATUS_FILE)
        self.log_lines = []

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {msg}"
        print(line)
        self.log_lines.append(line)

    def save_log(self):
        log_path = get_log_path(self.config)
        save_file(log_path, "\n".join(self.log_lines))
        self.log(f"Log saved to {log_path}")
        return log_path

    def update_status(self, **kwargs):
        for key, value in kwargs.items():
            self.status[key] = value
        save_json(STATUS_FILE, self.status)

    def add_history(self, event_type, details=None):
        entry = {
            "timestamp": get_timestamp(),
            "type": event_type,
            "details": details
        }
        self.status["history"].append(entry)
        # Keep last 50 entries
        if len(self.status["history"]) > 50:
            self.status["history"] = self.status["history"][-50:]
        save_json(STATUS_FILE, self.status)

    def is_rate_limited(self):
        """Check if we're in a rate limit cooldown."""
        rate_limited_until = self.status.get("rate_limited_until")
        if rate_limited_until:
            until = datetime.fromisoformat(rate_limited_until)
            if datetime.now() < until:
                self.log(f"Rate limited until {rate_limited_until}", "WARN")
                return True
            else:
                self.update_status(rate_limited_until=None)
        return False

    def detect_rate_limit(self, output):
        """Detect rate limit from CLI output."""
        patterns = [
            r"rate.?limit",
            r"limit.*reset",
            r"too many requests",
            r"429",
            r"quota exceeded"
        ]
        output_lower = output.lower()
        for pattern in patterns:
            if re.search(pattern, output_lower):
                return True
        return False

    def set_rate_limit_cooldown(self, hours=None):
        """Set rate limit cooldown period."""
        if hours is None:
            hours = self.config["rate_limit"]["cooldown_hours"]
        until = datetime.now() + timedelta(hours=hours)
        self.update_status(rate_limited_until=until.isoformat())
        self.log(f"Rate limit cooldown set until {until.isoformat()}", "WARN")

    def run_simple_heartbeat(self):
        """Run a simple single-instance heartbeat via CLI."""
        self.log("Running simple heartbeat (CLI)")

        prompt_path = self.config["paths"]["heartbeat_prompt"]
        prompt = load_file(prompt_path)

        # Run claude CLI - pipe prompt via stdin
        try:
            result = subprocess.run(
                [CLAUDE_CLI, "--dangerously-skip-permissions", "-p"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=str(CONTEXT_DIR)
            )

            output = result.stdout + result.stderr

            if self.detect_rate_limit(output):
                self.log("Rate limit detected in output", "ERROR")
                return False, output, "rate_limit"

            if result.returncode != 0:
                self.log(f"CLI returned non-zero: {result.returncode}", "ERROR")
                return False, output, "cli_error"

            self.log("Heartbeat completed successfully")
            return True, output, None

        except subprocess.TimeoutExpired:
            self.log("Heartbeat timed out after 10 minutes", "ERROR")
            return False, "", "timeout"
        except FileNotFoundError:
            self.log("Claude CLI not found in PATH", "ERROR")
            return False, "", "cli_not_found"
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            return False, str(e), "exception"

    def run_api_heartbeat(self):
        """Run heartbeat via Anthropic API with prompt caching."""
        if not HAS_ANTHROPIC:
            self.log("Anthropic SDK not installed, falling back to CLI", "WARN")
            return self.run_simple_heartbeat()

        self.log("Running API heartbeat with prompt caching")

        # Load context for caching
        context_path = CONTEXT_DIR / "context.json"
        context_content = load_file(context_path)

        # Load heartbeat instructions
        prompt_path = self.config["paths"]["heartbeat_prompt"]
        instructions = load_file(prompt_path)

        # Build system prompt with cached context prefix
        system_parts = [
            {
                "type": "text",
                "text": f"# Your Context (cached)\n\n```json\n{context_content}\n```",
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": instructions
            }
        ]

        try:
            api_key = get_api_key()
            if not api_key:
                self.log("No API key found in credential manager or env var", "ERROR")
                return False, "", "no_api_key"
            client = anthropic.Anthropic(api_key=api_key)

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                system=system_parts,
                messages=[
                    {"role": "user", "content": "Begin your heartbeat session. You have full context above."}
                ]
            )

            output = response.content[0].text

            # Log cache performance
            usage = response.usage
            cache_read = getattr(usage, 'cache_read_input_tokens', 0)
            cache_create = getattr(usage, 'cache_creation_input_tokens', 0)
            if cache_read > 0:
                self.log(f"Cache hit: {cache_read} tokens read from cache")
            if cache_create > 0:
                self.log(f"Cache miss: {cache_create} tokens cached for next call")

            self.log("API heartbeat completed successfully")
            return True, output, None

        except anthropic.RateLimitError as e:
            self.log(f"Rate limit error: {e}", "ERROR")
            return False, str(e), "rate_limit"
        except anthropic.APIError as e:
            error_msg = str(e).lower()
            # Check for credit/payment issues
            if any(term in error_msg for term in ["credit", "payment", "billing", "insufficient", "quota"]):
                self.log(f"No credits available: {e}", "WARN")
                return False, str(e), "no_credits"
            self.log(f"API error: {e}", "ERROR")
            return False, str(e), "api_error"
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            return False, str(e), "exception"

    def run_mesh_heartbeat(self, task=None):
        """Run mesh orchestrator for complex tasks."""
        self.log("Running mesh heartbeat")

        mesh_dir = Path(self.config["paths"]["mesh"])
        orchestrator = mesh_dir / "orchestrator.py"

        if not orchestrator.exists():
            self.log("Mesh orchestrator not found", "ERROR")
            return False, "", "mesh_not_found"

        # If task provided, write it to task.json
        if task:
            task_file = mesh_dir / "task.json"
            save_json(task_file, task)
            # Set status to drafting to kick off the loop
            status_file = mesh_dir / "status.json"
            mesh_status = load_json(status_file)
            mesh_status["state"] = "drafting"
            mesh_status["iteration"] = 0
            save_json(status_file, mesh_status)

        try:
            result = subprocess.run(
                [sys.executable, str(orchestrator), "--max", "3"],
                capture_output=True,
                text=True,
                timeout=900,  # 15 minute timeout for mesh
                cwd=str(mesh_dir),
                env={**os.environ}
            )

            output = result.stdout + result.stderr

            if self.detect_rate_limit(output):
                return False, output, "rate_limit"

            self.log("Mesh heartbeat completed")
            return True, output, None

        except subprocess.TimeoutExpired:
            self.log("Mesh timed out", "ERROR")
            return False, "", "timeout"
        except Exception as e:
            self.log(f"Mesh error: {e}", "ERROR")
            return False, str(e), "exception"

    def run_with_retry(self, mode="simple", task=None):
        """Run heartbeat with retry logic."""
        max_attempts = self.config["retry"]["max_attempts"]
        base_delay = self.config["retry"]["base_delay_seconds"]
        multiplier = self.config["retry"]["backoff_multiplier"]

        for attempt in range(max_attempts):
            if attempt > 0:
                delay = base_delay * (multiplier ** (attempt - 1))
                self.log(f"Retry {attempt + 1}/{max_attempts} after {delay}s delay")
                time.sleep(delay)

            if mode == "mesh":
                success, output, error = self.run_mesh_heartbeat(task)
            elif mode == "api":
                success, output, error = self.run_api_heartbeat()
            else:
                success, output, error = self.run_simple_heartbeat()

            if success:
                return True, output, None

            if error == "rate_limit":
                self.set_rate_limit_cooldown()
                return False, output, "rate_limit"

            if error == "no_credits":
                # Don't retry for no credits - just skip this heartbeat
                return False, output, "no_credits"

            if error in ["cli_not_found", "mesh_not_found", "no_api_key"]:
                # Don't retry for missing dependencies
                return False, output, error

        self.log(f"All {max_attempts} attempts failed", "ERROR")
        return False, output, "max_retries"

    def calculate_adaptive_interval(self):
        """Calculate next heartbeat interval based on recent performance."""
        failures = self.status.get("consecutive_failures", 0)

        if failures >= 3:
            return 240  # 4 hours - significant backoff
        elif failures == 2:
            return 120  # 2 hours - moderate backoff
        elif failures == 1:
            return 60   # 1 hour - gentle backoff
        else:
            return self.config.get("heartbeat_interval_minutes", 30)  # Normal

    def backup_context(self):
        """Create daily backup of context.json."""
        import shutil

        backups_dir = CONTEXT_DIR / "backups"
        backups_dir.mkdir(exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = backups_dir / f"context_{today}.json"

        # Only backup once per day
        if not backup_path.exists():
            context_path = CONTEXT_DIR / "context.json"
            shutil.copy(context_path, backup_path)
            self.log(f"Backup created: {backup_path.name}")

            # Cleanup old backups (keep last 7 days)
            all_backups = sorted(backups_dir.glob("context_*.json"))
            if len(all_backups) > 7:
                for old_backup in all_backups[:-7]:
                    old_backup.unlink()
                    self.log(f"Removed old backup: {old_backup.name}")

    def track_cost(self, tokens_used):
        """Track API costs and check budget."""
        if "costs" not in self.status:
            self.status["costs"] = {
                "total_spend": 0.0,
                "daily_budget": 5.00,
                "today_spend": 0.0,
                "last_reset": datetime.now().strftime("%Y-%m-%d"),
                "currency": "USD"
            }

        # Reset daily spend if new day
        today = datetime.now().strftime("%Y-%m-%d")
        if self.status["costs"]["last_reset"] != today:
            self.status["costs"]["today_spend"] = 0.0
            self.status["costs"]["last_reset"] = today
            self.log("Daily spend reset")

        # Calculate cost (Sonnet 4.5 pricing: $3/M input, $15/M output)
        # Estimate 20% output tokens
        input_tokens = tokens_used * 0.8
        output_tokens = tokens_used * 0.2
        cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)

        self.status["costs"]["total_spend"] += cost
        self.status["costs"]["today_spend"] += cost

        self.log(f"Cost: ${cost:.4f} (today: ${self.status['costs']['today_spend']:.2f})")

        # Check budget
        if self.status["costs"]["today_spend"] >= self.status["costs"]["daily_budget"]:
            self.log("WARNING: Daily budget reached!", "WARN")
            return False  # Signal to skip this heartbeat

        return True

    def check_health(self, display=True):
        """Check system health and optionally display dashboard."""
        try:
            from health_monitor import HealthMonitor

            status_path = STATUS_FILE
            context_path = CONTEXT_DIR / "context.json"

            monitor = HealthMonitor(status_path, context_path)
            metrics = monitor.get_metrics()

            # Log health score
            self.log(f"Health Score: {metrics['health_score']}/100")

            # Display full dashboard if requested and instance is multiple of 5
            context = load_json(context_path)
            instance = context.get("instance", 0)

            if display and instance % 5 == 0:
                print("\n")
                monitor.display_dashboard()

            return metrics

        except Exception as e:
            self.log(f"Health check failed: {e}", "ERROR")
            return None

    def decide_mode(self):
        """Decide whether to use simple or mesh mode."""
        # Check if there's a queued task
        tasks_file = CONTEXT_DIR / "queued_task.json"
        if tasks_file.exists():
            task = load_json(tasks_file)
            task_type = task.get("type", "")
            mesh_types = self.config["mode"]["use_mesh_for"]

            if task_type in mesh_types:
                self.log(f"Task type '{task_type}' -> mesh mode")
                # Remove queued task
                tasks_file.unlink()
                return "mesh", task

        return self.config["mode"]["default"], None

    def run(self):
        """Main entry point."""
        self.log("=" * 50)
        self.log("Heartbeat Runner starting")
        self.log("=" * 50)

        # Daily backup
        self.backup_context()

        # Check rate limit
        if self.is_rate_limited():
            self.add_history("skipped", {"reason": "rate_limited"})
            self.save_log()
            # Calculate adaptive interval for next run
            next_interval = self.calculate_adaptive_interval()
            self.log(f"Next heartbeat in {next_interval} minutes (adaptive)")
            return False

        # Update status
        self.update_status(
            last_heartbeat=get_timestamp(),
            state="running"
        )

        # Decide mode
        mode, task = self.decide_mode()
        self.log(f"Mode: {mode}")

        # Run with retry
        success, output, error_type = self.run_with_retry(mode, task)

        # Update status
        self.status["total_heartbeats"] += 1

        # Handle no credits specially - don't count as failure
        if not success and error_type == "no_credits":
            self.log("Skipping heartbeat - no API credits available", "WARN")
            self.add_history("skipped", {"reason": "no_credits"})
            self.save_log()
            # Don't increment failures or change intervals for this
            return False

        # Track cost (estimate 5000 tokens per heartbeat average)
        estimated_tokens = 5000
        budget_ok = self.track_cost(estimated_tokens)

        if success:
            self.update_status(
                last_success=get_timestamp(),
                consecutive_failures=0,
                state="ready"
            )
            self.add_history("success", {"mode": mode})
        else:
            self.status["total_failures"] += 1
            self.status["consecutive_failures"] += 1
            self.update_status(
                last_failure=get_timestamp(),
                state="failed"
            )
            self.add_history("failure", {"mode": mode, "error": error_type, "output_snippet": output[:500] if output else None})

        # Calculate adaptive interval for next run
        next_interval = self.calculate_adaptive_interval()
        self.log(f"Next heartbeat recommended in {next_interval} minutes")
        self.update_status(recommended_interval_minutes=next_interval)

        # Check budget
        if not budget_ok:
            self.log("Daily budget reached - skipping future heartbeats today", "WARN")
            self.update_status(budget_reached=True)

        # Save log
        log_path = self.save_log()

        # Also append to heartbeat_log.md in mine
        self.append_to_heartbeat_log(success, mode, log_path, output)

        # Check and display health (every 5 instances)
        self.check_health(display=True)

        return success

    def append_to_heartbeat_log(self, success, mode, log_path, output=None):
        """Append entry to the main heartbeat log."""
        heartbeat_log = Path(self.config["paths"]["mine"]) / "heartbeat_log.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        status_emoji = "ok" if success else "FAILED"

        entry = f"\n---\n\n## {timestamp} [{status_emoji}]\n- Mode: {mode}\n- Log: {log_path}\n"

        if output and success:
            # Include a snippet of Claude's output
            output_snippet = output[:2000] if len(output) > 2000 else output
            entry += f"\n### Output\n```\n{output_snippet}\n```\n"

        if heartbeat_log.exists():
            content = load_file(heartbeat_log)
            # Remove the "waiting for first heartbeat" placeholder if present
            content = content.replace("*Waiting for first heartbeat...*", "")
            content += entry
        else:
            content = "# Heartbeat Log\n" + entry

        save_file(heartbeat_log, content)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Heartbeat Runner")
    parser.add_argument("--mode", choices=["simple", "api", "mesh", "auto"], default="auto",
                        help="Force a specific mode (api uses prompt caching)")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument("--reset-rate-limit", action="store_true", help="Clear rate limit cooldown")
    args = parser.parse_args()

    runner = HeartbeatRunner()

    if args.status:
        print(json.dumps(runner.status, indent=2))
        return

    if args.reset_rate_limit:
        runner.update_status(rate_limited_until=None)
        print("Rate limit cooldown cleared")
        return

    if args.mode != "auto":
        runner.config["mode"]["default"] = args.mode

    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
