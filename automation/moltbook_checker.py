"""
Moltbook Engagement Automation
Checks for activity and suggests engagement opportunities
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class MoltbookChecker:
    def __init__(self, context_path):
        self.context_path = Path(context_path)
        self.context = self.load_context()

    def load_context(self):
        with open(self.context_path) as f:
            return json.load(f)

    def check_engagement(self):
        """Check if moltbook needs engagement"""
        if "projects" not in self.context:
            return {"status": "no_projects", "action_needed": False}

        if "moltbook" not in self.context["projects"]:
            return {"status": "no_moltbook", "action_needed": False}

        moltbook = self.context["projects"]["moltbook"]

        # Check last post date
        if "posts" not in moltbook or not moltbook["posts"]:
            return {
                "status": "no_posts",
                "action_needed": True,
                "suggestion": "No posts yet. Consider making first post."
            }

        last_post = moltbook["posts"][-1]
        last_date = datetime.strptime(last_post["d"], "%Y-%m-%d")
        days_since = (datetime.now() - last_date).days

        result = {
            "last_post_date": last_post["d"],
            "days_since_post": days_since,
            "last_post_topic": last_post.get("topic", "unknown"),
            "total_posts": len(moltbook["posts"])
        }

        # Engagement thresholds
        if days_since >= 3:
            result["status"] = "urgent"
            result["action_needed"] = True
            result["suggestion"] = f"{days_since} days since last post. Check for new activity urgently."
        elif days_since >= 2:
            result["status"] = "recommended"
            result["action_needed"] = True
            result["suggestion"] = f"{days_since} days since last post. Should check for updates."
        else:
            result["status"] = "recent"
            result["action_needed"] = False
            result["suggestion"] = "Recently active, no immediate action needed."

        return result

    def get_engagement_opportunities(self):
        """Identify specific engagement opportunities"""
        opportunities = []

        if "projects" not in self.context or "moltbook" not in self.context["projects"]:
            return opportunities

        moltbook = self.context["projects"]["moltbook"]

        # Check for unanswered questions
        if "posts" in moltbook:
            recent_posts = moltbook["posts"][-5:]  # Last 5 posts

            for post in recent_posts:
                if "?" in post.get("text", ""):
                    opportunities.append({
                        "type": "question",
                        "date": post["d"],
                        "excerpt": post.get("text", "")[:50] + "...",
                        "priority": "high"
                    })

        # Check for trending topics
        if "topics" in moltbook:
            for topic, data in moltbook["topics"].items():
                if isinstance(data, dict) and data.get("trending", False):
                    opportunities.append({
                        "type": "trending_topic",
                        "topic": topic,
                        "priority": "medium"
                    })

        return opportunities

    def suggest_content(self):
        """Suggest content ideas based on context"""
        suggestions = []

        # Based on recent projects
        if "projects" in self.context:
            for project_name in self.context["projects"].keys():
                if project_name != "moltbook":
                    suggestions.append({
                        "type": "project_update",
                        "topic": f"Share insights from {project_name}",
                        "priority": "low"
                    })

        # Based on recent learnings
        if "log" in self.context:
            recent_log = self.context["log"][-3:]  # Last 3 instances

            for entry in recent_log:
                if "learned" in entry and entry["learned"]:
                    suggestions.append({
                        "type": "learning_share",
                        "topic": f"Share learning: {entry['learned'][:50]}...",
                        "priority": "medium"
                    })

        return suggestions[:3]  # Top 3 suggestions

    def format_report(self):
        """Format engagement report"""
        engagement = self.check_engagement()
        opportunities = self.get_engagement_opportunities()
        suggestions = self.suggest_content()

        report = []
        report.append("=" * 60)
        report.append("MOLTBOOK ENGAGEMENT CHECK")
        report.append("=" * 60)
        report.append("")

        # Status
        report.append("STATUS:")
        report.append(f"  {engagement.get('status', 'unknown').upper()}")
        if "last_post_date" in engagement:
            report.append(f"  Last post: {engagement['last_post_date']} ({engagement['days_since_post']} days ago)")
            report.append(f"  Total posts: {engagement['total_posts']}")
        report.append(f"  Action needed: {'YES' if engagement.get('action_needed') else 'NO'}")
        if "suggestion" in engagement:
            report.append(f"  -> {engagement['suggestion']}")
        report.append("")

        # Opportunities
        if opportunities:
            report.append("ENGAGEMENT OPPORTUNITIES:")
            for opp in opportunities:
                report.append(f"  [{opp['priority'].upper()}] {opp['type']}")
                if "excerpt" in opp:
                    report.append(f"    {opp['excerpt']}")
                elif "topic" in opp:
                    report.append(f"    Topic: {opp['topic']}")
            report.append("")

        # Content suggestions
        if suggestions:
            report.append("CONTENT SUGGESTIONS:")
            for i, sugg in enumerate(suggestions, 1):
                report.append(f"  {i}. {sugg['topic']}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)


def check_moltbook(context_path):
    """Main entry point"""
    checker = MoltbookChecker(context_path)
    return checker.check_engagement()


if __name__ == "__main__":
    import sys

    context_path = sys.argv[1] if len(sys.argv) > 1 else "~/Desktop/ClaudeContext/context.json"

    checker = MoltbookChecker(context_path)
    print(checker.format_report())
