
from mistralai import Mistral
from env import MISTRAL_AGENT_NAME, MISTRAL_API_KEY


client = Mistral(api_key=MISTRAL_API_KEY)

mistral_agent = None
agents = client.beta.agents.list()
for agent in agents:
    if agent.name == MISTRAL_AGENT_NAME:
        mistral_agent = agent
        break

mistral_agent.add_document(
    '/Users/ilian/Documents/HeadOfScience/HOS-V2/package.json')

library = client.beta.libraries.create(
    name="MyCodeLibrary", description="Library for my codebase")

a = client.beta.libraries.list()
for lib in a:
    print(lib[1][0])

lib_id = '019a1810-d867-71e3-92a9-f797ca065fe3'

client.beta.libraries.documents.upload(
    library_id=lib_id,
    file={
        "file_name": "/Users/ilian/Documents/HeadOfScience/HOS-V2/package.json",
        "content": open('/Users/ilian/Documents/HeadOfScience/HOS-V2/package.json', 'r').read(),
    })

# List all document in the library
status = client.beta.libraries.documents.list(library_id=lib_id)
for doc in status:
    print(doc)

"""
('data', [DocumentOut(id='67531bb8-5dee-420d-a77c-6c78b5c6b3bb', library_id='019a1810-d867-71e3-92a9-f797ca065fe3', hash='fd173ff5d3afbbb6ab8df980d00460ed', mime_type='application/json', extension='json', size=2283, name='/Users/ilian/Documents/HeadOfScience/HOS-V2/package.json', created_at=datetime.datetime(2025, 10, 24, 21, 19, 29, 147216, tzinfo=TzInfo(UTC)), processing_status='Completed', uploaded_by_id='322a569e-88bb-4a57-b855-06edf76cd8f7', uploaded_by_type='Workspace', tokens_processing_total=2069, summary='The document is a package.json file for a monorepo project using pnpm and TurboRepo. It includes scripts for building, developing, linting, and formatting multiple packages (api, web, sdk). The project uses TypeScript, ESLint, Prettier, and other tools for development and maintenance.', last_processed_at=datetime.datetime(2025, 10, 24, 21, 19, 30, 578585, tzinfo=TzInfo(UTC)), number_of_pages=None, tokens_processing_main_content=1028, tokens_processing_summary=1041)])
"""

agent = client.beta.agents.create(
    model="mistral-medium-2505",
    name="test",
    description="Agent to analyze and reason about my codebase",
    instructions="""You are a code analysis expert.
        When asked about the codebase, ALWAYS use the document_library tool to search for relevant files.
        Use the uploaded documents to answer questions accurately.""",
    tools=[{"type": "document_library", "library_ids": [lib_id]}],
    completion_args={
        "temperature": 0.3,
        "tool_choice": "auto"
    }
)

# print(agent)
agentId = 'ag_019a1822634674f6866a65bfad2b8b41'

response = client.beta.conversations.start(
    agent_id=agentId,
    inputs=" the package.json file in the document library. Read its ENTIRE content. Based on the dependencies, what can you say about the project type and tech stack used?"
)

print(response)
print()
messageOutput = None
for output in response.outputs:
    if output.type == 'message.output':
        messageOutput = output
        break

print(messageOutput.content)
