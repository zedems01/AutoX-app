from pydantic import BaseModel, Field
from typing import List



class TrendsAnalysisResponse(BaseModel):
    "Schema for the trends analyst response."
    trend_choice: str = Field(description="The topic choice of the viral checker agent.")
    justification: str = Field(description="The justification for the topic choice.")