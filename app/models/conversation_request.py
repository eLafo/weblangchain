from pydantic import BaseModel

class ConversationRequest(BaseModel):
    input: str
    conversation_id: str
