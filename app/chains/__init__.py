from .researcher_chain import create_researcher_chain
from .rephrase_input_chain import chain as rephrase_input
from .research_chain import chain as research
from .classify_chain import chain as classify
from ..llm import llm
from ..retrievers import contextual_compression_retriever

researcher = create_researcher_chain(llm=llm, retriever=contextual_compression_retriever)