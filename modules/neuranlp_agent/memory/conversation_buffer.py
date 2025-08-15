# File: modules/neuranlp_agent/memory/conversation_buffer.py

from langchain.memory import ConversationBufferMemory

def get_conversation_memory():
    """
    Creates a new instance of a short-term conversational memory buffer.
    This is intentionally NOT a singleton. Each new user session/thread
    would ideally get its own separate memory instance.
    """

    # We set return_messages=True so that the memory object provides a clean
    # list of Human and AI messages for the agent's prompt.
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return memory