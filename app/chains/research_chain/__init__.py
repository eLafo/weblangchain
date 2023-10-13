import os
from operator import itemgetter
from typing import Sequence

from langchain.prompts import load_prompt
from langchain.schema import Document
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough, RunnableMap
from ...llm import llm
from ...retrievers import contextual_compression_retriever

system_prompt = load_prompt(os.path.dirname(__file__) + "/system_prompt.yaml")

def _format_docs(docs: Sequence[Document]) -> str:
    formatted_docs = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{i}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)

chain = {
    "question": RunnablePassthrough()
} | RunnableMap(
    question = RunnableLambda(itemgetter("question")),
    context=(RunnableLambda(itemgetter("question")) | contextual_compression_retriever | _format_docs)
) | (system_prompt | llm | StrOutputParser())
