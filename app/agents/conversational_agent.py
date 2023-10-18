from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableBranch, RunnableMap
from langchain.schema.output_parser import StrOutputParser
from langchain.agents import AgentExecutor
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from app.llm import llm
from app.chains import classify, research, rephrase_input
from app.models import Topic
from lib.chamber_py import Chamber
from langchain.vectorstores.pgvector import PGVector

topics = [
    Topic(name="research",
          description="Questions about some topic that would benefit from some kind of research")
]

_route = RunnablePassthrough.assign(topics=lambda inputs: topics) | RunnablePassthrough.assign(topic=classify) | RunnableBranch(
    (lambda x: "research" in x["topic"].lower(),
    research),
    (RunnableLambda(lambda x: x["input"]) | llm | StrOutputParser())
)

def create_memory(conversation_id):
    db_settings = {k: Chamber()["database"][k] for k in ('user', 'host', 'password', 'port', 'database')}

    CONNECTION_STRING = PGVector.connection_string_from_db_params(**Chamber()["pgvector"], **db_settings)
    vectorstore = PGVector(
        collection_name=conversation_id,
        connection_string=CONNECTION_STRING,
        embedding_function=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    memory = VectorStoreRetrieverMemory(retriever=retriever)
    
    return memory

agent = {
    "input": lambda x: x["input"],
    "conversation_id": lambda x: x["conversation_id"]
} | RunnablePassthrough.assign(
        memory = RunnableLambda(lambda x: create_memory(x["conversation_id"]))
) | RunnablePassthrough.assign(
        chat_history = RunnableLambda(lambda x: x["memory"].load_memory_variables({"prompt": x["input"]}))
) | RunnablePassthrough.assign(
        original_input=lambda x: x["input"], input=rephrase_input
) | RunnablePassthrough.assign(
        output=_route
) | RunnablePassthrough.assign(
        memory=lambda x: x["memory"].save_context({"input": x["original_input"]}, {"output": x["output"]})
)
