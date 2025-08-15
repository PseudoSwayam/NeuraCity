# File: modules/neuranlp_agent/agent_core.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, create_react_agent
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .utils import config
from utils.config_loader import settings
from .utils import api_triggers 
from memorycore.memory_manager import get_memory_core
import logging
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate

logging.basicConfig(level=config.LOGGING_LEVEL)

REACT_PROMPT = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

class AgentCore:
    def __init__(self):
        self.memory_core = get_memory_core()

        self.llm, self.source = self._initialize_llms()
        self.tools = self._setup_tools()
        
        with open("./modules/neuranlp_agent/prompts/base_prompt.txt") as f:
            base_prompt_text = f.read()

        full_prompt_string = f"{base_prompt_text}\n\n{REACT_PROMPT}"
        self.prompt = PromptTemplate.from_template(full_prompt_string)
        self.conversation_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.conversation_memory,
            verbose=True,
            handle_parsing_errors="I'm sorry, I had trouble understanding my thoughts. Could you please rephrase?",
            max_iterations=5,
            prompt_template_kwargs={"base_prompt": base_prompt_text}
        )

    def _initialize_llms(self):
        """Initializes Gemini and Ollama models with a fallback mechanism."""
        try:
            safety_settings = {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", # Use the stable gemini-pro model name
                google_api_key=settings.GEMINI_API_KEY, 
                convert_system_message_to_human=True,
                safety_settings=safety_settings
            )
            logging.info("Successfully initialized Gemini Pro with custom safety settings.")
            return llm, "gemini"
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini, falling back to Ollama: {e}")
            llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
            logging.info(f"Using Ollama with model {settings.OLLAMA_MODEL}.")
            return llm, "ollama"

    def _setup_tools(self):
        """Sets up the tools available to the agent."""
        tools = [
            Tool(
                name="SearchKnowledgeBase",
                func=self.memory_core.vector.query,
                description="Use this for answering factual questions. It searches a knowledge base of official campus documents. Good for questions about locations, rules, schedules, etc. Does not search conversation history."
            ),
            Tool.from_function(
                func=api_triggers.get_on_campus_users,
                name="CheckCampusAttendance",
                description="Use this to find out which users are currently checked-in on campus. Takes no input."
            ),
            Tool.from_function(
                func=api_triggers.call_security,
                name="CallSecurity",
                description="Use this tool to dispatch security to a specified location in case of an emergency. The input must be ONLY the location as a string (e.g., 'Main Library')."
            ),
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