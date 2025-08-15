# File: modules/neuranlp_agent/agent_core.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, create_react_agent
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain.memory import ConversationBufferMemory
from typing import Optional
import logging

from .utils import config
from utils.config_loader import settings
from .utils import api_triggers
from memorycore.memory_manager import get_memory_core


logging.basicConfig(level=logging.INFO)

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

--- IMPORTANT ---
If an Action result is an error or indicates failure, your Final Answer MUST inform the user about the failure and suggest a next step. Do not retry the same action.

Final Answer: the final, conclusive answer to the original input question that will be shown to the user.

Begin!

PREVIOUS CONVERSATION:
{chat_history}

NEW QUESTION: {input}
Thought:{agent_scratchpad}
"""

class AgentCore:
    def __init__(self):
        self.memory_core = get_memory_core()
        self.llm, self.source = self._initialize_llms()
        self.current_auth_token: Optional[str] = None
        self.tools = self._setup_tools()
        
        with open("./modules/neuranlp_agent/prompts/base_prompt.txt") as f:
            base_prompt_text = f.read()

        self.prompt = PromptTemplate.from_template(MANUAL_REACT_PROMPT_TEMPLATE).partial(base_prompt=base_prompt_text)
        
        # Each user session will have its own conversational memory.
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        agent = create_react_agent(self.llm, self.tools, self.prompt)
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.conversation_memory,
            verbose=True,
            handle_parsing_errors="I'm sorry, I'm having trouble thinking clearly. Could you please rephrase your request?",
            max_iterations=5,
        )

    def _initialize_llms(self):
        """Initializes Gemini, using the central config for the API key."""
        try:
            safety_settings = { HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", 
                google_api_key=settings.GEMINI_API_KEY, 
                convert_system_message_to_human=True,
                safety_settings=safety_settings
            )
            logging.info("Successfully initialized Gemini Pro.")
            return llm, "gemini"
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini, falling back to Ollama: {e}")
            llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
            return llm, "ollama"

    def _setup_tools(self):
        """Sets up tools that are now aware of the agent's current security context."""
        tools = [
            Tool.from_function(
                func=lambda dummy_input: api_triggers.get_system_health_summary(token=self.current_auth_token),
                name="GetSystemHealth",
                description="Use this tool to get a health summary of all NeuraCity modules. Requires admin privileges. Takes no input."
            ),
            Tool.from_function(
                func=lambda dummy_input: api_triggers.get_on_campus_users(),
                name="CheckCampusAttendance",
                description="Use to find out which users are currently checked-in on campus. Takes no input."
            ),
            # Unsecured tools
            Tool(name="SearchKnowledgeBase", func=self.memory_core.vector.query, description="Use for factual questions from campus documents."),
            Tool.from_function(func=api_triggers.call_security, name="CallSecurity", description="Use for emergencies to dispatch security."),
            Tool.from_function(func=api_triggers.send_announcement, name="SendCampusAnnouncement", description="Use to send a campus-wide announcement."),
            Tool.from_function(
                func=lambda input_str: api_triggers.notify_admin(
                    department=input_str.split(',')[0].strip(),
                    message=''.join(input_str.split(',')[1:]).strip()
                ),
                name="NotifyDepartmentAdmin",
                description="Use to send a notification to a department admin. Input must be a comma-separated string of the department and message."
            )
        ]
        return tools

    def run_query(self, query: str, auth_token: Optional[str] = None):
        """
        Processes a query, setting the security context (auth_token) for the duration of the run.
        """
        self.current_auth_token = auth_token
        try:
            response = self.agent_executor.invoke({"input": query})
            convo_text = f"User query: {query}\nAI response: {response['output']}"
            self.memory_core.vector.add(
                source='neuranlp_agent', type='conversation_log',
                text_content=convo_text, metadata={"query": query}
            )
            
            return {"response": response['output'], "source": self.source}
        except Exception as e:
            logging.error(f"Error running agent query: {e}", exc_info=True)
            return {"response": "I'm sorry, a critical error occurred.", "source": "error"}
        finally:
            self.current_auth_token = None
            
def initialize_agent():
    """Initializes agent and loads documents into the shared MemoryCore."""
    core = get_memory_core()
    core.load_external_documents(config.DOCUMENT_SOURCES)
    return AgentCore()

agent_core = initialize_agent()