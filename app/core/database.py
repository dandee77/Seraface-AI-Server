from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings


class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    def connect(cls):
        """Connect to MongoDB using settings from config"""
        cls.client = AsyncIOMotorClient(settings.MONGO_URI)
    
    @classmethod
    def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
    
    @classmethod
    def get_database(cls):
        """Get the database instance"""
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    def get_products_collection(cls):
        """Get the products collection"""
        db = cls.get_database()
        return db[settings.PRODUCTS_COLLECTION]


# For backward compatibility (if needed)
DatabaseConfig = settings
