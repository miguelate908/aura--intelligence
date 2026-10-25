from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.sql import func

from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    sku = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    price = Column(Float, default=0)


class Warehouse(Base):
    __tablename__ = "warehouses"


    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(200), nullable=True)
class Event(Base):
    __tablename__ = "events"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    event_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    entity_type = Column(
        String(100),
        nullable=True
    )

    entity_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    description = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class DemoRequest(Base):
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    message = Column(Text, nullable=True)
    notification_sent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    source_type = Column(
        String(100),
        nullable=False
    )

    source_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    relationship_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    target_type = Column(
        String(100),
        nullable=False
    )

    target_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
