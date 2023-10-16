from .researcher_chain import create_researcher_chain
from .rephrase_question_chain import chain as rephrase_question
from .research_chain import chain as research
from .classification_chain import chain as classification
from ..llm import llm
from ..retrievers import contextual_compression_retriever

researcher = create_researcher_chain(llm=llm, retriever=contextual_compression_retriever)