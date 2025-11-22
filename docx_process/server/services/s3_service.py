"""
S3 service for file upload and download operations.
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import hashlib
import mimetypes
import uuid
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service for S3 operations."""
    
    def __init__(self):
        """Initialize S3 client for Cloudflare R2."""
        # Cloudflare R2 credentials
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.cloudflare_access_key_id = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
        self.cloudflare_secret_access_key = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("CLOUDFLARE_BUCKET_NAME")
        self.public_domain = os.getenv("CLOUDFLARE_PUBLIC_DOMAIN")
        
        if not all([self.cloudflare_access_key_id, self.cloudflare_secret_access_key, self.bucket_name]):
            raise ValueError("Cloudflare R2 credentials and bucket name are required")
        
        # Cloudflare R2 endpoint
        self.endpoint_url = f"https://{self.cloudflare_account_id}.r2.cloudflarestorage.com"
        
        # Initialize S3 client for Cloudflare R2
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.cloudflare_access_key_id,
            aws_secret_access_key=self.cloudflare_secret_access_key,
            endpoint_url=self.endpoint_url,
            region_name='auto'  # Cloudflare R2 uses 'auto' region
        )
        
        # Initialize S3 resource for additional operations
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.cloudflare_access_key_id,
            aws_secret_access_key=self.cloudflare_secret_access_key,
            endpoint_url=self.endpoint_url,
            region_name='auto'
        )
        
        self.bucket = self.s3_resource.Bucket(self.bucket_name)
    
    def generate_presigned_upload_url(self, file_key: str, content_type: str, 
                                    expires_in: int = 3600) -> Dict[str, Any]:
        """
        Generate a pre-signed URL for file upload.
        
        Args:
            file_key: S3 object key
            content_type: File content type
            expires_in: URL expiration time in seconds
            
        Returns:
            Dictionary with upload URL and metadata
        """
        try:
            # Generate pre-signed URL for PUT operation
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
            
            return {
                'upload_url': presigned_url,
                'file_key': file_key,
                'content_type': content_type,
                'expires_at': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate upload URL: {str(e)}")
            raise Exception(f"Failed to generate upload URL: {str(e)}")
    
    def generate_presigned_download_url(self, file_key: str, 
                                      expires_in: int = 3600) -> Dict[str, Any]:
        """
        Generate a pre-signed URL for file download.
        
        Args:
            file_key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Dictionary with download URL and metadata
        """
        try:
            # Get object metadata first
            try:
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
                content_type = response.get('ContentType', 'application/octet-stream')
                content_length = response.get('ContentLength', 0)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise Exception("File not found in S3")
                raise e
            
            # Generate pre-signed URL for GET operation
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expires_in
            )
            
            return {
                'download_url': presigned_url,
                'file_key': file_key,
                'content_type': content_type,
                'file_size': content_length,
                'expires_at': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate download URL: {str(e)}")
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def upload_file(self, file_path: str, file_key: str, 
                   content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to S3.
        
        Args:
            file_path: Local file path
            file_key: S3 object key
            content_type: File content type (auto-detected if not provided)
            
        Returns:
            Dictionary with upload result
        """
        try:
            # Auto-detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                file_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            
            return {
                'file_key': file_key,
                'content_type': content_type,
                'file_size': response.get('ContentLength', 0),
                'etag': response.get('ETag', '').strip('"'),
                'uploaded_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def upload_file_object(self, file_object: BinaryIO, file_key: str, 
                          content_type: str) -> Dict[str, Any]:
        """
        Upload a file object to S3.
        
        Args:
            file_object: File-like object
            file_key: S3 object key
            content_type: File content type
            
        Returns:
            Dictionary with upload result
        """
        try:
            # Upload file object
            self.s3_client.upload_fileobj(
                file_object,
                self.bucket_name,
                file_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            
            return {
                'file_key': file_key,
                'content_type': content_type,
                'file_size': response.get('ContentLength', 0),
                'etag': response.get('ETag', '').strip('"'),
                'uploaded_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file object: {str(e)}")
            raise Exception(f"Failed to upload file object: {str(e)}")
    
    def download_file(self, file_key: str, local_path: str) -> Dict[str, Any]:
        """
        Download a file from S3.
        
        Args:
            file_key: S3 object key
            local_path: Local file path to save to
            
        Returns:
            Dictionary with download result
        """
        try:
            # Download file
            self.s3_client.download_file(self.bucket_name, file_key, local_path)
            
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            
            return {
                'file_key': file_key,
                'local_path': local_path,
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'file_size': response.get('ContentLength', 0),
                'downloaded_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise e
    
    def get_file_metadata(self, file_key: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from S3.
        
        Args:
            file_key: S3 object key
            
        Returns:
            Dictionary with file metadata or None if not found
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            
            return {
                'file_key': file_key,
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'file_size': response.get('ContentLength', 0),
                'etag': response.get('ETag', '').strip('"'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise e
    
    def copy_file(self, source_key: str, destination_key: str) -> bool:
        """
        Copy a file within S3.
        
        Args:
            source_key: Source S3 object key
            destination_key: Destination S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file: {str(e)}")
            return False
    
    def generate_file_key(self, user_id: str, file_name: str, 
                          version_number: int = 1) -> str:
        """
        Generate a unique S3 file key.
        
        Args:
            user_id: User ID
            file_name: Original file name
            version_number: File version number
            
        Returns:
            Generated S3 file key
        """
        # Create a unique identifier
        unique_id = str(uuid.uuid4())
        
        # Sanitize file name
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        safe_file_name = safe_file_name.replace(' ', '_')
        
        # Generate file key with structure: users/{user_id}/files/{unique_id}_{version}_{filename}
        file_key = f"users/{user_id}/files/{unique_id}_v{version_number}_{safe_file_name}"
        
        return file_key
    
    def get_public_url(self, file_key: str) -> str:
        """
        Generate a public URL for a file using Cloudflare R2 public domain.
        
        Args:
            file_key: S3 object key
            
        Returns:
            Public URL for the file
        """
        if not self.public_domain:
            raise ValueError("Cloudflare public domain not configured")
        
        return f"https://{self.public_domain}/{file_key}"
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 checksum
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def calculate_file_object_checksum(self, file_object: BinaryIO) -> str:
        """
        Calculate SHA-256 checksum of a file object.
        
        Args:
            file_object: File-like object
            
        Returns:
            SHA-256 checksum
        """
        sha256_hash = hashlib.sha256()
        
        # Reset file pointer to beginning
        file_object.seek(0)
        
        for chunk in iter(lambda: file_object.read(4096), b""):
            sha256_hash.update(chunk)
        
        # Reset file pointer to beginning
        file_object.seek(0)
        
        return sha256_hash.hexdigest()
