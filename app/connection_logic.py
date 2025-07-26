"""
MongoDB Data Store for Seraface AI Server

Professional MongoDB storage layer for multi-phase skincare AI pipeline.
Stores phase data across 4 collections with automatic expiration and cleanup.

Collections:
- skincare_phase1_data: Form analysis data
- skincare_phase2_data: Image analysis results  
- skincare_phase3_data: Product recommendations
- skincare_phase4_data: Generated routines
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from .core.database import Database


class DataStore:
    """MongoDB storage handler for skincare AI pipeline data"""
    
    def __init__(self):
        pass  
    
    def _get_database(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance"""
        return Database.get_database()
    
    def _get_collection_name(self, phase: str) -> str:
        """Get MongoDB collection name for a specific phase"""
        return f"skincare_{phase}_data"
    
    async def save_phase_data(self, session_id: str, phase: str, data: Dict[Any, Any]) -> bool:
        """Save phase data to MongoDB collection"""
        try:
            db = self._get_database()
            collection = db[self._get_collection_name(phase)]
            
            document = {
                "_id": session_id,
                "session_id": session_id,
                "phase": phase,
                "timestamp": datetime.utcnow(),
                "data": data,
                "expires_at": datetime.utcnow() + timedelta(days=90),
                "version": "1.0"
            }
            
            await collection.replace_one({"_id": session_id}, document, upsert=True)
            print(f"✅ Saved {phase} data for session {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving {phase} data: {e}")
            return False
    
    async def load_phase_data(self, session_id: str, phase: str) -> Optional[Dict[Any, Any]]:
        """Load phase data from MongoDB collection"""
        try:
            db = self._get_database()
            collection = db[self._get_collection_name(phase)]
            
            document = await collection.find_one({"_id": session_id})
            if not document:
                return None

            if document.get("expires_at") and document["expires_at"] < datetime.utcnow():
                await collection.delete_one({"_id": session_id})
                return None
            
            return document.get("data")
            
        except Exception as e:
            print(f"❌ Error loading {phase} data: {e}")
            return None
    
    def create_session(self) -> str:
        """Create a new session ID"""
        return str(uuid.uuid4())
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if session has any data in MongoDB"""
        try:
            db = self._get_database()
            for phase in ["phase1", "phase2", "phase3", "phase4"]:
                collection = db[self._get_collection_name(phase)]
                if await collection.find_one({"_id": session_id}):
                    return True
            return False
        except Exception as e:
            print(f"❌ Error checking session existence: {e}")
            return False
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive status of session and all phases"""
        try:
            db = self._get_database()
            phases = ["phase1", "phase2", "phase3", "phase4"]
            phase_status = {}
            
            for phase in phases:
                collection = db[self._get_collection_name(phase)]
                document = await collection.find_one({"_id": session_id})
                phase_status[phase] = document is not None
            
            completed_count = sum(1 for status in phase_status.values() if status)
            progress_percentage = (completed_count / len(phases)) * 100
            
            return {
                "session_id": session_id,
                "exists": completed_count > 0,
                "phases": phase_status,
                "completed_phases_count": completed_count,
                "total_phases": len(phases),
                "progress_percentage": progress_percentage
            }
            
        except Exception as e:
            print(f"❌ Error getting session status: {e}")
            return {
                "session_id": session_id,
                "exists": False,
                "phases": {"phase1": False, "phase2": False, "phase3": False, "phase4": False},
                "error": str(e)
            }
    
    def create_session(self) -> str:
        """Create a new session ID"""
        return str(uuid.uuid4())
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete all session data from MongoDB collections"""
        try:
            db = self._get_database()
            deleted_phases = []
            total_deleted = 0
            
            for phase in ["phase1", "phase2", "phase3", "phase4"]:
                collection = db[self._get_collection_name(phase)]
                result = await collection.delete_one({"_id": session_id})
                if result.deleted_count > 0:
                    deleted_phases.append(phase)
                    total_deleted += result.deleted_count
            
            return {
                "session_id": session_id,
                "deleted_phases": deleted_phases,
                "total_deleted": total_deleted,
                "success": total_deleted > 0
            }
            
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            return {"session_id": session_id, "success": False, "error": str(e)}
    
    async def get_all_sessions(self) -> Dict[str, Any]:
        """Get summary of all sessions from MongoDB"""
        try:
            db = self._get_database()
            session_ids = set()
        
            for phase in ["phase1", "phase2", "phase3", "phase4"]:
                collection = db[self._get_collection_name(phase)]
                async for document in collection.find({}, {"_id": 1}):
                    session_ids.add(document["_id"])
            
            all_sessions = {}
            for session_id in session_ids:
                status = await self.get_session_status(session_id)
                all_sessions[session_id] = status
            
            return {
                "total_sessions": len(all_sessions),
                "sessions": all_sessions
            }
            
        except Exception as e:
            print(f"❌ Error getting all sessions: {e}")
            return {"total_sessions": 0, "sessions": {}, "error": str(e)}
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """Clean up expired sessions from MongoDB collections"""
        try:
            db = self._get_database()
            cleanup_results = {}
            total_deleted = 0
            current_time = datetime.utcnow()
            
            for phase in ["phase1", "phase2", "phase3", "phase4"]:
                collection = db[self._get_collection_name(phase)]
                result = await collection.delete_many({
                    "expires_at": {"$lt": current_time}
                })
                cleanup_results[phase] = result.deleted_count
                total_deleted += result.deleted_count
            
            return {
                "total_deleted": total_deleted,
                "by_phase": cleanup_results,
                "cleanup_time": current_time.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return {"total_deleted": 0, "error": str(e)}


data_store = DataStore()
