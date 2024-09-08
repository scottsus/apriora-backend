from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class Interview(BaseModel):
    id: int
    interviewee: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Role(Enum):
    interviewer = "interviewer"
    interviewee = "interviewee"


class Message(BaseModel):
    id: UUID
    interview_id: int
    role: Role
    content: str
    start_time: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Recording(BaseModel):
    id: UUID
    interview_id: int
    s3_file_name: str

    class Config:
        orm_mode = True


class Video(BaseModel):
    id: UUID
    interview_id: int
    s3_file_name: str

    class Config:
        orm_mode = True


class Audio(BaseModel):
    id: UUID
    interview_id: int
    s3_file_name: str

    class Config:
        orm_mode = True
