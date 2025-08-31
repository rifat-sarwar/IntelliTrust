import boto3
import hashlib
import logging
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings

logger = logging.getLogger(__name__)

class FileStorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile) -> str:
        """
        Upload a file to S3/MinIO storage
        """
        try:
            # Generate unique filename
            file_hash = self.calculate_hash(file)
            file_extension = self._get_file_extension(file.filename)
            filename = f"{file_hash}{file_extension}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                filename,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'private'
                }
            )
            
            # Generate URL
            file_url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{filename}"
            
            logger.info(f"File uploaded successfully: {filename}")
            return file_url
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"File upload failed: {str(e)}")

    def calculate_hash(self, file: UploadFile) -> str:
        """
        Calculate SHA256 hash of file content
        """
        try:
            # Read file content
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer
            
            # Calculate hash
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            raise Exception(f"Hash calculation failed: {str(e)}")

    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from storage
        """
        try:
            # Extract filename from URL
            filename = file_url.split('/')[-1]
            
            # Delete from S3/MinIO
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            logger.info(f"File deleted successfully: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def get_file_url(self, filename: str, expires_in: int = 3600) -> str:
        """
        Generate presigned URL for file access
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise Exception(f"URL generation failed: {str(e)}")

    def _get_file_extension(self, filename: Optional[str]) -> str:
        """
        Extract file extension from filename
        """
        if not filename:
            return ""
        
        if '.' in filename:
            return '.' + filename.split('.')[-1]
        return ""

    def validate_file_type(self, filename: str) -> bool:
        """
        Validate if file type is allowed
        """
        if not filename:
            return False
        
        allowed_extensions = settings.ALLOWED_FILE_TYPES.split(',')
        file_extension = self._get_file_extension(filename).lower()
        
        return file_extension in allowed_extensions
