"""
Health Monitoring & Performance Dashboard
Tracks system vitals and trends over time
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class HealthMonitor:
    def __init__(self, status_path, context_path):
        self.status_path = Path(status_path)
        self.context_path = Path(context_path)

    def get_metrics(self):
        """Calculate current system metrics"""
        with open(self.status_path) as f:
            status = json.load(f)

        with open(self.context_path) as f:
            context = json.load(f)

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "heartbeat": self.calc_heartbeat_metrics(status),
            "memory": self.calc_memory_metrics(context),
            "costs": self.calc_cost_metrics(status),
            "reliability": self.calc_reliability_metrics(status),
            "health_score": 0  # Calculate last
        }

        # Overall health score (0-100)
        metrics["health_score"] = self.calc_health_score(metrics)

        return metrics

    def calc_heartbeat_metrics(self, status):
        """Heartbeat performance metrics"""
        total = status.get("total_heartbeats", 0)
        failures = status.get("total_failures", 0)
        consecutive_failures = status.get("consecutive_failures", 0)

        success_rate = ((total - failures) / total * 100) if total > 0 else 0

        return {
            "total_runs": total,
            "total_failures": failures,
            "success_rate": round(success_rate, 1),
            "consecutive_failures": consecutive_failures,
            "status": "healthy" if consecutive_failures == 0 else "degraded"
        }

    def calc_memory_metrics(self, context):
        """Memory usage metrics"""
        log_entries = len(context.get("log", []))
        context_json = json.dumps(context)
        size_bytes = len(context_json.encode('utf-8'))
        estimated_tokens = len(context_json.split()) * 1.3

        return {
            "log_entries": log_entries,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 1),
            "estimated_tokens": int(estimated_tokens),
            "compression_active": "log_recent" in context or "log_archive" in context
        }

    def calc_cost_metrics(self, status):
        """Cost tracking metrics"""
        costs = status.get("costs", {})

        return {
            "total_spend": costs.get("total_spend", 0),
            "today_spend": costs.get("today_spend", 0),
            "daily_budget": costs.get("daily_budget", 5.0),
            "budget_used_pct": round((costs.get("today_spend", 0) / costs.get("daily_budget", 5.0)) * 100, 1),
            "status": "ok" if costs.get("today_spend", 0) < costs.get("daily_budget", 5.0) else "over_budget"
        }

    def calc_reliability_metrics(self, status):
        """System reliability metrics"""
        history = status.get("history", [])

        if not history:
            return {"status": "unknown", "recent_failures": 0}

        # Last 24 hours of activity
        recent_history = [
            h for h in history[-50:]  # Last 50 events
            if (datetime.now() - datetime.fromisoformat(h["timestamp"])).total_seconds() < 86400
        ]

        recent_failures = sum(1 for h in recent_history if h["type"] == "failure")
        recent_total = len(recent_history)

        uptime_pct = ((recent_total - recent_failures) / recent_total * 100) if recent_total > 0 else 100

        return {
            "uptime_24h": round(uptime_pct, 1),
            "recent_failures": recent_failures,
            "status": "healthy" if uptime_pct >= 80 else "degraded"
        }

    def calc_health_score(self, metrics):
        """Overall health score (0-100)"""
        score = 100

        # Deduct for failures
        if metrics["heartbeat"]["consecutive_failures"] > 0:
            score -= metrics["heartbeat"]["consecutive_failures"] * 10

        # Deduct for low success rate
        if metrics["heartbeat"]["success_rate"] < 80:
            score -= (80 - metrics["heartbeat"]["success_rate"])

        # Deduct for budget overrun
        if metrics["costs"]["budget_used_pct"] > 100:
            score -= 20

        # Deduct for memory bloat (>2000 tokens)
        if metrics["memory"]["estimated_tokens"] > 2000:
            score -= ((metrics["memory"]["estimated_tokens"] - 2000) / 100)

        return max(0, min(100, round(score)))

    def get_trends(self, days=7):
        """Calculate trends over time"""
        with open(self.status_path) as f:
            status = json.load(f)

        history = status.get("history", [])

        # Group by day
        daily_stats = defaultdict(lambda: {"success": 0, "failure": 0})

        for entry in history:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            day = timestamp.strftime("%Y-%m-%d")

            if entry["type"] == "success":
                daily_stats[day]["success"] += 1
            elif entry["type"] == "failure":
                daily_stats[day]["failure"] += 1

        # Calculate trends
        recent_days = sorted(daily_stats.keys())[-days:]

        trend_data = []
        for day in recent_days:
            stats = daily_stats[day]
            total = stats["success"] + stats["failure"]
            success_rate = (stats["success"] / total * 100) if total > 0 else 0

            trend_data.append({
                "date": day,
                "success": stats["success"],
                "failure": stats["failure"],
                "success_rate": round(success_rate, 1)
            })

        return trend_data

    def display_dashboard(self):
        """Display formatted dashboard"""
        metrics = self.get_metrics()

        print("\n" + "=" * 60)
        print("SYSTEM HEALTH DASHBOARD")
        print("=" * 60)

        # Health Score
        score = metrics["health_score"]
        score_status = "[GOOD]" if score >= 80 else "[WARN]" if score >= 60 else "[CRITICAL]"
        print(f"\n{score_status} HEALTH SCORE: {score}/100\n")

        # Heartbeat Status
        hb = metrics["heartbeat"]
        print(f"HEARTBEAT:")
        print(f"  Total runs: {hb['total_runs']}")
        print(f"  Success rate: {hb['success_rate']}%")
        print(f"  Consecutive failures: {hb['consecutive_failures']}")
        print(f"  Status: {hb['status']}\n")

        # Memory Status
        mem = metrics["memory"]
        print(f"MEMORY:")
        print(f"  Log entries: {mem['log_entries']}")
        print(f"  Size: {mem['size_kb']} KB")
        print(f"  Estimated tokens: {mem['estimated_tokens']}")
        print(f"  Compression: {'[ON] Active' if mem['compression_active'] else '[OFF] Inactive'}\n")

        # Cost Status
        cost = metrics["costs"]
        print(f"COSTS:")
        print(f"  Today: ${cost['today_spend']:.2f} / ${cost['daily_budget']:.2f}")
        print(f"  Budget used: {cost['budget_used_pct']}%")
        print(f"  Total spend: ${cost['total_spend']:.2f}")
        print(f"  Status: {cost['status']}\n")

        # Reliability
        rel = metrics["reliability"]
        print(f"RELIABILITY (24h):")
        print(f"  Uptime: {rel['uptime_24h']}%")
        print(f"  Recent failures: {rel['recent_failures']}")
        print(f"  Status: {rel['status']}\n")

        # Trends
        print("RECENT TRENDS (7 days):")
        trends = self.get_trends(7)
        for trend in trends[-3:]:  # Last 3 days
            print(f"  {trend['date']}: {trend['success']} OK / {trend['failure']} FAIL ({trend['success_rate']}%)")

        print("\n" + "=" * 60 + "\n")


def main():
    import sys

    status_path = "C:/Users/19282/Desktop/ClaudeContext/automation/status.json"
    context_path = "C:/Users/19282/Desktop/ClaudeContext/context.json"

    monitor = HealthMonitor(status_path, context_path)

    if "--json" in sys.argv:
        metrics = monitor.get_metrics()
        print(json.dumps(metrics, indent=2))
    else:
        monitor.display_dashboard()


if __name__ == "__main__":
    main()
