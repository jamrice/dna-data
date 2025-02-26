from datetime import datetime
from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey
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


class Role(Base):
    __tablename__ = "role"

    # 권한_id
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # role
    role: Mapped[str] = mapped_column(String(10), nullable=False)

    # USER 테이블과의 관계(1:N)
    # users = relationship("User", back_populates="role")


class Interest(Base):
    __tablename__ = "interests"

    # 키워드_id
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 키워드
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)

    # USER_INTEREST 테이블과의 관계(1:N, 실제로는 M:N 관계 매핑용)
    # user_interests = relationship("UserInterest", back_populates="interest")


class User(Base):
    __tablename__ = "users"

    # id
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 이름
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 비밀번호
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    # 성별
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    # 주소
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    # 나이
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    # 생성날짜
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # 이메일
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    # 권한 (ROLE 테이블의 id 참조)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # ROLE 테이블과의 관계(N:1)
    # role = relationship("Role", back_populates="users")

    # USER_INTEREST 테이블과의 관계(1:N, 실제로는 M:N 관계 매핑용)
    # user_interests = relationship("UserInterest", back_populates="user")


class UserInterest(Base):
    __tablename__ = "user_interests"

    # 키워드_id (INTEREST 테이블 참조)
    interest_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # user_id (USER 테이블 참조)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 각 테이블과의 관계 매핑(M:N 연결 테이블)
    # interest = relationship("Interest", back_populates="user_interests")
    # user = relationship("User", back_populates="user_interests")
