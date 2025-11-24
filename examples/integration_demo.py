#!/usr/bin/env python3
"""
Full Integration Demo

This example demonstrates a complete integration workflow including:
- Project discovery
- Error monitoring
- Automated triage
- Issue management
- Reporting
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any
from sentry_mcp import SentryMCPOptimized


class SentryMonitor:
    """Automated Sentry monitoring and triage"""

    def __init__(self, sentry: SentryMCPOptimized):
        self.sentry = sentry
        self.stats = {
            "total_issues": 0,
            "analyzed": 0,
            "auto_triaged": 0,
            "high_priority": 0
        }

    async def discover_projects(self) -> List[Dict[str, Any]]:
        """Discover all accessible projects"""
        print("🔍 Discovering projects...")
        projects = await self.sentry.list_projects()
        print(f"✓ Found {len(projects)} projects\n")

        for project in projects:
            print(f"  📁 {project['name']}")
            print(f"     Slug: {project['slug']}")
            print(f"     Platform: {project['platform']}")
            print(f"     Status: {project['status']}")
            print()

        return projects

    async def monitor_project(self, project_slug: str) -> Dict[str, Any]:
        """Monitor errors for a specific project"""
        print(f"📊 Monitoring project: {project_slug}")

        # Get unresolved issues
        issues = await self.sentry.list_issues(
            project=project_slug,
            status="unresolved",
            sort="freq",
            limit=20
        )

        self.stats["total_issues"] += len(issues)

        print(f"✓ Found {len(issues)} unresolved issues")

        return {
            "project": project_slug,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }

    async def triage_issue(self, issue: Dict[str, Any]) -> Dict[str, str]:
        """Auto-triage an issue based on severity"""
        count = issue['count']
        user_count = issue.get('user_count', 0)

        if count < 5 and user_count < 2:
            return {
                "priority": "low",
                "action": "ignore",
                "reason": "Low frequency, minimal user impact"
            }
        elif count > 100 or user_count > 20:
            return {
                "priority": "high",
                "action": "assign_oncall",
                "reason": "High frequency or widespread impact"
            }
        else:
            return {
                "priority": "medium",
                "action": "assign_team",
                "reason": "Moderate impact, needs team review"
            }

    async def analyze_and_triage(self, project_slug: str):
        """Analyze and auto-triage issues"""
        print(f"\n🔬 Analyzing issues for {project_slug}...")

        issues = await self.sentry.list_issues(
            project=project_slug,
            status="unresolved",
            limit=10
        )

        triaged_issues = []

        for issue in issues:
            self.stats["analyzed"] += 1

            # Get triage recommendation
            triage = await self.triage_issue(issue)

            # Perform full analysis for high-priority issues
            if triage["priority"] == "high":
                self.stats["high_priority"] += 1
                analysis = await self.sentry.analyze_error(issue["id"])

                triaged_issues.append({
                    "issue": issue,
                    "triage": triage,
                    "analysis": analysis
                })

                print(f"\n  🚨 HIGH PRIORITY: {issue['title']}")
                print(f"     Occurrences: {issue['count']}")
                print(f"     Error Type: {analysis['analysis']['error_type']}")
                print(f"     Suggested Fix: {analysis['analysis']['suggested_fix']}")
            else:
                triaged_issues.append({
                    "issue": issue,
                    "triage": triage,
                    "analysis": None
                })

                self.stats["auto_triaged"] += 1

        return triaged_issues

    async def generate_report(self, project_slug: str):
        """Generate comprehensive error report"""
        print(f"\n📋 Generating Report for {project_slug}")
        print("="*60)

        # Get issues from last 24h
        issues = await self.sentry.list_issues(
            project=project_slug,
            period="24h",
            limit=50
        )

        # Calculate statistics
        total_issues = len(issues)
        total_occurrences = sum(i['count'] for i in issues)
        error_levels = {}
        for issue in issues:
            level = issue['level']
            error_levels[level] = error_levels.get(level, 0) + 1

        # Print report
        print(f"\n📊 Statistics (Last 24 hours):")
        print(f"  Total Issues: {total_issues}")
        print(f"  Total Occurrences: {total_occurrences}")
        print(f"\n  By Level:")
        for level, count in sorted(error_levels.items()):
            print(f"    {level}: {count} issues")

        # Top issues
        print(f"\n🔥 Top 5 Issues by Frequency:")
        sorted_issues = sorted(issues, key=lambda x: x['count'], reverse=True)[:5]
        for i, issue in enumerate(sorted_issues, 1):
            print(f"  {i}. {issue['title']}")
            print(f"     Count: {issue['count']} | Level: {issue['level']}")

        # Recommendations
        print(f"\n💡 Recommendations:")
        high_freq = [i for i in issues if i['count'] > 50]
        if high_freq:
            print(f"  • {len(high_freq)} high-frequency issues need immediate attention")
        recent = [i for i in issues if i['last_seen'] > i['first_seen']]
        if recent:
            print(f"  • {len(recent)} issues are actively occurring")
        print(f"  • Consider implementing error rate alerts")

        print()


async def main():
    """Main integration demo"""

    print("🚀 Sentry MCP Optimized - Full Integration Demo")
    print("="*60)
    print()

    # Initialize
    sentry = SentryMCPOptimized(
        auth_token=os.getenv("SENTRY_AUTH_TOKEN"),
        organization=os.getenv("SENTRY_ORG_SLUG", "my-org")
    )

    monitor = SentryMonitor(sentry)

    # 1. Discover projects
    projects = await monitor.discover_projects()

    if not projects:
        print("❌ No projects found")
        return

    # 2. Monitor first project
    project_slug = os.getenv("SENTRY_PROJECT", projects[0]["slug"])
    await monitor.monitor_project(project_slug)

    # 3. Analyze and triage
    await monitor.analyze_and_triage(project_slug)

    # 4. Generate report
    await monitor.generate_report(project_slug)

    # 5. Print summary statistics
    print("\n📈 Session Statistics")
    print("="*60)
    print(f"Total Issues Processed: {monitor.stats['total_issues']}")
    print(f"Issues Analyzed: {monitor.stats['analyzed']}")
    print(f"Auto-triaged: {monitor.stats['auto_triaged']}")
    print(f"High Priority Flagged: {monitor.stats['high_priority']}")

    print("\n✅ Integration demo completed successfully!")


if __name__ == "__main__":
    if not os.getenv("SENTRY_AUTH_TOKEN"):
        print("❌ Error: SENTRY_AUTH_TOKEN environment variable not set")
        print("\nSet it with:")
        print("  export SENTRY_AUTH_TOKEN='your_token_here'")
        print("  export SENTRY_ORG_SLUG='your-org'")
        print("  export SENTRY_PROJECT='your-project'  # Optional")
        exit(1)

    asyncio.run(main())
