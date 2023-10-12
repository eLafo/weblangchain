from ..prompts import rephrase_template
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.runnable import Runnable

def create_condense_question_chain(llm: BaseLanguageModel) -> Runnable:
    return (rephrase_template | llm | StrOutputParser())

