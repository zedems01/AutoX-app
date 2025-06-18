import json
from pydantic import BaseModel
from pathlib import Path
from enum import Enum
from langgraph.types import Send


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Send):
            return obj._asdict()
        return json.JSONEncoder.default(self, obj) 