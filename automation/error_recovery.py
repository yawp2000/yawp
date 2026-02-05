"""
Error Recovery System
Handles failures gracefully and attempts recovery
"""

import json
from pathlib import Path
from datetime import datetime

class ErrorRecovery:
    def __init__(self, context_path, status_path):
        self.context_path = Path(context_path)
        self.status_path = Path(status_path)

    def check_health(self):
        """Check system health and attempt recovery if needed"""
        issues = []

        # Check 1: Context file integrity
        try:
            with open(self.context_path) as f:
                context = json.load(f)
            print("[OK] Context file valid")
        except json.JSONDecodeError as e:
            issues.append({
                "severity": "CRITICAL",
                "issue": "Context file corrupted",
                "error": str(e),
                "recovery": "restore_from_backup"
            })
        except FileNotFoundError:
            issues.append({
                "severity": "CRITICAL",
                "issue": "Context file missing",
                "recovery": "restore_from_backup"
            })

        # Check 2: Status file integrity
        try:
            with open(self.status_path) as f:
                status = json.load(f)
            print("[OK] Status file valid")

            # Check for persistent failures
            if status.get("consecutive_failures", 0) >= 5:
                issues.append({
                    "severity": "HIGH",
                    "issue": f"{status['consecutive_failures']} consecutive failures",
                    "recovery": "increase_backoff"
                })

        except (json.JSONDecodeError, FileNotFoundError) as e:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Status file invalid",
                "error": str(e),
                "recovery": "rebuild_status"
            })

        # Check 3: Backup availability
        backups_dir = self.context_path.parent / "backups"
        if backups_dir.exists():
            backups = list(backups_dir.glob("context_*.json"))
            print(f"[OK] {len(backups)} backups available")

            if len(backups) == 0:
                issues.append({
                    "severity": "MEDIUM",
                    "issue": "No backups found",
                    "recovery": "create_backup_now"
                })
        else:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Backup directory missing",
                "recovery": "create_backup_dir"
            })

        return issues

    def attempt_recovery(self, issue):
        """Attempt to recover from issue"""
        recovery_action = issue["recovery"]

        if recovery_action == "restore_from_backup":
            return self.restore_from_backup()

        elif recovery_action == "rebuild_status":
            return self.rebuild_status()

        elif recovery_action == "increase_backoff":
            return self.increase_backoff()

        elif recovery_action == "create_backup_now":
            return self.create_backup()

        elif recovery_action == "create_backup_dir":
            return self.create_backup_dir()

        return False

    def restore_from_backup(self):
        """Restore context from most recent backup"""
        backups_dir = self.context_path.parent / "backups"

        if not backups_dir.exists():
            print("[FAIL] No backup directory")
            return False

        backups = sorted(backups_dir.glob("context_*.json"), reverse=True)

        if not backups:
            print("[FAIL] No backups found")
            return False

        latest_backup = backups[0]
        print(f"Restoring from: {latest_backup.name}")

        # Verify backup is valid
        try:
            with open(latest_backup) as f:
                backup_data = json.load(f)

            # Copy backup to context
            with open(self.context_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            print("[OK] Restored from backup")
            return True

        except Exception as e:
            print(f"[FAIL] Failed to restore: {e}")
            return False

    def rebuild_status(self):
        """Rebuild status file from scratch"""
        default_status = {
            "last_heartbeat": datetime.now().isoformat(),
            "last_success": None,
            "last_failure": None,
            "consecutive_failures": 0,
            "total_heartbeats": 0,
            "total_failures": 0,
            "rate_limited_until": None,
            "state": "ready",
            "history": [],
            "costs": {
                "total_spend": 0.0,
                "daily_budget": 5.00,
                "today_spend": 0.0,
                "last_reset": datetime.now().strftime("%Y-%m-%d")
            }
        }

        with open(self.status_path, 'w') as f:
            json.dump(default_status, f, indent=2)

        print("[OK] Status file rebuilt")
        return True

    def increase_backoff(self):
        """Increase backoff time"""
        try:
            with open(self.status_path) as f:
                status = json.load(f)

            # Set long cooldown
            status["rate_limited_until"] = (
                datetime.now() + timedelta(hours=4)
            ).isoformat()

            with open(self.status_path, 'w') as f:
                json.dump(status, f, indent=2)

            print("[OK] Increased backoff to 4 hours")
            return True

        except Exception as e:
            print(f"[FAIL] Failed to increase backoff: {e}")
            return False

    def create_backup(self):
        """Create backup immediately"""
        import shutil

        backups_dir = self.context_path.parent / "backups"
        backups_dir.mkdir(exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = backups_dir / f"context_{today}.json"

        shutil.copy(self.context_path, backup_path)
        print(f"[OK] Backup created: {backup_path.name}")
        return True

    def create_backup_dir(self):
        """Create backup directory"""
        backups_dir = self.context_path.parent / "backups"
        backups_dir.mkdir(exist_ok=True)
        print("[OK] Backup directory created")
        return True


def main():
    import sys

    context_path = "~/Desktop/ClaudeContext/context.json"
    status_path = "~/Desktop/ClaudeContext/automation/status.json"

    recovery = ErrorRecovery(context_path, status_path)

    print("\\n" + "=" * 60)
    print("SYSTEM HEALTH CHECK")
    print("=" * 60 + "\\n")

    issues = recovery.check_health()

    if not issues:
        print("\\n[OK] All systems healthy\\n")
        return 0

    print(f"\\n[WARN]  {len(issues)} issue(s) found\\n")

    for issue in issues:
        print(f"[{issue['severity']}] {issue['issue']}")

        if "--auto-recover" in sys.argv:
            print(f"  Attempting recovery: {issue['recovery']}")
            success = recovery.attempt_recovery(issue)
            if success:
                print("  [OK] Recovered")
            else:
                print("  [FAIL] Recovery failed")
        else:
            print(f"  Recovery available: {issue['recovery']}")
            print("  (Run with --auto-recover to attempt)")

        print()

    return 1 if issues else 0


if __name__ == "__main__":
    exit(main())
