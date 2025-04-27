"""
Base management operations and business logic
"""
from sqlalchemy.orm import Session, Query, joinedload
from typing import Type, Optional, List, Any, Dict, Union
from app.db import models
from app.db.database import db
import logging

logger = logging.getLogger(__name__)

class BaseManager:
    """Base manager class for handling common CRUD operations"""
    
    def __init__(self, model_class: Type[Any], db_session: Optional[Session] = None):
        self._db = db_session or db.get_session()
        self.model_class = model_class

    def get_query(self) -> Query:
        """Get a base query object for the model"""
        return self._db.query(self.model_class)

    def get(self, id: Any) -> Optional[Any]:
        """Get a record by ID"""
        try:
            return self._db.query(self.model_class).filter(self.model_class.id == id).first()
        except Exception as e:
            logger.error(f"Error getting record: {str(e)}")
            return None

    def get_multi(self, skip: int = 0, limit: int = 100) -> Union[Query, List[Any]]:
        """Get multiple records with pagination"""
        try:
            return self._db.query(self.model_class).offset(skip).limit(limit)
        except Exception as e:
            logger.error(f"Error getting records: {str(e)}")
            return []

    def get_multi_with_relationships(self, *relationships: str) -> Query:
        """Get multiple records with eager loading of relationships"""
        try:
            query = self.get_query()
            for relationship in relationships:
                query = query.options(joinedload(getattr(self.model_class, relationship)))
            return query
        except Exception as e:
            logger.error(f"Error getting records with relationships: {str(e)}")
            return self.get_query()

    def create(self, obj_in: Dict[str, Any]) -> Optional[Any]:
        """Create a new record"""
        try:
            db_obj = self.model_class(**obj_in)
            self._db.add(db_obj)
            self._db.commit()
            self._db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating record: {str(e)}")
            return None

    def update(self, db_obj: Any, obj_in: Dict[str, Any]) -> Optional[Any]:
        """Update a record"""
        try:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            self._db.commit()
            self._db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating record: {str(e)}")
            return None

    def delete(self, id: Any) -> bool:
        """Delete a record"""
        try:
            obj = self.get(id)
            if not obj:
                return False
            self._db.delete(obj)
            self._db.commit()
            return True
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting record: {str(e)}")
            return False

    def get_by_field(self, field: str, value: Any) -> Optional[Any]:
        """Get a record by field value"""
        try:
            logger.debug(f"Attempting to get record by field '{field}' with value '{value}'")
            result = self._db.query(self.model_class).filter(getattr(self.model_class, field) == value).first()
            if result:
                logger.debug(f"Successfully found record with {field}={value}")
            else:
                logger.debug(f"No record found with {field}={value}")
            return result
        except Exception as e:
            logger.error(f"Error getting record by field '{field}' with value '{value}': {str(e)}")
            return None

    def get_multi_by_field(self, field: str, value: Any) -> List[Any]:
        """Get multiple records by field value"""
        try:
            return self._db.query(self.model_class).filter(getattr(self.model_class, field) == value).all()
        except Exception as e:
            logger.error(f"Error getting records by field: {str(e)}")
            return []

    def exists(self, id: Any) -> bool:
        """Check if a record exists"""
        try:
            return self._db.query(self.model_class).filter(self.model_class.id == id).first() is not None
        except Exception as e:
            logger.error(f"Error checking record existence: {str(e)}")
            return False

    def count(self) -> int:
        """Count total records"""
        try:
            return self._db.query(self.model_class).count()
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            return 0

    def filter(self, **kwargs) -> List[Any]:
        """Filter records by multiple criteria"""
        try:
            query = self._db.query(self.model_class)
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.all()
        except Exception as e:
            logger.error(f"Error filtering records: {str(e)}")
            return [] 