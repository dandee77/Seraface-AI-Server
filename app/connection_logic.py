import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class DataStore:
    """Handles JSON file storage for phase data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def _get_file_path(self, session_id: str, phase: str) -> Path:
        """Get file path for a specific session and phase"""
        return self.data_dir / f"{session_id}_{phase}.json"
    
    def save_phase_data(self, session_id: str, phase: str, data: Dict[Any, Any]) -> bool:
        """Save phase data to JSON file"""
        try:
            file_path = self._get_file_path(session_id, phase)
            
            # Add metadata
            save_data = {
                "session_id": session_id,
                "phase": phase,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"❌ Error saving {phase} data: {e}")
            return False
    
    def get_phase_data(self, session_id: str, phase: str) -> Optional[Dict[Any, Any]]:
        """Get phase data from JSON file (alias for load_phase_data)"""
        return self.load_phase_data(session_id, phase)
    
    def load_phase_data(self, session_id: str, phase: str) -> Optional[Dict[Any, Any]]:
        """Load phase data from JSON file"""
        try:
            file_path = self._get_file_path(session_id, phase)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            
            return saved_data.get("data")
        except Exception as e:
            print(f"❌ Error loading {phase} data: {e}")
            return None
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session has any data"""
        phase1_file = self._get_file_path(session_id, "phase1")
        return phase1_file.exists()
    
    def get_session_status(self, session_id: str) -> Dict[str, bool]:
        """Get completion status of all phases for a session"""
        phases = ["phase1", "phase2", "phase3", "phase4"]
        status = {}
        
        for phase in phases:
            file_path = self._get_file_path(session_id, phase)
            status[phase] = file_path.exists()
        
        return status
    
    def create_session(self) -> str:
        """Create a new session ID"""
        return str(uuid.uuid4())


# Global instance
data_store = DataStore()
