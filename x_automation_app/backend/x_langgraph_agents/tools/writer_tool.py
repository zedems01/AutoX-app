from pydantic import BaseModel, Field
from typing import List



class WriterResponse(BaseModel):
    "Schema for the writer agent response."
    tweet: str = Field(description="The tweet written by the agent.")