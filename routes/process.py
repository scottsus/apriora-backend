import os

import ffmpeg
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from database.connection import get_db
from utils.postgres.store import get_audios, get_video, store_recording
from utils.s3.client import get_signed_url, upload_recording

router = APIRouter()


@router.get("/process-multimedia", status_code=status.HTTP_200_OK)
def ping():
    return {"message": "/process-multimedia endpoint 👋"}


@router.post("/process-multimedia", status_code=status.HTTP_200_OK)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=1, max=8))
async def process_multimedia(interview_id: int, db: Session = Depends(get_db)):
    print(f"Processing recording for interview: {interview_id}")

    try:
        local_file_name = f"final_{interview_id}.mp4"

        video = get_video(interview_id=interview_id, db=db)
        audios = get_audios(interview_id=interview_id, db=db)

        video_url = get_signed_url("videos/", video.s3_file_name)
        audio_urls = [get_signed_url("audios/", audio.s3_file_name) for audio in audios]

        video_input = ffmpeg.input(video_url)
        audio_inputs = [ffmpeg.input(url) for url in audio_urls]

        video_audio = video_input.audio
        audio_streams = [
            audio_input.filter("adelay", f"{audio.start_time}ms|{audio.start_time}ms")
            for audio_input, audio in zip(audio_inputs, audios)
        ]
        audio_streams.insert(0, video_audio)

        merged_audio = ffmpeg.filter(
            audio_streams, "amix", inputs=len(audio_streams), normalize=0
        )

        output = ffmpeg.output(
            video_input.video,
            merged_audio,
            local_file_name,
            vcodec="libx264",
            acodec="aac",
        )

        ffmpeg.run(output, overwrite_output=True)

        upload_recording(local_file_name)
        store_recording(interview_id=interview_id, file_name=local_file_name, db=db)

    except Exception as e:
        print(f"process_multimedia: {str(e)}")
        raise

    finally:
        if os.path.exists(local_file_name):
            os.remove(local_file_name)

    return {"message": f"Successfully processed recording for {interview_id}"}
