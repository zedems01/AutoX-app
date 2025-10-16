"""
Metrics Manager for AutoX workflow monitoring.

This module provides a centralized way to manage metrics with proper state tracking
to prevent negative values and race conditions.
"""

from threading import Lock
from typing import Set, Dict
import time
import atexit
from .metrics import ACTIVE_WORKFLOWS, ACTIVE_WEBSOCKETS


class MetricsManager:
    """
    Manages metrics state to prevent negative values and race conditions.
    """
    
    def __init__(self):
        self._lock = Lock()
        self._active_workflows: Set[str] = set()
        self._active_websockets: Set[str] = set()
        self._workflow_start_times: Dict[str, float] = {}
        
        # Register cleanup on application exit
        atexit.register(self.cleanup_all_metrics)
    
    def start_workflow(self, thread_id: str) -> bool:
        """
        Start tracking a workflow. Returns True if workflow was newly started,
        False if it was already active.
        """
        with self._lock:
            if thread_id in self._active_workflows:
                # Workflow already exists, don't increment again
                return False
            
            self._active_workflows.add(thread_id)
            self._workflow_start_times[thread_id] = time.time()
            ACTIVE_WORKFLOWS.inc()
            return True
    
    def stop_workflow(self, thread_id: str) -> bool:
        """
        Stop tracking a workflow. Returns True if workflow was active and stopped,
        False if it wasn't active.
        """
        with self._lock:
            if thread_id not in self._active_workflows:
                # Workflow not active, don't decrement
                return False
            
            self._active_workflows.discard(thread_id)
            self._workflow_start_times.pop(thread_id, None)
            
            # Only decrement if we have active workflows to prevent negative values
            if ACTIVE_WORKFLOWS._value._value > 0:
                ACTIVE_WORKFLOWS.dec()
            return True
    
    def start_websocket(self, thread_id: str) -> bool:
        """
        Start tracking a WebSocket connection. Returns True if WebSocket was newly started.
        """
        with self._lock:
            # Use thread_id as unique identifier for WebSocket
            if thread_id in self._active_websockets:
                return False
            
            self._active_websockets.add(thread_id)
            ACTIVE_WEBSOCKETS.inc()
            return True
    
    def stop_websocket(self, thread_id: str) -> bool:
        """
        Stop tracking a WebSocket connection. Returns True if WebSocket was active.
        """
        with self._lock:
            if thread_id not in self._active_websockets:
                return False
            
            self._active_websockets.discard(thread_id)
            
            # Only decrement if we have active websockets to prevent negative values
            if ACTIVE_WEBSOCKETS._value._value > 0:
                ACTIVE_WEBSOCKETS.dec()
            return True
    
    def is_workflow_active(self, thread_id: str) -> bool:
        """Check if a workflow is currently active."""
        with self._lock:
            return thread_id in self._active_workflows
    
    def is_websocket_active(self, thread_id: str) -> bool:
        """Check if a WebSocket is currently active."""
        with self._lock:
            return thread_id in self._active_websockets
    
    def get_active_workflows_count(self) -> int:
        """Get the number of active workflows."""
        with self._lock:
            return len(self._active_workflows)
    
    def get_active_websockets_count(self) -> int:
        """Get the number of active WebSockets."""
        with self._lock:
            return len(self._active_websockets)
    
    def cleanup_all_metrics(self):
        """
        Clean up all metrics on application shutdown.
        This prevents stale metrics when the application restarts.
        """
        with self._lock:
            # Reset all active workflows
            for thread_id in list(self._active_workflows):
                self.stop_workflow(thread_id)
            
            # Reset all active websockets
            for thread_id in list(self._active_websockets):
                self.stop_websocket(thread_id)
    
    def reset_metrics(self):
        """
        Force reset all metrics to zero.
        Useful for testing or recovery from inconsistent state.
        """
        with self._lock:
            # Clear tracking sets
            self._active_workflows.clear()
            self._active_websockets.clear()
            self._workflow_start_times.clear()
            
            # Reset gauges to zero
            ACTIVE_WORKFLOWS.set(0)
            ACTIVE_WEBSOCKETS.set(0)
    
    def get_workflow_runtime(self, thread_id: str) -> float:
        """Get the runtime of a workflow in seconds."""
        with self._lock:
            if thread_id not in self._workflow_start_times:
                return 0.0
            return time.time() - self._workflow_start_times[thread_id]
    
    def get_stale_workflows(self, max_age_seconds: int = 3600) -> Set[str]:
        """
        Get workflows that have been active for longer than max_age_seconds.
        Useful for cleanup of stale workflows.
        """
        with self._lock:
            current_time = time.time()
            stale_workflows = set()
            
            for thread_id, start_time in self._workflow_start_times.items():
                if current_time - start_time > max_age_seconds:
                    stale_workflows.add(thread_id)
            
            return stale_workflows


# Global instance
metrics_manager = MetricsManager()
