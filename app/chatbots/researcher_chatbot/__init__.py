from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableMap, RunnableParallel

from app.chains import research_chain
from app.chains.research_chain.rephrase_question_chain import chain as rephrase_question_chain

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
researcher_chatbot = RunnableMap(
    question = RunnablePassthrough(),
    chat_history = (RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history"))
) | RunnableMap(
    output=(rephrase_question_chain | research_chain),
    input=RunnableLambda(itemgetter("question"))
) | RunnableParallel(
    memory = RunnableLambda(lambda x: memory.save_context({"input": x["input"]}, {"output": x["output"]})),
    output = itemgetter("output")
) | RunnableLambda(lambda x: x["output"])