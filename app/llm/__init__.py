from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    # model="gpt-4",
    streaming=True,
    temperature=0,
)
