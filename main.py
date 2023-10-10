"""Main entrypoint for the app."""
from app import api

# dotenv
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, host="0.0.0.0", port=8080)
