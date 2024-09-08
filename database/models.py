import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.connection import Base, engine


class Interviews(Base):
    __tablename__ = "apriora_interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interviewee = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.UTC),
        onupdate=lambda: datetime.now(datetime.UTC),
    )

    messages = relationship("Messages", back_populates="interview")
    recordings = relationship("Recordings", back_populates="interview")
    videos = relationship("Videos", back_populates="interview")
    audios = relationship("Audios", back_populates="interview")


class Role(Enum):
    interviewer = "interviewer"
    interviewee = "interviewee"


class Messages(Base):
    __tablename__ = "apriora_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(
        Integer,
        ForeignKey("apriora_interviews.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    role = Column(SQLAlchemyEnum(Role), nullable=False)
    content = Column(String, nullable=False)
    start_time = Column(BigInteger, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC),
        onupdate=lambda: datetime.now(datetime.UTC),
    )

    interview = relationship("Interviews", back_populates="messages")


class Recordings(Base):
    __tablename__ = "apriora_recordings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(
        Integer,
        ForeignKey("apriora_interviews.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    s3_file_name = Column(String, nullable=False)

    interview = relationship("Interviews", back_populates="recordings")


class Videos(Base):
    __tablename__ = "apriora_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(
        Integer,
        ForeignKey("apriora_interviews.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    s3_file_name = Column(String, nullable=False)

    interview = relationship("Interviews", back_populates="videos")


class Audios(Base):
    __tablename__ = "apriora_audios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(
        Integer,
        ForeignKey("apriora_interviews.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    s3_file_name = Column(String, nullable=False)
    start_time = Column(BigInteger, nullable=False)

    interview = relationship("Interviews", back_populates="audios")


Base.metadata.create_all(engine)
