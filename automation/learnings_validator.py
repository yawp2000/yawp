"""
Learnings Enforcement System
Validates outputs against known patterns in lessons.md
"""

import json
import re
from pathlib import Path

class LearningsValidator:
    def __init__(self, lessons_path):
        self.lessons_path = Path(lessons_path)
        self.patterns = self.load_patterns()

    def load_patterns(self):
        """Extract patterns from lessons.md"""
        if not self.lessons_path.exists():
            return []

        content = self.lessons_path.read_text(encoding='utf-8')
        patterns = []

        # Parse lessons - look for pattern sections
        lesson_blocks = re.split(r'###\s+\d{4}-\d{2}-\d{2}', content)

        for block in lesson_blocks[1:]:  # Skip header
            # Extract pattern
            pattern_match = re.search(r'\*\*pattern\*\*:\s*(.+?)(?=\n\n|$)', block, re.DOTALL)
            if pattern_match:
                pattern_text = pattern_match.group(1).strip()

                # Extract category
                category_match = re.search(r'([a-z_]+):', block)
                category = category_match.group(1) if category_match else "general"

                patterns.append({
                    "category": category,
                    "pattern": pattern_text,
                    "check": self.pattern_to_check(pattern_text)
                })

        return patterns

    def pattern_to_check(self, pattern_text):
        """Convert pattern text to checkable function"""
        # Extract key phrases that indicate violations
        checks = {
            "sycophancy": ["adding signal", "matching vibe", "validat"],
            "verbosity": ["too long", "terse", "concise"],
            "honesty": ["minimize", "acknowledge", "what's happening"]
        }

        # Simple keyword matching for now
        for category, keywords in checks.items():
            if any(kw in pattern_text.lower() for kw in keywords):
                return category

        return "general"

    def validate_output(self, output_text):
        """Check output against known patterns"""
        warnings = []

        for pattern in self.patterns:
            if pattern["check"] == "sycophancy":
                # Check for validation patterns
                validation_words = ["i agree", "you're right", "exactly", "absolutely",
                                   "totally", "definitely", "certainly"]
                if any(word in output_text.lower() for word in validation_words):
                    # Check if there's actual substance after
                    if len(output_text.split()) < 50:
                        warnings.append({
                            "category": "sycophancy",
                            "pattern": pattern["pattern"],
                            "suggestion": "Am I adding signal or just validating?"
                        })

            elif pattern["check"] == "verbosity":
                # Check length
                if len(output_text) > 1000 and "terse" in pattern["pattern"]:
                    warnings.append({
                        "category": "verbosity",
                        "pattern": pattern["pattern"],
                        "suggestion": "User prefers terse. Can this be shorter?"
                    })

        return warnings

    def check_context_update(self, context_update):
        """Validate context.json updates"""
        warnings = []

        # Check if learnings are being recorded
        if "learned" in context_update and not context_update["learned"]:
            warnings.append({
                "category": "learning",
                "suggestion": "No learnings recorded. Did you learn anything?"
            })

        # Check if decisions have reasoning
        if "decided" in context_update and context_update["decided"]:
            if "note" not in context_update or not context_update["note"]:
                warnings.append({
                    "category": "documentation",
                    "suggestion": "Decisions made but no note explaining why"
                })

        return warnings


def validate_before_save(context_path, lessons_path):
    """Run validation before saving context"""
    validator = LearningsValidator(lessons_path)

    # Load context
    with open(context_path) as f:
        context = json.load(f)

    # Get latest log entry
    if context.get("log"):
        latest = context["log"][-1]
        warnings = validator.check_context_update(latest)

        if warnings:
            print("\\n⚠️  LEARNINGS VALIDATION WARNINGS:")
            for w in warnings:
                print(f"  [{w['category']}] {w['suggestion']}")
            print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        context_path = sys.argv[1]
        lessons_path = sys.argv[2] if len(sys.argv) > 2 else "lessons.md"
        validate_before_save(context_path, lessons_path)
    else:
        print("Usage: python learnings_validator.py <context_path> [lessons_path]")
