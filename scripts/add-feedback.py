#!/usr/bin/env python3
"""
Add feedback to the FEEDBACK.md file.

Usage:
    python scripts/add-feedback.py --type problem --title "Issue title" --description "Details"
    python scripts/add-feedback.py --type enhancement --title "Feature idea" --description "Details"
    python scripts/add-feedback.py --type feedback --title "Observation" --description "Details"

Or interactively:
    python scripts/add-feedback.py
"""

import argparse
import re
from datetime import date
from pathlib import Path


def get_next_id(content: str, prefix: str) -> str:
    """Get the next sequential ID for a type."""
    pattern = rf'\[{prefix}(\d+)\]'
    matches = re.findall(pattern, content)
    if matches:
        max_num = max(int(m) for m in matches)
        return f"{prefix}{max_num + 1:03d}"
    return f"{prefix}001"


def add_feedback(
    feedback_type: str,
    title: str,
    description: str,
    extra_field: str,
    extra_value: str
) -> str:
    """Add a new feedback entry to FEEDBACK.md."""

    feedback_path = Path(__file__).parent.parent / "FEEDBACK.md"

    if not feedback_path.exists():
        print("❌ FEEDBACK.md not found")
        return ""

    content = feedback_path.read_text()

    # Determine prefix and section
    type_config = {
        "problem": {
            "prefix": "P",
            "section": "## Problems",
            "field_name": "Severity",
            "extra_field": "Suggested Fix"
        },
        "enhancement": {
            "prefix": "E",
            "section": "## Enhancements",
            "field_name": "Priority",
            "extra_field": "Benefit"
        },
        "feedback": {
            "prefix": "F",
            "section": "## Feedback",
            "field_name": "From",
            "extra_field": "Action"
        }
    }

    config = type_config.get(feedback_type.lower())
    if not config:
        print(f"❌ Unknown type: {feedback_type}")
        return ""

    # Generate ID
    item_id = get_next_id(content, config["prefix"])

    # Create entry
    today = date.today().isoformat()
    entry = f"""
### [{item_id}] {title}
- **Date:** {today}
- **{config['field_name']}:** {extra_field}
- **Description:** {description}
- **{config['extra_field']}:** {extra_value}
- **Status:** Open
"""

    # Find section and insert
    section_marker = config["section"]
    section_pos = content.find(section_marker)

    if section_pos == -1:
        print(f"❌ Section '{section_marker}' not found")
        return ""

    # Find the end of the section (next ## or end of problems/enhancements/feedback)
    next_section = content.find("\n## ", section_pos + len(section_marker))
    if next_section == -1:
        next_section = content.find("\n---\n\n## Template", section_pos)

    if next_section == -1:
        # Append to end of section
        insert_pos = len(content)
    else:
        # Insert before next section
        insert_pos = next_section

    # Insert the entry
    new_content = content[:insert_pos].rstrip() + "\n" + entry + "\n" + content[insert_pos:].lstrip()

    # Write back
    feedback_path.write_text(new_content)

    print(f"✅ Added [{item_id}] {title}")
    return item_id


def interactive_mode():
    """Run in interactive mode."""
    print("📝 Add Feedback to MDD TDD Git Dev Factory")
    print("=" * 50)
    print()

    # Get type
    print("Type:")
    print("  1. Problem (something broken)")
    print("  2. Enhancement (new feature)")
    print("  3. Feedback (observation)")
    choice = input("\nSelect (1-3): ").strip()

    type_map = {"1": "problem", "2": "enhancement", "3": "feedback"}
    feedback_type = type_map.get(choice)

    if not feedback_type:
        print("❌ Invalid choice")
        return

    # Get details
    title = input("\nTitle: ").strip()
    if not title:
        print("❌ Title required")
        return

    description = input("Description: ").strip()
    if not description:
        print("❌ Description required")
        return

    # Type-specific field
    if feedback_type == "problem":
        extra_field = input("Severity (Low/Medium/High): ").strip() or "Medium"
        extra_value = input("Suggested fix: ").strip() or "TBD"
    elif feedback_type == "enhancement":
        extra_field = input("Priority (Low/Medium/High): ").strip() or "Medium"
        extra_value = input("Benefit: ").strip() or "TBD"
    else:  # feedback
        extra_field = input("From (who gave feedback): ").strip() or "User"
        extra_value = input("Suggested action: ").strip() or "TBD"

    # Add it
    add_feedback(feedback_type, title, description, extra_field, extra_value)


def main():
    parser = argparse.ArgumentParser(description="Add feedback to FEEDBACK.md")
    parser.add_argument("--type", "-t", choices=["problem", "enhancement", "feedback"],
                        help="Type of feedback")
    parser.add_argument("--title", help="Title of the item")
    parser.add_argument("--description", "-d", help="Description")
    parser.add_argument("--severity", "--priority", "--from", dest="extra_field",
                        help="Severity/Priority/From value")
    parser.add_argument("--fix", "--benefit", "--action", dest="extra_value",
                        help="Suggested fix/Benefit/Action")

    args = parser.parse_args()

    # If all args provided, use them
    if args.type and args.title and args.description:
        add_feedback(
            args.type,
            args.title,
            args.description,
            args.extra_field or "Medium",
            args.extra_value or "TBD"
        )
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
