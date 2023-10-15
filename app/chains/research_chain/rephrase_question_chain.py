import os
from typing import List
from operator import itemgetter
from langchain.prompts import load_prompt
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnableLambda
from langchain.schema import HumanMessage, AIMessage, ChatMessage

from app.llm import llm

def _serialize_history(chat_history: List[ChatMessage]):
    print("serializing")
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(
                HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))
    print(f"serialized: {converted_chat_history}")
    return converted_chat_history

prompt = load_prompt(os.path.dirname(__file__) + "/rephrase_question_prompt.yaml")

branch_chain = RunnableBranch(
    (
        lambda x: bool(x.get("chat_history")),
        ( prompt | llm | StrOutputParser()).with_config(run_name="SummarizeQuestionAndHistoryChat")
    ),
    (
        RunnableLambda(itemgetter("question")).with_config(run_name="ReturnRawQuestion")
    )
).with_config(run_name="BranchDependingOnChatHistory")

chain = {
    "question": RunnableLambda(itemgetter("question")),
    "chat_history": (RunnableLambda(itemgetter("chat_history")) | _serialize_history)
} | branch_chain | StrOutputParser