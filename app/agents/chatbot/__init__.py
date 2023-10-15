from langchain.agents import tool
from operator import itemgetter
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.tools.render import render_text_description
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableMap, RunnableParallel
from langchain import hub
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from app.llm import llm
from app.chains import research_chain
from app.chains.research_chain.rephrase_question_chain import chain as rephrase_question_chain

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = RunnableMap(
    question = RunnablePassthrough(),
    chat_history = (RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history"))
) | RunnableMap(
    output=(rephrase_question_chain | research_chain),
    input=RunnableLambda(itemgetter("question"))
) | RunnableParallel(
    memory = RunnableLambda(lambda x: memory.save_context({"input": x["input"]}, {"output": x["output"]})),
    output = itemgetter("output")
) | RunnableLambda(lambda x: x["output"])