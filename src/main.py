import json
import logging

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.ai.gemini_service import make_decision
from src.auth import create_access_token, hash_password, verify_password
from src.database import Base, SessionLocal, engine, get_db
from src.dependencies import get_current_user
from src.models import Decision, Ticket, User
from src.schemas import (
    LoginRequest,
    RegisterRequest,
    TicketCreate,
    TicketResponse,
    TokenResponse,
    UserResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


def create_demo_user():
    db = SessionLocal()

    try:
        demo_email = "demo@maxsorlabs.com"
        demo_password = "MaxsorLabsDemo123!"

        existing_user = (
            db.query(User)
            .filter(User.email == demo_email)
            .first()
        )

        if existing_user is None:
            demo_user = User(
                email=demo_email,
                password_hash=hash_password(demo_password),
            )

            db.add(demo_user)
            db.commit()

            logger.info("Demo user created: %s", demo_email)

    finally:
        db.close()


create_demo_user()


app = FastAPI(
    title="MaxsorLabs AI Decision Assistant",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User registered: id=%s", user.id)

    return user


@app.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        logger.warning(
            "Failed login attempt for email=%s",
            request.email,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id)

    logger.info(
        "Successful login: user_id=%s",
        user.id,
    )

    return TokenResponse(
        access_token=token,
    )


@app.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    request: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = Ticket(
        user_id=current_user.id,
        message=request.message,
    )

    db.add(ticket)
    db.flush()

    try:
        decision_data = make_decision(request.message)

        decision = Decision(
            ticket_id=ticket.id,
            action=decision_data["action"],
            confidence=decision_data["confidence"],
            reason=decision_data["reason"],
            sources=json.dumps(decision_data["sources"]),
        )

        db.add(decision)
        db.commit()
        db.refresh(ticket)

    except Exception:
        db.rollback()

        logger.exception(
            "AI decision failed for ticket user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate an AI decision.",
        )

    logger.info(
        "Ticket and decision created: ticket_id=%s user_id=%s action=%s",
        ticket.id,
        current_user.id,
        decision_data["action"],
    )

    return ticket


@app.get(
    "/tickets",
    response_model=list[TicketResponse],
)
def get_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(Ticket)
        .options(joinedload(Ticket.decision))
        .filter(Ticket.user_id == current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return tickets


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .options(joinedload(Ticket.decision))
        .filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id,
        )
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket