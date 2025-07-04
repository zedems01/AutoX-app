import json
from pydantic import BaseModel
from pathlib import Path
from enum import Enum


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle models and objects during websocket communication"""
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj) 