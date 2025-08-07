from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, create_react_agent
# Import the required types for safety settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .utils import config, api_triggers
from .memory.memory_handler import memory_handler
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

MANUAL_REACT_PROMPT_TEMPLATE = """
{base_prompt}

You have access to the following tools:

{tools}

Use the following format to answer the question:

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
Thought:{agent_scratchpad}
"""

class AgentCore:
    def __init__(self):
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
            # THE FIX IS HERE 👇: Add safety settings to prevent the API from blocking emergency-related queries.
            safety_settings = {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", 
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
            Tool(name="SearchMemory", func=memory_handler.retrieve_memory, description="Use this tool to find information about the campus, events, faculty, or past conversations. It is the primary source of knowledge."),
            Tool(name="CallSecurity", func=api_triggers.call_security, description="Use this tool to dispatch security to a specified location in case of an emergency. Input should be the location as a string."),
            Tool(name="SendCampusAnnouncement", func=api_triggers.send_announcement, description="Use this tool to send a campus-wide announcement. This is for major alerts and requires authorization. Input should be the message as a string."),
            Tool(name="NotifyDepartmentAdmin", func=lambda input_str: api_triggers.notify_admin(department=input_str.split(',')[0].strip(), message=''.join(input_str.split(',')[1:]).strip()), description="Use this tool to send a notification to a specific department's admin. The input must be a comma-separated string of two values: the target department and the message. Example: 'IT, The Wi-Fi in the main auditorium is down.'")
        ]
        return tools

    def run_query(self, query: str):
        """Processes a query through the agent."""
        try:
            response = self.agent_executor.invoke({"input": query})
            memory_handler.store_interaction(query, response['output'])
            return {"response": response['output'], "source": self.source}
        except Exception as e:
            logging.error(f"Error running agent query: {e}")
            return {"response": "I'm sorry, I encountered an error and couldn't process your request.", "source": "error"}

agent_core = AgentCore()