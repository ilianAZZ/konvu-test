from cve import fetch_cve_data
from dependencies import scan_dependencies
from llm_clean import print_agent_context
from llm_prompt import explain
from llm_init import get_agent, send_files_to_api
from code_base_read import get_code_files
from env import CODE_BASE_PATH, MISTRAL_API_KEY
import sys


def explain_cve(cve_id, codebase_path="."):

    cve_data = fetch_cve_data(cve_id)

    deps = scan_dependencies(codebase_path)

    agent = get_agent(codebase_path)

    output = explain(
        agent=agent,
        cve_data=cve_data,
        dependencies=deps,
        api_key=MISTRAL_API_KEY
    )

    print(output)


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) < 2:
        print("Usage: python main.py <vuln_id> [codebase_path]")
        sys.exit(1)

    cve_id = argv[1]
    codebase_path = argv[2] if len(argv) > 2 else CODE_BASE_PATH

    explain_cve(cve_id,
                codebase_path=codebase_path)
