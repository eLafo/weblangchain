import os
from langchain.prompts import load_prompt as load_prompt, ChatPromptTemplate, MessagesPlaceholder

def _prompts_dir():
    return os.path.dirname(__file__)

def _load_prompt(relative_path):
    return load_prompt(f"{_prompts_dir()}/{relative_path}")

response_template = _load_prompt("response_template.yaml")
rephrase_template = _load_prompt("rephrase_template.yaml")
chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", response_template.template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
