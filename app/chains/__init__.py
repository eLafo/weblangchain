from .researcher_chain import create_researcher_chain
from ..llm import llm
from ..retrievers import contextual_compression_retriever

researcher = create_researcher_chain(llm=llm, retriever=contextual_compression_retriever)