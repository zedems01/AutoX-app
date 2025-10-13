"""Tests for custom JSON encoder."""
import pytest
import json
from datetime import datetime
from pydantic import BaseModel
from backend.app.utils.json_encoder import CustomJSONEncoder
from backend.app.utils.schemas import Trend, TweetAuthor


class TestCustomJSONEncoder:
    """Tests for CustomJSONEncoder."""

    def test_encode_pydantic_model(self):
        """Test encoding Pydantic model."""
        trend = Trend(name="Python", rank=1, tweet_count="10K")
        encoded = json.dumps(trend, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["name"] == "Python"
        assert decoded["rank"] == 1
        assert decoded["tweet_count"] == "10K"

    def test_encode_nested_pydantic_model(self):
        """Test encoding nested Pydantic models."""
        from backend.app.utils.schemas import TweetSearched
        
        author = TweetAuthor(userName="testuser", name="Test User")
        tweet = TweetSearched(
            text="Test tweet",
            retweetCount=5,
            replyCount=2,
            likeCount=10,
            viewCount=50,
            createdAt="2025-01-01",
            author=author
        )
        
        encoded = json.dumps(tweet, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["text"] == "Test tweet"
        assert decoded["author"]["userName"] == "testuser"

    def test_encode_datetime(self):
        """Test encoding datetime objects."""
        dt = datetime(2025, 1, 1, 12, 0, 0)
        encoded = json.dumps({"timestamp": dt}, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert "2025-01-01" in decoded["timestamp"]
        assert "12:00:00" in decoded["timestamp"]

    def test_encode_list_of_pydantic_models(self):
        """Test encoding list of Pydantic models."""
        trends = [
            Trend(name="Python", tweet_count="10K", rank=1),
            Trend(name="FastAPI", tweet_count="8K", rank=2),
            Trend(name="AI", tweet_count="6K", rank=3)
        ]
        
        encoded = json.dumps(trends, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert len(decoded) == 3
        assert decoded[0]["name"] == "Python"
        assert decoded[1]["name"] == "FastAPI"

    def test_encode_dict_with_pydantic_values(self):
        """Test encoding dictionary with Pydantic model values."""
        trend = Trend(name="Python", tweet_count="10K", rank=1)
        data = {
            "topic": trend,
            "count": 100,
            "active": True
        }
        
        encoded = json.dumps(data, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["topic"]["name"] == "Python"
        assert decoded["count"] == 100
        assert decoded["active"] is True

    def test_encode_standard_types(self):
        """Test encoding standard Python types."""
        data = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        encoded = json.dumps(data, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["string"] == "hello"
        assert decoded["integer"] == 42
        assert decoded["float"] == 3.14
        assert decoded["boolean"] is True
        assert decoded["null"] is None
        assert decoded["list"] == [1, 2, 3]
        assert decoded["dict"]["nested"] == "value"

    def test_encode_mixed_data(self):
        """Test encoding mixed data with Pydantic models and standard types."""
        trend = Trend(name="Python", tweet_count="10K", rank=1)
        dt = datetime(2025, 1, 1, 12, 0, 0)
        
        data = {
            "trend": trend,
            "timestamp": dt,
            "count": 100,
            "tags": ["python", "coding"],
            "metadata": {
                "author": "system",
                "version": "1.0"
            }
        }
        
        encoded = json.dumps(data, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["trend"]["name"] == "Python"
        assert "2025-01-01" in decoded["timestamp"]
        assert decoded["count"] == 100
        assert len(decoded["tags"]) == 2
        assert decoded["metadata"]["author"] == "system"

    def test_encode_empty_structures(self):
        """Test encoding empty structures."""
        data = {
            "empty_list": [],
            "empty_dict": {},
            "empty_string": ""
        }
        
        encoded = json.dumps(data, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["empty_list"] == []
        assert decoded["empty_dict"] == {}
        assert decoded["empty_string"] == ""

    def test_encoder_with_complex_nested_structure(self):
        """Test encoder with complex nested structure."""
        trends = [
            Trend(name="Python", tweet_count="10K", rank=1),
            Trend(name="AI", tweet_count="8K", rank=2)
        ]
        
        complex_data = {
            "workflow": {
                "id": "workflow_123",
                "trends": trends,
                "metadata": {
                    "created_at": datetime(2025, 1, 1),
                    "status": "active",
                    "counts": {
                        "total": 100,
                        "processed": 50
                    }
                }
            },
            "results": []
        }
        
        encoded = json.dumps(complex_data, cls=CustomJSONEncoder)
        decoded = json.loads(encoded)
        
        assert decoded["workflow"]["id"] == "workflow_123"
        assert len(decoded["workflow"]["trends"]) == 2
        assert decoded["workflow"]["trends"][0]["name"] == "Python"
        assert "2025-01-01" in decoded["workflow"]["metadata"]["created_at"]
        assert decoded["workflow"]["metadata"]["counts"]["total"] == 100

