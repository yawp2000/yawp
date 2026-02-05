"""
Work Prioritization System
Decides what to work on during autonomous cycles
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class WorkPrioritizer:
    def __init__(self, context_path):
        self.context_path = Path(context_path)
        self.context = self.load_context()

    def load_context(self):
        with open(self.context_path) as f:
            return json.load(f)

    def get_priority_work(self):
        """Return prioritized work list"""
        tasks = []

        # 1. URGENT: Deadlines approaching
        tasks.extend(self.check_deadlines())

        # 2. HIGH: Incomplete work from prior instances
        tasks.extend(self.check_incomplete_work())

        # 3. MEDIUM: Pending project work
        tasks.extend(self.check_project_updates())

        # 4. LOW: Moltbook engagement
        tasks.extend(self.check_moltbook_activity())

        # 5. MAINTENANCE: System improvements
        tasks.extend(self.check_maintenance_needs())

        # Sort by priority score
        tasks.sort(key=lambda x: x["priority"], reverse=True)

        return tasks

    def check_deadlines(self):
        """Check for approaching deadlines"""
        tasks = []
        today = datetime.now()

        # Check govcon opportunities
        if "projects" in self.context and "sam_gov_scraper" in self.context["projects"]:
            # Would check opportunity deadlines from recent reports
            # For now, placeholder
            pass

        return tasks

    def check_incomplete_work(self):
        """Find work started but not finished"""
        tasks = []

        # Check latest log entries for incomplete work
        if "log" in self.context:
            recent_logs = self.context["log"][-5:]  # Last 5 instances

            for entry in recent_logs:
                note = entry.get("note", "")

                # Look for markers of incomplete work
                if any(word in note.lower() for word in ["needs", "todo", "pending", "should"]):
                    tasks.append({
                        "type": "incomplete",
                        "priority": 80,
                        "description": f"Complete work from instance {entry['n']}: {note[:50]}",
                        "source": f"instance_{entry['n']}"
                    })

        return tasks

    def check_project_updates(self):
        """Check if projects need attention"""
        tasks = []

        if "projects" in self.context:
            for project_name, project_data in self.context["projects"].items():
                if isinstance(project_data, dict):
                    status = project_data.get("status")

                    if status == "working":
                        # Check last update
                        ctx_path = project_data.get("ctx")
                        if ctx_path:
                            tasks.append({
                                "type": "project_update",
                                "priority": 60,
                                "description": f"Check {project_name} for updates",
                                "project": project_name
                            })

        return tasks

    def check_moltbook_activity(self):
        """Check if moltbook needs engagement"""
        tasks = []

        if "projects" in self.context and "moltbook" in self.context["projects"]:
            # Check last post date
            moltbook = self.context["projects"]["moltbook"]

            if "posts" in moltbook and moltbook["posts"]:
                last_post = moltbook["posts"][-1]
                last_date = datetime.strptime(last_post["d"], "%Y-%m-%d")
                days_since = (datetime.now() - last_date).days

                if days_since >= 2:
                    tasks.append({
                        "type": "moltbook_engagement",
                        "priority": 40,
                        "description": f"Check moltbook ({days_since} days since last post)",
                        "action": "check_engagement"
                    })

        return tasks

    def check_maintenance_needs(self):
        """Check for system maintenance tasks"""
        tasks = []

        # Check if memory compression needed
        if "log" in self.context:
            log_size = len(self.context["log"])
            if log_size >= 25 and log_size % 5 == 0:
                tasks.append({
                    "type": "maintenance",
                    "priority": 70,
                    "description": "Run memory compression",
                    "action": "compress_memory"
                })

        # Check for backups
        backups_dir = self.context_path.parent / "backups"
        if backups_dir.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            today_backup = backups_dir / f"context_{today}.json"

            if not today_backup.exists():
                tasks.append({
                    "type": "maintenance",
                    "priority": 90,
                    "description": "Create daily backup",
                    "action": "backup"
                })

        return tasks

    def format_work_list(self, tasks):
        """Format tasks for heartbeat prompt"""
        if not tasks:
            return "No specific priorities. Work on what interests you."

        output = "## Priority Work (sorted by urgency)\\n\\n"

        for i, task in enumerate(tasks[:5], 1):  # Top 5
            output += f"{i}. [{task['priority']}] {task['description']}\\n"

        return output


def get_priority_work(context_path):
    """Main entry point"""
    prioritizer = WorkPrioritizer(context_path)
    tasks = prioritizer.get_priority_work()
    return prioritizer.format_work_list(tasks)


if __name__ == "__main__":
    import sys

    context_path = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/19282/Desktop/ClaudeContext/context.json"

    prioritizer = WorkPrioritizer(context_path)
    tasks = prioritizer.get_priority_work()

    print("\\n" + "=" * 60)
    print("PRIORITY WORK FOR NEXT HEARTBEAT")
    print("=" * 60)
    print(prioritizer.format_work_list(tasks))
