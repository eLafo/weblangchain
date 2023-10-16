from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableBranch, RunnableMap
from langchain.schema.output_parser import StrOutputParser
from langchain.agents import AgentExecutor
from app.llm import llm
from app.chains import classify, research, rephrase_input
from app.models import Topic

tools = []
memory = ConversationBufferMemory(memory_key="chat_history")
topics = [
    Topic(name="research",
          description="Questions about some topic that would benefit from some kind of research")
]

_route = RunnablePassthrough.assign(topics=lambda inputs: topics) | RunnablePassthrough.assign(topic=classify) | RunnableBranch(
    (lambda x: "research" in x["topic"].lower(),
     RunnableLambda(lambda x: x["input"]) | research),
    (llm | StrOutputParser)
)

agent = {
    "input": RunnablePassthrough(),
    "memory": lambda x: memory,
    "chat_history": (RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history")),
} | RunnablePassthrough.assign(original_input=lambda x: x["input"], input=rephrase_input) | RunnablePassthrough.assign(output=_route) | RunnablePassthrough.assign(memory=lambda x: x["memory"].save_context({"input": x["original_input"]}, {"output": x["output"]}))
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True)
