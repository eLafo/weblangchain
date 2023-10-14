from langchain.agents import tool
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain import hub

from app.llm import llm
from app.chains import research_chain

@tool(return_direct=True)
def perform_research(question: str):
    """Performs a research. Use this tool when you need to answer questions about topics"""
    return research_chain.invoke(question)
    
tools = [
    perform_research
]


prompt = hub.pull("hwchase17/react-chat")

prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)

llm_with_stop = llm.bind(stop=["\nObservation"])

agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_log_to_str(x['intermediate_steps']),
    "chat_history": lambda x: x["chat_history"]
} | prompt | llm_with_stop | ReActSingleInputOutputParser()

from langchain.agents import AgentExecutor

memory = ConversationBufferMemory(memory_key="chat_history")
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True)