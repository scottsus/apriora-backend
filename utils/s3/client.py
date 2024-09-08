import os

import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
RECORDING_FOLDER = "recordings/"


def get_signed_url(folder_prefix: str, file_name: str) -> str:
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": f"{folder_prefix}{file_name}"},
            ExpiresIn=3600,
        )
    except Exception as e:
        print(f"get_signed_url: {e}")
        raise


def upload_recording(file_name: str) -> str:
    print(f"Uploading recording for: {file_name}")

    file_size = os.path.getsize(file_name)
    chunk_size = 5 * 1024 * 1024  # S3 5MB minimum requirement

    try:
        s3_key = f"{RECORDING_FOLDER}{file_name}"

        if file_size < chunk_size:
            with open(file_name, "rb") as file:
                client.put_object(
                    Bucket=BUCKET_NAME, Key=s3_key, Body=file, ContentType="video/mp4"
                )

            return file_name

        mpu = client.create_multipart_upload(
            Bucket=BUCKET_NAME, Key=s3_key, ContentType="video/mp4"
        )

        parts = []
        part_number = 1

        with open(file_name, "rb") as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                part = client.upload_part(
                    Bucket=BUCKET_NAME,
                    Key=s3_key,
                    PartNumber=part_number,
                    UploadId=mpu["UploadId"],
                    Body=data,
                )
                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                part_number += 1

            client.complete_multipart_upload(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                UploadId=mpu["UploadId"],
                MultipartUpload={"Parts": parts},
            )

            print(f"Uploaded {file_name} to S3")

        return file_name
    except Exception as e:
        raise Exception(f"upload_recording: {str(e)}")
