from pydantic import BaseModel, Field

class Topic(BaseModel):
    name: str = Field(description="The name of the topic")
    description: str = Field(description="The description of the topic")
    
    def to_xml(self):
        return f"""
        <topic>
            <name>{self.name}</name>
            <description>{self.description}</description>
        </topic>
        """
