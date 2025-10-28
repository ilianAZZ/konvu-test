from mistralai import Agent, Mistral
from env import MISTRAL_API_KEY, MISTRAL_AGENT_NAME
from code_base_read import get_code_files
import json

client = Mistral(api_key=MISTRAL_API_KEY)


def send_files_to_api(client: Mistral, lib_id: str, codebase_path: str) -> list[str]:
    """
    Upload code files from the codebase to the Mistral API library
    1. Scan the codebase to get all code files
    2. Upload each file to the specified library in Mistral API
    3. Return list of uploaded file IDs
    4. Print upload progress and errors
    Arguments:
        client: Mistral API client instance
        lib_id: ID of the Mistral library to upload files to
        codebase_path: Path to the codebase directory
    Returns:
        List of uploaded file IDs: List[str]
    """

    file_paths = get_code_files(codebase_path)

    errors = []
    file_ids = []

    print(f"Uploading {len(file_paths)} code files to Mistral API...")

    for file_path in file_paths[:10]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                client.beta.libraries.documents.upload(
                    library_id=lib_id,
                    file={
                        "file_name": file_path,
                        "content": content,
                    }
                )
                file_ids.append(file_path)

            print(".", end='', flush=True)
        except Exception as e:
            print("X", end='', flush=True)
            errors.append((file_path, str(e)))

    if errors:
        print(f"\n\nFailed to upload {len(errors)} files:")
        for err in errors:
            print(f"- {err[0]}: {err[1]}")
    else:
        print("\nAll files uploaded successfully")

    return file_ids


def create_agent(codebase_path: str) -> Agent:
    """Create a Mistral agent for vulnerability code analysis"""

    library = client.beta.libraries.create(
        name=f"{MISTRAL_AGENT_NAME}_LIB", description="Library for konvu code analysis")

    lib_id = library.id

    uploaded_files = send_files_to_api(client, lib_id, codebase_path)

    # Ensure at least one file was uploaded, otherwise it's useless to create the agent
    if len(uploaded_files) == 0:
        raise Exception("No files were uploaded to the library.")

    agent = client.beta.agents.create(
        model="mistral-medium-2505",
        name=MISTRAL_AGENT_NAME,
        description="Agent to analyze codebases for security vulnerabilities.",
        instructions="""You are a code analysis expert.
            When asked about the codebase, ALWAYS use the document_library tool to search for relevant files.
            Use the uploaded documents to answer questions accurately.""",
        tools=[{"type": "document_library", "library_ids": [lib_id]},
               {"type": "code_interpreter"}],
        completion_args={
            "temperature": 0.3,
            "tool_choice": "auto"
        }
    )

    print("Created Mistral agent")
    return agent


def get_agent(codebase_path: str) -> Agent | None:
    """
    Main Function that initialize the agent
    - Create the library
    - Add documents
    - Create agent with linked files
    """
    agent_name = MISTRAL_AGENT_NAME

    agents = client.beta.agents.list()
    for agent in agents:
        if agent.name == agent_name:
            return agent

    # If not found, create it
    return create_agent(codebase_path)
