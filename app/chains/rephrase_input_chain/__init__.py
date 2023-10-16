import os
from operator import itemgetter
from langchain.prompts import load_prompt
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnableLambda

from app.llm import llm

prompt = load_prompt(os.path.dirname(__file__) + "/rephrase_input_prompt.yaml")

branch_chain = RunnableBranch(
    (
        lambda x: bool(x.get("chat_history")),
        ( prompt | llm | StrOutputParser()).with_config(run_name="SummarizeQuestionAndHistoryChat")
    ),
    (
        RunnableLambda(itemgetter("input")).with_config(run_name="ReturnRawQuestion")
    )
).with_config(run_name="BranchDependingOnChatHistory")

chain = {
    "input": RunnableLambda(itemgetter("input")),
    "chat_history": (RunnableLambda(itemgetter("chat_history")))
} | branch_chain | StrOutputParser()