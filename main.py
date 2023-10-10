"""Main entrypoint for the app."""
from langchain.chat_models import ChatOpenAI

# Backup
from langserve import add_routes
from models import ChatRequest
from prompts import rephrase_template
from api import api as app
from retrievers import contextual_compression_retriever

# dotenv
from dotenv import load_dotenv
from chains import create_chain

load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    # model="gpt-4",
    streaming=True,
    temperature=0,
)

chain = create_chain(llm, contextual_compression_retriever)

add_routes(app, chain, path="/chat", input_type=ChatRequest)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
