from datetime import datetime
from sqlalchemy import String, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
from typing import Optional


class Conf(Base):
    __tablename__ = "conferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    num: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_url: Mapped[str] = mapped_column(String(500), nullable=True)
    date: Mapped[datetime] = mapped_column(Date, default=datetime.date, nullable=False)
    ord_num: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship with conf_summary_relation
    # summaries = relationship("ConfSummaryRelation", back_populates="conf")


class ConfSummary(Base):
    __tablename__ = "conf_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    bill_id: Mapped[int] = mapped_column(Integer, nullable=True)
    conf_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conferences.id"), nullable=True
    )

    # Relationship with conf_summary_relation
    # relations = relationship("ConfSummaryRelation", back_populates="summary")


class ConfSummaryRelation(Base):
    __tablename__ = "conf_summary_relation"

    conf_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conferences.id"), primary_key=True
    )
    summary_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conf_summaries.id"), primary_key=True
    )

    # Relationships
    # conf = relationship("Conf", back_populates="summaries")
    # summary = relationship("ConfSummary", back_populates="relations")


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bill_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    num: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    ord_num: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    keyword1: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # 추가된 필드
    keyword2: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # 추가된 필드
    keyword3: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # 추가된 필드

    # Relationship with BillSummaryRelation and BillSummaryㅂ
    # summaries = relationship("BillSummary", back_populates="bill", cascade="all, delete-orphan")


class BillSummary(Base):
    __tablename__ = "bill_summaries"

    summary_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    bill_id: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("bills.bill_id"), nullable=True
    )
    conf_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("conferences.id"), nullable=True
    )

    # Relationship with Bill and ConfSummaryRelation
    # bill = relationship("Bill", back_populates="summaries")
    # Add more relationships if needed


class BillSummaryRelation(Base):
    __tablename__ = "bill_summary_relation"

    bill_id: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("bills.bill_id"), nullable=True
    )
    summary_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bill_summaries.summary_id"), primary_key=True
    )

    # Relationships (optional, based on need)
    # bill = relationship("Bill")
    # summary = relationship("BillSummary")
