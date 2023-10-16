import os
from typing import List
from langchain.prompts import load_prompt
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from app.models import Topic

from app.llm import llm

def _format_topics(topics: List[Topic]):
    return "\n".join(topic.to_xml() for topic in topics)

prompt = load_prompt(os.path.dirname(__file__) + "/classify_chain_prompt.yaml")
chain = {
            "input": lambda x: x["input"],
            "topics": lambda x: _format_topics(x["topics"])
        } | (prompt | llm) | StrOutputParser()