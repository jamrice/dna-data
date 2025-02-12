from datetime import datetime
from sqlalchemy import String, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Conf(Base):
    tablename = "conf"

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
    tablename = "conf_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    bill_id: Mapped[int] = mapped_column(Integer, nullable=True)
    conf_id: Mapped[int] = mapped_column(Integer, ForeignKey("conf.id"), nullable=True)

    # Relationship with conf_summary_relation
    # relations = relationship("ConfSummaryRelation", back_populates="summary")


class ConfSummaryRelation(Base):
    tablename = "conf_summary_relation"

    conf_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conf.id"), primary_key=True
    )
    summary_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conf_summary.id"), primary_key=True
    )

    # Relationships
    # conf = relationship("Conf", back_populates="summaries")
    # summary = relationship("ConfSummary", back_populates="relations")
