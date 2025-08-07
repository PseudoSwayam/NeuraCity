# File: modules/neuranlp_agent/agent_core.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, create_react_agent
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .utils import config, api_triggers
from memorycore.memory_manager import get_memory_core
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

MANUAL_REACT_PROMPT_TEMPLATE = """
{base_prompt}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer and am ready to respond to the user.
Final Answer: the final, conclusive answer to the original input question that will be shown to the user.

Begin! After the final Observation, you MUST use the 'Thought' and 'Final Answer' format.

Question: {input}
Thought:{agent_scratchpad}
"""

class AgentCore:
    def __init__(self):
        self.memory_core = get_memory_core()

        self.llm, self.source = self._initialize_llms()
        self.tools = self._setup_tools()
        
        with open("./modules/neuranlp_agent/prompts/base_prompt.txt") as f:
            base_prompt_text = f.read()

        self.prompt = PromptTemplate.from_template(MANUAL_REACT_PROMPT_TEMPLATE).partial(
            base_prompt=base_prompt_text
        )

        agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors="I'm sorry, I had trouble understanding my own thoughts. Could you please rephrase?"
        )

    def _initialize_llms(self):
        """Initializes Gemini and Ollama models with a fallback mechanism."""
        try:
            safety_settings = {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", # Use the stable gemini-pro model name
                google_api_key=config.GEMINI_API_KEY, 
                convert_system_message_to_human=True,
                safety_settings=safety_settings
            )
            logging.info("Successfully initialized Gemini Pro with custom safety settings.")
            return llm, "gemini"
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini, falling back to Ollama: {e}")
            llm = Ollama(base_url=config.OLLAMA_BASE_URL, model=config.OLLAMA_MODEL)
            logging.info(f"Using Ollama with model {config.OLLAMA_MODEL}.")
            return llm, "ollama"

    def _setup_tools(self):
        """Sets up the tools available to the agent."""
        tools = [
            Tool(
                name="SearchSharedVectorMemory", 
                func=self.memory_core.vector.query, 
                description="Use for semantic search of conversations and documents. Ideal for answering 'who', 'what', 'where', 'how' questions based on past knowledge."
            ),
            
            # --- THE ONLY NEEDFUL CHANGE IS HERE ---
            # Replace the simple Tool() constructor with Tool.from_function()
            # This robustly tells the agent that the function expects a simple string input.
            Tool.from_function(
                func=api_triggers.call_security,
                name="CallSecurity",
                description="Use this tool to dispatch security to a specified location in case of an emergency. The input must be ONLY the location as a string (e.g., 'Main Library')."
            ),
            # --- All other tools remain unchanged ---
            Tool(
                name="SendCampusAnnouncement", 
                func=api_triggers.send_announcement, 
                description="Use this tool to send a campus-wide announcement. This is for major alerts and requires authorization. The input is the message string."
            ),
            Tool.from_function(
                func=lambda input_str: api_triggers.notify_admin(
                    department=input_str.split(',')[0].strip(),
                    message=''.join(input_str.split(',')[1:]).strip()
                ),
                name="NotifyDepartmentAdmin",
                description="Use this tool to send a notification to a specific department's admin. The input must be a single comma-separated string of two values: the target department and the message. Example: 'IT, The Wi-Fi in the main auditorium is down.'"
            )
        ]
        return tools

    def run_query(self, query: str):
        """Processes a query through the agent."""
        try:
            response = self.agent_executor.invoke({"input": query})

            convo_text = f"User query: {query}\nAI response: {response['output']}"
            metadata = {"query": query}
            self.memory_core.vector.add(
                source='neuranlp_agent',
                type='conversation',
                text_content=convo_text,
                metadata=metadata
            )
            
            return {"response": response['output'], "source": self.source}
        except Exception as e:
            logging.error(f"Error running agent query: {e}")
            return {"response": "I'm sorry, I encountered an error and couldn't process your request.", "source": "error"}


def initialize_agent():
    """Initializes agent and loads documents into the shared MemoryCore."""
    core = get_memory_core()
    core.load_external_documents(config.DOCUMENT_SOURCES)
    return AgentCore()

agent_core = initialize_agent()