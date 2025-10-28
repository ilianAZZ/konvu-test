from mistralai import Mistral

from env import MISTRAL_API_KEY
from llm_init import get_agent


def clean_agents(client: Mistral):
    """Clean all agents from the Mistral account"""

    agents = client.beta.agents.list()
    print(f"Found {len(agents)} agents to delete.")
    for agent in agents:

        print(f"Deleting agent: {agent.name} ({agent.id})")
        client.beta.agents.delete(agent_id=agent.id)


def clean_libs(client: Mistral):
    """Clean all libraries from the Mistral account"""

    libs = client.beta.libraries.list().data
    print(f"Found {len(libs)} libraries to delete.")
    for lib in libs:

        print(f"Deleting library: {lib.name} ({lib.id})")
        client.beta.libraries.delete(library_id=lib.id)


def clean_all():
    """
    Clean all agents and libraries from the Mistral account
    1. Delete all agents
    2. Delete all libraries
    """
    client = Mistral(api_key=MISTRAL_API_KEY)

    clean_agents(client)
    clean_libs(client)


def print_agent_context():
    """Print the context of the agent's document libraries"""

    client = Mistral(api_key=MISTRAL_API_KEY)
    agent = get_agent('')

    print("\n🧠  Agent Document Library Context")
    print("====================================\n")

    found_any = False

    for tool in agent.tools:
        if tool.type != "document_library":
            continue

        found_any = True
        library_ids = tool.library_ids
        print(
            f"📚  Agent uses {len(library_ids)} document librar{'y' if len(library_ids) == 1 else 'ies'}:")

        for library_id in library_ids:
            print(f"\n🗂️  Library ID: {library_id}")

            try:
                library = client.beta.libraries.get(library_id=library_id)
                print(f"   🔸 Name: {library.name}")
                print(
                    f"   📝 Description: {getattr(library, 'description', 'No description')}")
            except Exception as e:
                print(f"   ⚠️  Failed to fetch library info: {e}")
                continue

            try:
                docs_response = client.beta.libraries.documents.list(
                    library_id=library_id)
                # unpack tuple (pagination, [docs])
                pagination, documents = docs_response
            except Exception as e:
                print(f"   ⚠️  Failed to list documents: {e}")
                continue

            if not documents:
                print("   🚫 No documents found in this library.")
                continue

            print("\n   📄 Documents:")
            print("   ────────────────────────────────────────────────────────────")
            print("   🧾 Name\t\t📎 ID\t\t\t📏 Size")
            print("   ────────────────────────────────────────────────────────────")

            for doc in documents[1]:
                name = getattr(doc, "name", "Unknown")
                doc_id = getattr(doc, "id", "Unknown")
                size = f"{doc.size} bytes" if hasattr(
                    doc, "size") else "Unknown"
                print(f"   {name}\t{doc_id}\t{size}")

            print("   ────────────────────────────────────────────────────────────")

    if not found_any:
        print("❌  No document libraries found for this agent.")
