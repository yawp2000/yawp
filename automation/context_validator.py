"""
Context Integrity Validator
Validates context.json structure and prevents corruption
"""

import json
from pathlib import Path
from datetime import datetime

class ContextValidator:
    def __init__(self, context_path):
        self.context_path = Path(context_path)
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validation checks"""
        self.errors = []
        self.warnings = []

        # Check 1: File exists and readable
        if not self.validate_file_exists():
            return False

        # Check 2: Valid JSON
        context = self.validate_json()
        if context is None:
            return False

        # Check 3: Required structure
        if not self.validate_structure(context):
            return False

        # Check 4: Data integrity
        self.validate_data_integrity(context)

        # Check 5: Log consistency
        self.validate_log_consistency(context)

        # Check 6: Size checks
        self.validate_size(context)

        return len(self.errors) == 0

    def validate_file_exists(self):
        """Check file exists"""
        if not self.context_path.exists():
            self.errors.append({
                "severity": "CRITICAL",
                "check": "file_exists",
                "message": f"Context file not found: {self.context_path}"
            })
            return False
        return True

    def validate_json(self):
        """Check JSON is valid"""
        try:
            with open(self.context_path, encoding='utf-8') as f:
                context = json.load(f)
            return context
        except json.JSONDecodeError as e:
            self.errors.append({
                "severity": "CRITICAL",
                "check": "json_valid",
                "message": f"Invalid JSON: {str(e)}",
                "line": e.lineno,
                "column": e.colno
            })
            return None
        except Exception as e:
            self.errors.append({
                "severity": "CRITICAL",
                "check": "json_valid",
                "message": f"Cannot read file: {str(e)}"
            })
            return None

    def validate_structure(self, context):
        """Check required fields exist"""
        required_fields = ["instance", "log", "projects"]
        optional_fields = ["capabilities"]

        for field in required_fields:
            if field not in context:
                self.errors.append({
                    "severity": "HIGH",
                    "check": "structure",
                    "message": f"Missing required field: {field}"
                })

        for field in optional_fields:
            if field not in context:
                self.warnings.append({
                    "severity": "LOW",
                    "check": "structure",
                    "message": f"Optional field missing: {field}"
                })

        return len(self.errors) == 0

    def validate_data_integrity(self, context):
        """Check data types and values"""

        # Check instance number
        if "instance" in context:
            if not isinstance(context["instance"], int) or context["instance"] < 0:
                self.errors.append({
                    "severity": "HIGH",
                    "check": "data_integrity",
                    "message": f"Invalid instance number: {context['instance']}"
                })

        # Check log is array
        if "log" in context:
            if not isinstance(context["log"], list):
                self.errors.append({
                    "severity": "HIGH",
                    "check": "data_integrity",
                    "message": "Log must be an array"
                })

        # Check projects is object
        if "projects" in context:
            if not isinstance(context["projects"], dict):
                self.errors.append({
                    "severity": "HIGH",
                    "check": "data_integrity",
                    "message": "Projects must be an object"
                })

    def validate_log_consistency(self, context):
        """Check log entries are consistent"""
        if "log" not in context or not isinstance(context["log"], list):
            return

        log = context["log"]
        expected_instance = context.get("instance", 0)

        # Check log entries have required fields
        for i, entry in enumerate(log):
            if not isinstance(entry, dict):
                self.warnings.append({
                    "severity": "MEDIUM",
                    "check": "log_consistency",
                    "message": f"Log entry {i} is not an object"
                })
                continue

            # Check required fields
            if "n" not in entry:
                self.warnings.append({
                    "severity": "MEDIUM",
                    "check": "log_consistency",
                    "message": f"Log entry {i} missing instance number 'n'"
                })

            if "ts" not in entry:
                self.warnings.append({
                    "severity": "LOW",
                    "check": "log_consistency",
                    "message": f"Log entry {i} missing timestamp 'ts'"
                })

        # Check log matches instance count
        if log:
            last_entry = log[-1]
            if isinstance(last_entry, dict) and "n" in last_entry:
                if last_entry["n"] != expected_instance:
                    self.warnings.append({
                        "severity": "MEDIUM",
                        "check": "log_consistency",
                        "message": f"Log entry instance ({last_entry['n']}) doesn't match context instance ({expected_instance})"
                    })

    def validate_size(self, context):
        """Check file size and complexity"""
        # File size
        size_bytes = self.context_path.stat().st_size
        size_kb = size_bytes / 1024

        if size_kb > 500:
            self.warnings.append({
                "severity": "MEDIUM",
                "check": "size",
                "message": f"Context file is large: {size_kb:.1f} KB (consider compression)"
            })

        # Log length
        if "log" in context:
            log_len = len(context["log"])
            if log_len > 50:
                self.warnings.append({
                    "severity": "LOW",
                    "check": "size",
                    "message": f"Log has {log_len} entries (consider compression)"
                })

        # Token estimate
        context_str = json.dumps(context)
        estimated_tokens = len(context_str.split()) * 1.3

        if estimated_tokens > 5000:
            self.warnings.append({
                "severity": "MEDIUM",
                "check": "size",
                "message": f"Estimated {int(estimated_tokens)} tokens (may impact performance)"
            })

    def get_report(self):
        """Generate validation report"""
        report = []
        report.append("=" * 60)
        report.append("CONTEXT VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Summary
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            report.append("✓ All checks passed")
            report.append("")
        else:
            report.append(f"Found {len(self.errors)} error(s) and {len(self.warnings)} warning(s)")
            report.append("")

        # Errors
        if self.errors:
            report.append("ERRORS:")
            for err in self.errors:
                report.append(f"  [{err['severity']}] {err['check']}: {err['message']}")
            report.append("")

        # Warnings
        if self.warnings:
            report.append("WARNINGS:")
            for warn in self.warnings:
                report.append(f"  [{warn['severity']}] {warn['check']}: {warn['message']}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)


def validate_context(context_path):
    """Main entry point"""
    validator = ContextValidator(context_path)
    is_valid = validator.validate()

    return {
        "valid": is_valid,
        "errors": validator.errors,
        "warnings": validator.warnings
    }


if __name__ == "__main__":
    import sys

    context_path = sys.argv[1] if len(sys.argv) > 1 else "~/Desktop/ClaudeContext/context.json"

    validator = ContextValidator(context_path)
    validator.validate()
    print(validator.get_report())
