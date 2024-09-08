from typing import List

from sqlalchemy.orm import Session

from database.models import Audios, Recordings, Videos
from schemas.models import Audio, Recording, Video


def get_video(interview_id: int, db: Session) -> Video:
    return db.query(Videos).filter_by(interview_id=interview_id).one()


def get_audios(interview_id: int, db: Session) -> List[Audio]:
    return db.query(Audios).filter_by(interview_id=interview_id).all()


def store_recording(interview_id: int, file_name: str, db: Session) -> Recording:
    recording = Recordings(interview_id=interview_id, s3_file_name=file_name)
    db.add(recording)
    db.commit()
    db.refresh(recording)

    return recording
