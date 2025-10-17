"""
Persistent task tracking to avoid duplicates even after restart.
"""
import json
import os
from typing import Set
from pathlib import Path


class TaskTracker:
    """Track processed tasks persistently."""
    
    def __init__(self, filepath: str = "processed_tasks.json"):
        """
        Initialize task tracker.
        
        Args:
            filepath: Path to JSON file for storing processed tasks
        """
        self.filepath = filepath
        self.tasks = self._load()
    
    def _load(self) -> Set[str]:
        """Load processed tasks from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
                    return set()
            except Exception as e:
                print(f"Warning: Could not load task tracker: {e}")
                return set()
        return set()
    
    def _save(self):
        """Save processed tasks to file."""
        try:
            # Ensure directory exists
            Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.filepath, 'w') as f:
                json.dump(list(self.tasks), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save task tracker: {e}")
    
    def is_processed(self, task_key: str) -> bool:
        """
        Check if task was already processed.
        
        Args:
            task_key: Unique task identifier (task-round-nonce)
            
        Returns:
            True if task was already processed
        """
        return task_key in self.tasks
    
    def mark_processed(self, task_key: str):
        """
        Mark task as processed.
        
        Args:
            task_key: Unique task identifier (task-round-nonce)
        """
        self.tasks.add(task_key)
        self._save()
    
    def get_all(self) -> Set[str]:
        """Get all processed task keys."""
        return self.tasks.copy()
    
    def get_processed_tasks(self) -> list:
        """Get all processed task keys as a sorted list."""
        return sorted(list(self.tasks))
    
    def clear(self):
        """Clear all processed tasks (use with caution)."""
        self.tasks = set()
        self._save()
    
    def count(self) -> int:
        """Get count of processed tasks."""
        return len(self.tasks)
