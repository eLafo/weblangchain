from typing import Sequence
from operator import itemgetter

from langchain.schema import Document
from langchain.schema.document import Document
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.retriever import BaseRetriever
from langchain.schema.runnable import (Runnable, RunnableBranch,
                                       RunnableLambda, RunnableMap)
from langchain.schema.output_parser import StrOutputParser
from prompts import rephrase_template, chat_prompt_template
from models import ChatRequest

def create_retriever_chain(
    llm: BaseLanguageModel, retriever: BaseRetriever
) -> Runnable:
    CONDENSE_QUESTION_PROMPT = rephrase_template
    condense_question_chain = (
        CONDENSE_QUESTION_PROMPT | llm | StrOutputParser()
    ).with_config(
        run_name="CondenseQuestion",
    )
    conversation_chain = condense_question_chain | retriever
    return RunnableBranch(
        (
            RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
                run_name="HasChatHistoryCheck"
            ),
            conversation_chain.with_config(run_name="RetrievalChainWithHistory"),
        ),
        (
            RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            )
            | retriever
        ).with_config(run_name="RetrievalChainWithNoHistory"),
    ).with_config(run_name="RouteDependingOnChatHistory")

def serialize_history(request: ChatRequest):
    chat_history = request["chat_history"] or []
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))
    return converted_chat_history


def format_docs(docs: Sequence[Document]) -> str:
    formatted_docs = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{i}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)

def create_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
) -> Runnable:
    retriever_chain = create_retriever_chain(llm, retriever) | RunnableLambda(
        format_docs
    ).with_config(run_name="FormatDocumentChunks")
    _context = RunnableMap(
        {
            "context": retriever_chain.with_config(run_name="RetrievalChain"),
            "question": RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            ),
            "chat_history": RunnableLambda(itemgetter("chat_history")).with_config(
                run_name="Itemgetter:chat_history"
            ),
        }
    )

    response_synthesizer = (chat_prompt_template | llm | StrOutputParser()).with_config(
        run_name="GenerateResponse",
    )
    return (
        {
            "question": RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            ),
            "chat_history": RunnableLambda(serialize_history).with_config(
                run_name="SerializeHistory"
            ),
        }
        | _context
        | response_synthesizer
    )
