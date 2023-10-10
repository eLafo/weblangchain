"""Main entrypoint for the app."""
# dotenv
from dotenv import load_dotenv

load_dotenv()

from app import api

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, host="0.0.0.0", port=8080)
