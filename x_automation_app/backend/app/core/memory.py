from langgraph.store.memory import InMemoryStore

def get_memory_store():
    """
    Initializes and returns a memory store for LangGraph.

    For development, this uses a simple InMemoryStore, which is volatile.
    For production, this should be updated to use a persistent store like AsyncPostgresStore.
    """
    # The embedding model and its dimensions are configured here.
    # We use "openai:text-embedding-3-small" as a default, which has 1536 dimensions.
    # This part can be made configurable if support for other embedding models is needed in the future.
    store = InMemoryStore(
        index={
            "dims": 1536,
            "embed": "openai:text-embedding-3-small",
        }
    )
    return store

# A global instance of the memory store to be used across the application during a single run.
memory_store = get_memory_store() 