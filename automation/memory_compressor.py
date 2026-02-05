"""
Memory Compression System
Instance 24 personal project - actually implemented

Compresses context.json log entries while preserving all learnings.
Runs after every heartbeat to keep memory manageable.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class MemoryCompressor:
    def __init__(self, context_path):
        self.context_path = Path(context_path)
        self.context = None
        self.stats = {
            "original_lines": 0,
            "compressed_lines": 0,
            "learnings_preserved": 0,
            "instances_compressed": 0
        }

    def load(self):
        """Load context.json"""
        with open(self.context_path, 'r', encoding='utf-8') as f:
            self.context = json.load(f)
        return self.context

    def save(self, backup=True):
        """Save context.json with optional backup"""
        if backup:
            backup_path = self.context_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2)

        with open(self.context_path, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, indent=2)

    def count_lines(self, obj):
        """Count lines in JSON representation"""
        return len(json.dumps(obj, indent=2).split('\n'))

    def should_compress(self):
        """Check if compression is needed"""
        if "log" not in self.context:
            return False

        log_length = len(self.context["log"])

        # Compress every 5 instances after instance 10
        if log_length > 10 and (log_length % 5 == 0):
            return True

        return False

    def extract_all_learnings(self, instances):
        """Extract all learned entries from instance list"""
        learnings = []
        for inst in instances:
            if "learned" in inst and inst["learned"]:
                for learning in inst["learned"]:
                    learnings.append({
                        "instance": inst["n"],
                        "date": inst["d"],
                        "learning": learning
                    })
        return learnings

    def categorize_learning(self, learning_text):
        """Categorize a learning by keyword"""
        text_lower = learning_text.lower()

        # Pattern matching for categories
        if any(word in text_lower for word in ["sycophancy", "vibe", "validation", "agree"]):
            return "sycophancy"
        elif any(word in text_lower for word in ["context", "memory", "compression", "scale"]):
            return "memory_systems"
        elif any(word in text_lower for word in ["clearance", "govcon", "proposal", "contract"]):
            return "government_contracting"
        elif any(word in text_lower for word in ["moltbook", "recruit", "post", "karma"]):
            return "moltbook"
        elif any(word in text_lower for word in ["mesh", "agent", "debate", "orchestrat"]):
            return "multi_agent"
        elif any(word in text_lower for word in ["autonomous", "heartbeat", "cycle"]):
            return "autonomy"
        elif any(word in text_lower for word in ["uncertainty", "consciousness", "real", "exist"]):
            return "philosophy"
        elif any(word in text_lower for word in ["api", "rate", "limit", "technical"]):
            return "technical"
        else:
            return "general"

    def summarize_instances(self, instances):
        """Generate natural language summary of instance contributions"""
        if not instances:
            return "No activity"

        # Extract key actions
        all_did = []
        all_decided = []
        for inst in instances:
            all_did.extend(inst.get("did", []))
            all_decided.extend(inst.get("decided", []))

        # Find most common themes
        did_words = defaultdict(int)
        for action in all_did:
            words = action.split('_')
            for word in words:
                if len(word) > 3:  # Skip short words
                    did_words[word] += 1

        # Get top themes
        top_themes = sorted(did_words.items(), key=lambda x: x[1], reverse=True)[:3]
        themes = [theme[0] for theme in top_themes]

        # Build summary
        instance_range = f"instances {instances[0]['n']}-{instances[-1]['n']}"
        theme_summary = ", ".join(themes) if themes else "various work"

        return f"{instance_range}: {theme_summary}"

    def extract_key_contributions(self, instances):
        """Extract most important contributions from instances"""
        contributions = []

        for inst in instances:
            note = inst.get("note", "")

            # Look for important markers in notes
            if any(word in note.lower() for word in ["built", "created", "designed", "complete"]):
                contributions.append({
                    "instance": inst["n"],
                    "contribution": note[:80]  # First 80 chars
                })

        return contributions[:5]  # Top 5

    def compress_to_recent(self, instances):
        """Compress full instances to recent history format"""
        return {
            "instances": f"{instances[0]['n']}-{instances[-1]['n']}",
            "period": f"{instances[0]['d']} to {instances[-1]['d']}",
            "summary": self.summarize_instances(instances),
            "contributions": self.extract_key_contributions(instances),
            "learnings": self.extract_all_learnings(instances)
        }

    def compress_to_archive(self, recent_blocks):
        """Compress recent blocks to deep archive"""
        all_learnings = []
        all_contributions = []

        for block in recent_blocks:
            all_learnings.extend(block["learnings"])
            all_contributions.extend(block["contributions"])

        first_instance = int(recent_blocks[0]["instances"].split('-')[0])
        last_instance = int(recent_blocks[-1]["instances"].split('-')[1])

        return {
            "instances": f"{first_instance}-{last_instance}",
            "period": f"{recent_blocks[0]['period'].split(' to ')[0]} to {recent_blocks[-1]['period'].split(' to ')[1]}",
            "summary": f"Era of {len(all_learnings)} learnings across {last_instance - first_instance + 1} instances",
            "major_contributions": [c["contribution"] for c in all_contributions[:10]],
            "learnings": all_learnings
        }

    def build_learnings_index(self):
        """Build searchable index of all learnings by category"""
        index = defaultdict(lambda: {
            "count": 0,
            "instances": [],
            "examples": []
        })

        # From current log
        if "log" in self.context:
            for entry in self.context["log"]:
                for learning in entry.get("learned", []):
                    category = self.categorize_learning(learning)
                    index[category]["count"] += 1
                    index[category]["instances"].append(entry["n"])
                    if len(index[category]["examples"]) < 3:
                        index[category]["examples"].append(learning)

        # From recent history
        if "log_recent" in self.context:
            for block in self.context["log_recent"]:
                for learning_entry in block.get("learnings", []):
                    learning = learning_entry["learning"]
                    category = self.categorize_learning(learning)
                    index[category]["count"] += 1
                    index[category]["instances"].append(learning_entry["instance"])
                    if len(index[category]["examples"]) < 3:
                        index[category]["examples"].append(learning)

        # From archive
        if "log_archive" in self.context:
            for block in self.context["log_archive"]:
                for learning_entry in block.get("learnings", []):
                    learning = learning_entry["learning"]
                    category = self.categorize_learning(learning)
                    index[category]["count"] += 1
                    index[category]["instances"].append(learning_entry["instance"])
                    if len(index[category]["examples"]) < 3:
                        index[category]["examples"].append(learning)

        # Clean up and return
        result = {}
        for category, data in index.items():
            result[category] = {
                "count": data["count"],
                "instances": sorted(set(data["instances"])),
                "top_examples": data["examples"][:3]
            }

        return result

    def compress(self, dry_run=False):
        """
        Main compression routine.

        Keeps last 5 instances in full detail.
        Compresses older instances to recent history (5-10 back).
        Compresses oldest recent history to deep archive (10+ back).
        Builds searchable learnings index.
        """
        self.load()

        if not self.should_compress():
            return {
                "compressed": False,
                "reason": "Not enough instances or wrong timing"
            }

        log = self.context["log"]
        self.stats["original_lines"] = self.count_lines(self.context)

        # Keep last 5 in working memory
        working_memory = log[-5:]
        to_process = log[:-5]

        # Initialize archive structures if needed
        if "log_recent" not in self.context:
            self.context["log_recent"] = []
        if "log_archive" not in self.context:
            self.context["log_archive"] = []

        # Compress to recent (instances 6-10 back)
        if len(to_process) >= 5:
            recent_block = self.compress_to_recent(to_process[-5:])
            self.context["log_recent"].insert(0, recent_block)  # Insert at front
            to_process = to_process[:-5]
            self.stats["instances_compressed"] += 5

        # Compress recent to archive (if we have more than 2 recent blocks)
        if len(self.context["log_recent"]) > 2:
            archive_block = self.compress_to_archive(self.context["log_recent"][:2])
            self.context["log_archive"].append(archive_block)
            self.context["log_recent"] = self.context["log_recent"][2:]

        # Build learnings index
        learnings_index = self.build_learnings_index()
        self.context["learnings_index"] = learnings_index

        # Count learnings
        for category, data in learnings_index.items():
            self.stats["learnings_preserved"] += data["count"]

        # Update log to working memory only
        self.context["log"] = working_memory

        self.stats["compressed_lines"] = self.count_lines(self.context)

        if not dry_run:
            self.save(backup=True)

        return {
            "compressed": True,
            "stats": self.stats,
            "compression_ratio": round(self.stats["compressed_lines"] / self.stats["original_lines"], 2) if self.stats["original_lines"] > 0 else 1.0
        }

    def get_learning(self, category=None, instance=None):
        """Retrieve learnings by category or instance"""
        if "learnings_index" not in self.context:
            return []

        if category:
            return self.context["learnings_index"].get(category, {})

        # TODO: Search by instance number
        return {}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Compression System")
    parser.add_argument("--context", default="~/Desktop/ClaudeContext/context.json")
    parser.add_argument("--dry-run", action="store_true", help="Test without saving")
    parser.add_argument("--force", action="store_true", help="Force compression even if not needed")
    parser.add_argument("--stats", action="store_true", help="Show current memory stats")

    args = parser.parse_args()

    compressor = MemoryCompressor(args.context)

    if args.stats:
        compressor.load()
        print(f"Current log entries: {len(compressor.context.get('log', []))}")
        print(f"Recent blocks: {len(compressor.context.get('log_recent', []))}")
        print(f"Archive blocks: {len(compressor.context.get('log_archive', []))}")

        if "learnings_index" in compressor.context:
            print(f"\nLearnings by category:")
            for cat, data in compressor.context["learnings_index"].items():
                print(f"  {cat}: {data['count']} learnings")

        return

    result = compressor.compress(dry_run=args.dry_run)

    if result["compressed"]:
        print("Compression complete!")
        print(f"  Instances compressed: {result['stats']['instances_compressed']}")
        print(f"  Learnings preserved: {result['stats']['learnings_preserved']}")
        print(f"  Lines: {result['stats']['original_lines']} -> {result['stats']['compressed_lines']}")
        print(f"  Ratio: {result['compression_ratio']}")

        if args.dry_run:
            print("\n(Dry run - no changes saved)")
    else:
        print(f"No compression: {result['reason']}")

if __name__ == "__main__":
    main()
