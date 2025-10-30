from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.session import Base


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    transaction_type = Column(String(20), nullable=False, index=True)  # purchase, usage, refund, bonus
    credits = Column(Integer, nullable=False)  # Positive for additions, negative for usage
    balance_after = Column(Integer, nullable=False)  # Balance after this transaction
    
    description = Column(String(500), nullable=False)
    extra_data = Column(JSON, nullable=True)  # Additional data (package_id, payment_method, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

