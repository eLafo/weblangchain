"""Main entrypoint for the app."""

# Backup
from langserve import add_routes
from app import api
from app.models import ChatRequest
from app.retrievers import contextual_compression_retriever
from app.chains import create_chain
from app.llm import llm

# dotenv
from dotenv import load_dotenv

load_dotenv()

chain = create_chain(llm, contextual_compression_retriever)

add_routes(api, chain, path="/chat", input_type=ChatRequest)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, host="0.0.0.0", port=8080)
