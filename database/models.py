"""SQLAlchemy ORM models for the Jaded Rose application."""

from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


class Order(Base):
    """Represents a synced Shopify order."""

    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    shopify_order_id: str = Column(String(64), unique=True, nullable=False, index=True)
    customer_email: str = Column(String(255), nullable=True)
    status: str = Column(String(32), nullable=False, default="open")
    total_price: float = Column(Float, nullable=False, default=0.0)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"<Order shopify_order_id={self.shopify_order_id!r} status={self.status!r}>"


class Product(Base):
    """Represents a synced Shopify product."""

    __tablename__ = "products"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    shopify_product_id: str = Column(String(64), unique=True, nullable=False, index=True)
    title: str = Column(String(512), nullable=False)
    sku: str = Column(String(128), nullable=True)
    inventory_quantity: int = Column(Integer, nullable=False, default=0)
    price: float = Column(Float, nullable=False, default=0.0)
    updated_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"<Product title={self.title!r} sku={self.sku!r}>"


class ChatSession(Base):
    """Tracks a customer chat session across channels."""

    __tablename__ = "chat_sessions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    channel: str = Column(String(32), nullable=False)
    user_id: str = Column(String(128), nullable=False, index=True)
    thread_id: str = Column(String(128), nullable=True)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_active: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"<ChatSession channel={self.channel!r} user_id={self.user_id!r}>"


class OutreachContact(Base):
    """Stores B2B outreach contact records."""

    __tablename__ = "outreach_contacts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    company_name: str = Column(String(256), nullable=False)
    email: str = Column(String(255), nullable=False, index=True)
    status: str = Column(String(32), nullable=False, default="pending")
    sent_at: datetime.datetime | None = Column(DateTime(timezone=True), nullable=True)
    replied_at: datetime.datetime | None = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"<OutreachContact company={self.company_name!r} status={self.status!r}>"


class WeeklyReport(Base):
    """Stores generated weekly business reports."""

    __tablename__ = "weekly_reports"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    week_start: datetime.datetime = Column(DateTime(timezone=True), nullable=False)
    week_end: datetime.datetime = Column(DateTime(timezone=True), nullable=False)
    total_units_sold: int = Column(Integer, nullable=False, default=0)
    report_json: dict[str, Any] = Column(JSON, nullable=True)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"<WeeklyReport week_start={self.week_start} units={self.total_units_sold}>"
