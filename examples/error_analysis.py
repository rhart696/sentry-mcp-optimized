#!/usr/bin/env python3
"""
Error Analysis Example

This example demonstrates using Sentry MCP Optimized for
comprehensive error analysis and automated triage.
"""

import asyncio
import os
from sentry_mcp import SentryMCPOptimized


async def main():
    """Error analysis workflow example"""

    sentry = SentryMCPOptimized(
        auth_token=os.getenv("SENTRY_AUTH_TOKEN"),
        organization=os.getenv("SENTRY_ORG_SLUG", "my-org")
    )

    project_slug = os.getenv("SENTRY_PROJECT", "PYTHON-1")

    print("🔬 Sentry MCP Optimized - Error Analysis Example\n")
    print(f"🎯 Analyzing project: {project_slug}\n")

    # Get high-frequency errors
    print("📊 Fetching high-frequency errors...")
    issues = await sentry.list_issues(
        project=project_slug,
        status="unresolved",
        sort="freq",  # Most frequent first
        limit=10
    )

    if not issues:
        print("✅ No unresolved issues found!")
        return

    print(f"✓ Found {len(issues)} issues\n")

    # Analyze each issue
    for i, issue in enumerate(issues, 1):
        print(f"{'='*60}")
        print(f"Issue {i}/{len(issues)}: {issue['title']}")
        print(f"{'='*60}\n")

        # Perform comprehensive analysis
        print("🔍 Analyzing error...")
        analysis = await sentry.analyze_error(issue["id"])

        # Display issue summary
        issue_data = analysis['issue']
        print(f"📋 Issue Summary:")
        print(f"  ID: {issue_data['id']}")
        print(f"  Level: {issue_data['level']}")
        print(f"  Status: {issue_data['status']}")
        print(f"  Occurrences: {issue_data['count']}")
        print(f"  Users Affected: {issue_data.get('user_count', 'N/A')}")

        # Display event details
        event_data = analysis['event']
        print(f"\n💥 Latest Event:")
        print(f"  Event ID: {event_data['event_id']}")
        print(f"  Platform: {event_data.get('platform', 'N/A')}")

        # Display AI analysis
        analysis_data = analysis['analysis']
        print(f"\n🤖 AI Analysis:")
        print(f"  Error Type: {analysis_data['error_type']}")
        print(f"  Primary File: {analysis_data['primary_file']}")
        print(f"  Suggested Fix: {analysis_data['suggested_fix']}")

        # Display stack trace
        if event_data.get('stack_trace'):
            print(f"\n📚 Stack Trace (top 5 frames):")
            for frame in event_data['stack_trace'][:5]:
                print(f"  {frame['filename']}:{frame['lineno']} in {frame['function']}")
                if frame.get('context_line'):
                    print(f"    → {frame['context_line'].strip()}")

        # Auto-triage based on severity
        print(f"\n⚖️  Triage Recommendation:")
        if issue_data['count'] < 5 and issue_data.get('user_count', 0) < 2:
            print("  → Low priority: Few occurrences, minimal user impact")
            print("  → Recommendation: Can be ignored or assigned to backlog")
        elif issue_data['count'] > 100 or issue_data.get('user_count', 0) > 20:
            print("  → HIGH PRIORITY: High frequency or widespread user impact")
            print("  → Recommendation: Assign to on-call engineer immediately")
        else:
            print("  → Medium priority: Moderate impact")
            print("  → Recommendation: Assign to appropriate team")

        print()

    # Summary statistics
    print(f"{'='*60}")
    print("📈 Summary Statistics")
    print(f"{'='*60}\n")

    total_occurrences = sum(issue['count'] for issue in issues)
    avg_occurrences = total_occurrences / len(issues)

    # Group by error type
    error_types = {}
    for issue in issues:
        # You would get this from analysis, simplified here
        error_type = issue['level']
        error_types[error_type] = error_types.get(error_type, 0) + 1

    print(f"Total Issues: {len(issues)}")
    print(f"Total Occurrences: {total_occurrences}")
    print(f"Average Occurrences: {avg_occurrences:.1f}")
    print(f"\nError Breakdown:")
    for error_type, count in error_types.items():
        print(f"  {error_type}: {count} issues")

    # Recommendations
    print(f"\n💡 Recommendations:")
    high_priority = [i for i in issues if i['count'] > 100]
    if high_priority:
        print(f"  • {len(high_priority)} high-priority issues need immediate attention")
    low_priority = [i for i in issues if i['count'] < 5]
    if low_priority:
        print(f"  • {len(low_priority)} low-priority issues can be deprioritized")
    print(f"  • Focus on fixing issues affecting the most users first")

    print("\n✅ Analysis completed!")


if __name__ == "__main__":
    if not os.getenv("SENTRY_AUTH_TOKEN"):
        print("❌ Error: SENTRY_AUTH_TOKEN environment variable not set")
        exit(1)

    asyncio.run(main())
