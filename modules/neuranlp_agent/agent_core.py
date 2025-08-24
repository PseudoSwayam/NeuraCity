# File: modules/neuranlp_agent/agent_core.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import AIMessage, HumanMessage
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain.memory import ConversationBufferMemory
from typing import Optional, Any
import logging

from .utils import config
from utils.config_loader import settings
from .utils import api_triggers
from memorycore.memory_manager import get_memory_core


logging.basicConfig(level=logging.INFO)

class AgentCore:
    def __init__(self):
        self.memory_core = get_memory_core()
        self.llm, self.source = self._initialize_llms()
        self.current_auth_token: Optional[str] = None
        self.tools = self._setup_tools()
        
        with open("./modules/neuranlp_agent/prompts/base_prompt.txt") as f:
            base_prompt_text = f.read()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", base_prompt_text),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Each user session will have its own conversational memory.
        self.agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
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

    def _parse_tool_input(self, tool_input: Any) -> str:
        """A robust helper to extract a simple string from a tool's input."""
        # The agent sometimes passes a dict like {'location': 'library'}, This function intelligently extracts the value.
        if isinstance(tool_input, dict):
            # Take the value of the first key
            return next(iter(tool_input.values()), "")
        return str(tool_input) # Otherwise, just convert to string

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
            Tool(
                name="CallSecurity",
                func=lambda location_input: api_triggers.call_security(self._parse_tool_input(location_input)),
                description="Use for emergencies to dispatch security to a location. The input is only the location as a string."
            ),
            Tool(
                name="SendCampusAnnouncement",
                func=lambda message_input: api_triggers.send_announcement(self._parse_tool_input(message_input)),
                description="Use to send a campus-wide announcement. The input is the full message string."
            ),
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