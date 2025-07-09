from extensions import db
from datetime import datetime, timezone
import uuid

class BaseModel(db.Model):
    """
    An abstract base model that provides common fields like id, created_at,
    and updated_at to other models, promoting code reuse and consistency.
    """
    __abstract__ = True  # Ensures SQLAlchemy does not create a table for BaseModel

    # For simple we can use an auto-incrementing integer ID.
    # id = db.Column(db.Integer, primary_key=True)

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Use timezone-aware datetime objects. The lambda ensures the function is called
    # every single time of record creation/update, not  only when the model is defined.
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))