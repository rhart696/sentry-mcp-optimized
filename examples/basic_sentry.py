#!/usr/bin/env python3
"""
Basic Sentry MCP Optimized Example

This example demonstrates basic usage of Sentry MCP Optimized for
listing and retrieving issue information.
"""

import asyncio
import os
from sentry_mcp import SentryMCPOptimized


async def main():
    """Basic Sentry operations example"""

    # Initialize with environment variables
    sentry = SentryMCPOptimized(
        auth_token=os.getenv("SENTRY_AUTH_TOKEN"),
        organization=os.getenv("SENTRY_ORG_SLUG", "my-org")
    )

    print("🔍 Sentry MCP Optimized - Basic Example\n")

    # List all accessible projects
    print("📁 Fetching projects...")
    projects = await sentry.list_projects()
    print(f"✓ Found {len(projects)} projects:")
    for project in projects[:5]:  # Show first 5
        print(f"  - {project['name']} ({project['slug']})")

    # Select a project (use first project or specify)
    project_slug = os.getenv("SENTRY_PROJECT", projects[0]["slug"] if projects else "PYTHON-1")
    print(f"\n🎯 Working with project: {project_slug}")

    # List recent unresolved issues
    print(f"\n📋 Fetching unresolved issues...")
    issues = await sentry.list_issues(
        project=project_slug,
        status="unresolved",
        limit=5,
        sort="date"  # Most recent first
    )

    if not issues:
        print("✓ No unresolved issues found!")
        return

    print(f"✓ Found {len(issues)} unresolved issues:\n")

    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['title']}")
        print(f"   ID: {issue['id']}")
        print(f"   Level: {issue['level']}")
        print(f"   Count: {issue['count']} occurrences")
        print(f"   First seen: {issue['first_seen']}")
        print(f"   Last seen: {issue['last_seen']}")
        print()

    # Get detailed information about the first issue
    if issues:
        first_issue = issues[0]
        print(f"🔎 Getting details for: {first_issue['title']}\n")

        details = await sentry.get_issue_details(first_issue["id"])

        print(f"Title: {details['title']}")
        print(f"Culprit: {details.get('culprit', 'N/A')}")
        print(f"Status: {details['status']}")
        print(f"Level: {details['level']}")
        print(f"Total occurrences: {details['count']}")
        print(f"Affected users: {details.get('user_count', 'N/A')}")

        if details.get('metadata'):
            print(f"\n📊 Metadata:")
            print(f"  Type: {details['metadata'].get('type', 'N/A')}")
            print(f"  Value: {details['metadata'].get('value', 'N/A')}")
            print(f"  Filename: {details['metadata'].get('filename', 'N/A')}")

        if details.get('tags'):
            print(f"\n🏷️  Tags:")
            for tag in details['tags'][:5]:
                print(f"  {tag['key']}: {tag['value']}")

    # Get latest event (stack trace)
    if issues:
        print(f"\n📄 Fetching latest event...")
        event = await sentry.get_latest_event(first_issue["id"])

        print(f"Event ID: {event['event_id']}")
        print(f"Platform: {event.get('platform', 'N/A')}")
        print(f"Message: {event.get('message', 'N/A')}")

        if event.get('stack_trace'):
            print(f"\n📚 Stack Trace (top 3 frames):")
            for frame in event['stack_trace'][:3]:
                print(f"  {frame['filename']}:{frame['lineno']} in {frame['function']}")
                if frame.get('context_line'):
                    print(f"    {frame['context_line'].strip()}")

    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    # Ensure environment variables are set
    if not os.getenv("SENTRY_AUTH_TOKEN"):
        print("❌ Error: SENTRY_AUTH_TOKEN environment variable not set")
        print("\nSet it with:")
        print("  export SENTRY_AUTH_TOKEN='your_token_here'")
        exit(1)

    # Run async main function
    asyncio.run(main())
