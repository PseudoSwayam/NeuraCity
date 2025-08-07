from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from .utils import config, api_triggers
from .memory.memory_handler import memory_handler
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

class AgentCore:
    def __init__(self):
        self.llm = self._initialize_llms()
        self.tools = self._setup_tools()
        with open("./modules/neuranlp_agent/prompts/base_prompt.txt") as f:
            prompt_template = f.read() + "\n\nTools: {tools}\n\n{input}\n\n{agent_scratchpad}"

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={"tools": str([tool.name for tool in self.tools])}
        )
        agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def _initialize_llms(self):
        """Initializes Gemini and Ollama models with a fallback mechanism."""
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=config.GEMINI_API_KEY)
            logging.info("Using Gemini Pro.")
            return llm
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini, falling back to Ollama: {e}")
            llm = Ollama(base_url=config.OLLAMA_BASE_URL, model=config.OLLAMA_MODEL)
            logging.info(f"Using Ollama with model {config.OLLAMA_MODEL}.")
            return llm

    def _setup_tools(self):
        """Sets up the tools available to the agent."""
        tools = [
            Tool(
                name="SearchMemory",
                func=memory_handler.retrieve_memory,
                description="Search through past conversations and documents for relevant information."
            ),
            Tool(
                name="CallSecurity",
                func=api_triggers.call_security,
                description="Dispatches security to a specified location in case of an emergency."
            ),
            Tool(
                name="SendCampusAnnouncement",
                func=api_triggers.send_announcement,
                description="Sends a campus-wide announcement. Requires admin authorization."
            ),
            Tool(
                name="NotifyDepartmentAdmin",
                func=lambda args: api_triggers.notify_admin(*args.split(',')),
                description="Sends a notification to a specific department's admin. Input should be a comma-separated string of department and message."
            )
        ]
        return tools

    def run_query(self, query: str):
        """Processes a query through the agent."""
        try:
            response = self.agent_executor.invoke({"input": query})
            memory_handler.store_interaction(query, response['output'])
            return {"response": response['output'], "source": "gemini" if isinstance(self.llm, ChatGoogleGenerativeAI) else "ollama"}
        except Exception as e:
            logging.error(f"Error running agent query: {e}")
            return {"response": "I'm sorry, I encountered an error. Please try again.", "source": "error"}

agent_core = AgentCore()