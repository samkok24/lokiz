from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from sqlalchemy import func

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.credit import CreditTransaction

router = APIRouter(prefix="/credits", tags=["credits"])


class CreditPurchaseRequest(BaseModel):
    """Request to purchase credits"""
    package_id: str  # e.g., "basic_100", "pro_500", "premium_2000"
    payment_method: str  # e.g., "card", "paypal", "bank_transfer"
    payment_token: Optional[str] = None  # Payment gateway token


class CreditPurchaseResponse(BaseModel):
    """Response after credit purchase"""
    transaction_id: UUID
    credits_added: int
    new_balance: int
    amount_paid: float
    currency: str = "USD"


class CreditHistoryItem(BaseModel):
    """Single credit transaction history item"""
    id: UUID
    transaction_type: str  # "purchase", "usage", "refund", "bonus"
    credits: int  # Positive for additions, negative for usage
    balance_after: int
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreditHistoryResponse(BaseModel):
    """Credit transaction history"""
    transactions: list[CreditHistoryItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class CreditBalanceResponse(BaseModel):
    """Current credit balance"""
    balance: int
    total_earned: int
    total_spent: int


class DailyClaimResponse(BaseModel):
    """Response after claiming daily credits"""
    claimed: bool
    amount: int
    next_claim_at: datetime
    new_balance: int


class DailyStatusResponse(BaseModel):
    """Daily credit claim status"""
    can_claim: bool
    next_claim_at: Optional[datetime]
    last_claimed_at: Optional[datetime]


# Credit packages
CREDIT_PACKAGES = {
    "starter_100": {"credits": 100, "price": 4.99, "name": "Starter Pack"},
    "basic_500": {"credits": 500, "price": 19.99, "name": "Basic Pack"},
    "pro_2000": {"credits": 2000, "price": 69.99, "name": "Pro Pack"},
    "premium_5000": {"credits": 5000, "price": 149.99, "name": "Premium Pack"},
}


@router.get("/packages")
async def get_credit_packages():
    """
    Get available credit packages
    Public endpoint - no authentication required
    """
    return {
        "packages": [
            {
                "id": package_id,
                "credits": package["credits"],
                "price": package["price"],
                "name": package["name"],
                "price_per_credit": round(package["price"] / package["credits"], 4)
            }
            for package_id, package in CREDIT_PACKAGES.items()
        ]
    }


@router.post("/purchase", response_model=CreditPurchaseResponse)
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase credits

    NOTE: This is a mock implementation for development.
    In production, integrate with actual payment gateway (Stripe, PayPal, etc.)
    """
    # Validate package
    if request.package_id not in CREDIT_PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package ID. Available: {list(CREDIT_PACKAGES.keys())}"
        )

    package = CREDIT_PACKAGES[request.package_id]

    # TODO: In production, process payment with payment gateway
    # payment_result = process_payment(
    #     amount=package["price"],
    #     token=request.payment_token,
    #     method=request.payment_method
    # )
    # if not payment_result.success:
    #     raise HTTPException(status_code=402, detail="Payment failed")

    # Mock payment success for development
    # In production, only proceed after successful payment

    # Add credits to user
    current_user.credits += package["credits"]

    # Create transaction record
    transaction = CreditTransaction(
        user_id=current_user.id,
        transaction_type="purchase",
        credits=package["credits"],
        balance_after=current_user.credits,
        description=f"Purchased {package['name']} ({package['credits']} credits)",
        extra_data={
            "package_id": request.package_id,
            "payment_method": request.payment_method,
            "amount_paid": package["price"],
            "currency": "USD"
        }
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return CreditPurchaseResponse(
        transaction_id=transaction.id,
        credits_added=package["credits"],
        new_balance=current_user.credits,
        amount_paid=package["price"],
        currency="USD"
    )


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current credit balance and statistics
    """
    # Calculate total earned (purchases + bonuses)
    total_earned = db.query(
        func.sum(CreditTransaction.credits)
    ).filter(
        CreditTransaction.user_id == current_user.id,
        CreditTransaction.transaction_type.in_(["purchase", "bonus", "refund"]),
        CreditTransaction.credits > 0
    ).scalar() or 0

    # Calculate total spent (usage)
    total_spent = abs(db.query(
        func.sum(CreditTransaction.credits)
    ).filter(
        CreditTransaction.user_id == current_user.id,
        CreditTransaction.transaction_type == "usage",
        CreditTransaction.credits < 0
    ).scalar() or 0)

    return CreditBalanceResponse(
        balance=current_user.credits,
        total_earned=total_earned,
        total_spent=total_spent
    )


@router.get("/history", response_model=CreditHistoryResponse)
async def get_credit_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    transaction_type: Optional[str] = Query(None, regex="^(purchase|usage|refund|bonus)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get credit transaction history
    """
    # Build query
    query = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == current_user.id
    )

    # Filter by transaction type if provided
    if transaction_type:
        query = query.filter(CreditTransaction.transaction_type == transaction_type)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    transactions = query.order_by(
        CreditTransaction.created_at.desc()
    ).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + len(transactions)) < total

    return CreditHistoryResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/daily-status", response_model=DailyStatusResponse)
async def get_daily_credit_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check daily credit claim status
    """
    now = datetime.now(timezone.utc)

    # Check if user has claimed today
    if current_user.last_daily_credit_claim:
        last_claim = current_user.last_daily_credit_claim

        # Convert to UTC if not already
        if last_claim.tzinfo is None:
            last_claim = last_claim.replace(tzinfo=timezone.utc)

        # Calculate next midnight (UTC)
        next_midnight = (last_claim + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Check if it's a new day
        can_claim = now >= next_midnight

        return DailyStatusResponse(
            can_claim=can_claim,
            next_claim_at=next_midnight if not can_claim else now,
            last_claimed_at=last_claim
        )
    else:
        # Never claimed before
        return DailyStatusResponse(
            can_claim=True,
            next_claim_at=None,
            last_claimed_at=None
        )


@router.post("/daily-claim", response_model=DailyClaimResponse)
async def claim_daily_credits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Claim daily free credits (10 credits per day)
    """
    DAILY_CREDIT_AMOUNT = 10
    now = datetime.now(timezone.utc)

    # Check if user has already claimed today
    if current_user.last_daily_credit_claim:
        last_claim = current_user.last_daily_credit_claim

        # Convert to UTC if not already
        if last_claim.tzinfo is None:
            last_claim = last_claim.replace(tzinfo=timezone.utc)

        # Calculate next midnight (UTC)
        next_midnight = (last_claim + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Check if it's still the same day
        if now < next_midnight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Daily credits already claimed",
                    "next_claim_at": next_midnight.isoformat(),
                    "hours_remaining": int((next_midnight - now).total_seconds() / 3600)
                }
            )

    # Add daily credits
    current_user.credits += DAILY_CREDIT_AMOUNT
    current_user.last_daily_credit_claim = now

    # Create transaction record
    transaction = CreditTransaction(
        user_id=current_user.id,
        transaction_type="bonus",
        credits=DAILY_CREDIT_AMOUNT,
        balance_after=current_user.credits,
        description="Daily free credits",
        extra_data={
            "claim_type": "daily",
            "claimed_at": now.isoformat()
        }
    )

    db.add(transaction)
    db.commit()
    db.refresh(current_user)

    # Calculate next claim time (next midnight)
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return DailyClaimResponse(
        claimed=True,
        amount=DAILY_CREDIT_AMOUNT,
        next_claim_at=next_midnight,
        new_balance=current_user.credits
    )

