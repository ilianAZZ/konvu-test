"""
Mistral AI Explainer
Uses Mistral LLM to generate clear explanations of CVE impact
"""

from typing import Dict, Optional
from mistralai import Agent, Mistral
from cve import CVEData
from dependencies import Dependency


def explain(
    agent: Agent,
    cve_data: CVEData,
    dependencies: list[Dependency],
    api_key: Optional[str] = None
) -> str:
    """
    Generate a clear explanation using Mistral AI
    Uses the free tier: mistral-small-latest
    """

    # Build the prompt
    prompt = build_prompt(cve_data, dependencies)

    print("Generated Prompt:")
    print(prompt)

    print('------')

    # Call Mistral API

    client = Mistral(api_key=api_key)

    response = client.beta.conversations.start(
        agent_id=agent.id,
        inputs=prompt
    )

    message_outputs = [
        output for output in response.outputs if output.type == 'message.output']

    if message_outputs:
        final_message = message_outputs[-1]
        return final_message.content
    else:
        print("No message output found")
        return None


def build_prompt(cve_data: CVEData, dependencies: list[Dependency]) -> str:
    """Build an optimized prompt for Mistral"""

    # THis leads for the agent to focus on these dependencies instead of exploring the document library
    # affected_deps = [dep for dep in dependencies if dep.get('affected', False)]
    # affected_summary = ""
    # if affected_deps:
    #     affected_summary = "**AFFECTED DEPENDENCIES IN THIS CODEBASE:**\n"
    #     for dep in affected_deps:
    #         affected_summary += f"- {dep['name']} v{dep['version']} ({dep['ecosystem']})\n"
    # else:
    #     affected_summary = "**NO DIRECTLY AFFECTED DEPENDENCIES FOUND**\n"

    # Format CVE info
    cve_summary = f"""
**CVE ID:** {cve_data.get('id')}
**Severity:** {cve_data.get('database_specific', 'Unknown')}
**Summary:** {cve_data.get('summary', 'No summary')}

**Details:** {cve_data.get('details', 'No details available')[:500]}

**Affected Packages (from CVE database):**
{format_affected_packages(cve_data.get('affected_packages', []))}
"""

    prompt = f"""Analyze this CVE and its impact on the provided codebase.

{cve_summary}

**Dependencies in codebase:** {len(dependencies)} total packages
EXPLORE DEPENDENCIES USING AGENT TOOLS IN YOUR AGENT CONTEXT. YOU CAN EXPLORE FILES AND THEIR CONTENT.
IF YOU HAVE ANY DOUBTS ABOUT DEPENDENCIES OR USAGE, STATE THAT CLEARLY AND DO NOT ASSUME AFFECTED STATUS.
---
TASK:

Provide a clear, actionable report for an application security engineer. Include:

1. **What is this vulnerability?** (2–3 sentences in plain language)

2. **Is this codebase affected?** 
   - YES/NO/UNCERTAIN (pick one)
   - Explain why, based on available evidence.
   - If manifests or dependency data are missing, explicitly mention that your assessment may be incomplete.

3. **Risk Assessment**
   - If affected: actual risk and exploitation context
   - If not affected or uncertain: explain why, and note what would need checking

4. **Recommended Actions**
   - Immediate steps (if vulnerable)
   - Verification steps if unsure
   - Preventive measures

5. **Production Impact**
   - Is this dependency/tool used at build-time, dev-time, or runtime?

6. **Confidence Level** (Low / Medium / High)
   - Be conservative: if dependency data or manifests are missing, confidence should be “Low”.

7. **Is risky for the project:** 
   - YES / NO / UNCERTAIN
   - Reply NO only if evidence strongly shows the project is not affected.

Keep it concise, actionable, and avoid unnecessary technical jargon.
"""

    return prompt


def format_affected_packages(packages: list) -> str:
    """Format affected packages list"""
    if not packages:
        return "No specific package information available"

    result = []
    for pkg in packages:
        name = pkg.get('name', 'Unknown')
        ecosystem = pkg.get('ecosystem', 'Unknown')
        versions = ', '.join(pkg.get('versions', [])[:3])
        result.append(f"- {name} ({ecosystem}) - versions: {versions}")

    return '\n'.join(result) if result else "No package data"


def format_dependencies_summary(dependencies: list[Dependency]) -> str:
    """Format dependencies summary"""
    if not dependencies:
        return "None found"

    return '\n'.join(str(dep) for dep in dependencies)
