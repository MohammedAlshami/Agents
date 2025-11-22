"""
Cloudflare R2 Download Service for Lambda-compatible file processing.
Handles downloading files from Cloudflare R2 URLs and processing them without local file system dependencies.
"""

import os
import requests
import tempfile
import logging
from typing import Dict, Any, BinaryIO, Optional
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudflareDownloadService:
    """
    Service for downloading files from Cloudflare R2 URLs for backend processing.
    Lambda-compatible implementation that doesn't rely on local file system.
    """
    
    def __init__(self):
        """Initialize the Cloudflare download service."""
        self.public_domain = os.getenv("CLOUDFLARE_PUBLIC_DOMAIN")
        if not self.public_domain:
            logger.warning("CLOUDFLARE_PUBLIC_DOMAIN not configured")
    
    def download_file_from_url(self, file_url: str, file_name: str = None) -> Dict[str, Any]:
        """
        Download a file from a Cloudflare R2 URL.
        
        Args:
            file_url: The public URL of the file in Cloudflare R2
            file_name: Optional file name (will be extracted from URL if not provided)
            
        Returns:
            Dictionary with file content and metadata
        """
        try:
            logger.info(f"Downloading file from URL: {file_url}")
            
            # Download file from URL
            response = requests.get(file_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file content
            file_content = response.content
            file_size = len(file_content)
            
            # Extract file name from URL if not provided
            if not file_name:
                file_name = file_url.split('/')[-1]
                # Remove query parameters if any
                file_name = file_name.split('?')[0]
            
            # Get content type from response headers
            content_type = response.headers.get('content-type', 'application/octet-stream')
            
            logger.info(f"Successfully downloaded file: {file_name} ({file_size} bytes)")
            
            return {
                'success': True,
                'file_content': file_content,
                'file_name': file_name,
                'file_size': file_size,
                'content_type': content_type,
                'downloaded_at': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download file from URL {file_url}: {e}")
            return {
                'success': False,
                'error': f'Failed to download file: {str(e)}',
                'message': 'Network error occurred while downloading file'
            }
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'message': 'An unexpected error occurred while downloading file'
            }
    
    def download_file_for_processing(self, file_url: str, file_name: str = None) -> Dict[str, Any]:
        """
        Download a file from Cloudflare R2 URL for backend processing.
        Returns file content as BytesIO object for Lambda compatibility.
        
        Args:
            file_url: The public URL of the file in Cloudflare R2
            file_name: Optional file name
            
        Returns:
            Dictionary with file object and metadata for processing
        """
        try:
            # Download file
            download_result = self.download_file_from_url(file_url, file_name)
            
            if not download_result['success']:
                return download_result
            
            # Create BytesIO object for processing
            file_object = BytesIO(download_result['file_content'])
            
            return {
                'success': True,
                'file_object': file_object,
                'file_name': download_result['file_name'],
                'file_size': download_result['file_size'],
                'content_type': download_result['content_type'],
                'downloaded_at': download_result['downloaded_at']
            }
            
        except Exception as e:
            logger.error(f"Error preparing file for processing: {e}")
            return {
                'success': False,
                'error': f'Failed to prepare file for processing: {str(e)}',
                'message': 'Error occurred while preparing file for backend processing'
            }
    
    def validate_cloudflare_url(self, file_url: str) -> bool:
        """
        Validate if the URL is a valid Cloudflare R2 URL.
        
        Args:
            file_url: The URL to validate
            
        Returns:
            True if valid Cloudflare R2 URL, False otherwise
        """
        try:
            if not self.public_domain:
                logger.warning("CLOUDFLARE_PUBLIC_DOMAIN not configured, cannot validate URL")
                return True  # Allow if domain not configured
            
            # Check if URL contains the public domain
            if self.public_domain in file_url:
                return True
            
            # Check if it's a Cloudflare R2 URL pattern
            if 'r2.dev' in file_url or 'cloudflarestorage.com' in file_url:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating Cloudflare URL: {e}")
            return False
    
    def get_file_metadata_from_url(self, file_url: str) -> Dict[str, Any]:
        """
        Get file metadata from Cloudflare R2 URL without downloading the full file.
        
        Args:
            file_url: The public URL of the file in Cloudflare R2
            
        Returns:
            Dictionary with file metadata
        """
        try:
            # Make HEAD request to get metadata
            response = requests.head(file_url, timeout=10)
            response.raise_for_status()
            
            # Extract file name from URL
            file_name = file_url.split('/')[-1].split('?')[0]
            
            return {
                'success': True,
                'file_name': file_name,
                'file_size': int(response.headers.get('content-length', 0)),
                'content_type': response.headers.get('content-type', 'application/octet-stream'),
                'last_modified': response.headers.get('last-modified'),
                'etag': response.headers.get('etag', '').strip('"'),
                'metadata_retrieved_at': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get file metadata from URL {file_url}: {e}")
            return {
                'success': False,
                'error': f'Failed to get file metadata: {str(e)}',
                'message': 'Network error occurred while getting file metadata'
            }
        except Exception as e:
            logger.error(f"Unexpected error getting file metadata: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'message': 'An unexpected error occurred while getting file metadata'
            }


# Global instance
cloudflare_download_service = CloudflareDownloadService()
