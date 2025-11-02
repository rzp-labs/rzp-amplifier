"""Track and validate orchestrator delegation patterns."""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal


class DelegationAudit:
    """Track modifications to ensure proper delegation."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.audit_file = Path(f".claude/sessions/{session_id}/delegation_audit.jsonl")
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)

    def record_modification(self, file_path: str, tool: str, source: Literal["main", "agent"]) -> None:
        """Record every file modification with source."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "tool": tool,
            "source": source,
        }

        with open(self.audit_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def get_violations(self) -> list[dict]:
        """Get all boundary violations (main orchestrator modifications)."""
        if not self.audit_file.exists():
            return []

        violations = []
        with open(self.audit_file) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if record["source"] == "main":
                        violations.append(record)
                except json.JSONDecodeError:
                    # Skip malformed lines (corrupted audit data)
                    continue

        return violations

    def validate_session(self) -> dict:
        """Check for orchestrator boundary violations."""
        violations = self.get_violations()

        return {"status": "violated" if violations else "clean", "violations": violations, "count": len(violations)}

    def report(self) -> str:
        """Generate human-readable violation report."""
        result = self.validate_session()

        if result["status"] == "clean":
            return "✅ Clean session - all modifications properly delegated"

        report = [f"⚠️  Found {result['count']} boundary violation(s):", ""]

        for v in result["violations"][:10]:  # Show first 10
            report.append(f"  • {v['file']} (via {v['tool']}) at {v['timestamp']}")

        if result["count"] > 10:
            report.append(f"  ... and {result['count'] - 10} more")

        report.append("")
        report.append("Main orchestrator should delegate modifications via Task tool.")

        return "\n".join(report)
