"""
Cloud storage service for managing PDF files using Cloudflare R2.
"""
import logging
from typing import Optional, Dict, Any
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class R2StorageService:
    """Service for managing PDF storage in Cloudflare R2."""
    
    def __init__(self, account_id: str, access_key_id: str, secret_access_key: str, 
                 bucket_name: str = "510k-pdfs", public_url_base: Optional[str] = None):
        """
        Initialize R2 storage service.
        
        Args:
            account_id: Cloudflare account ID
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: Name of the R2 bucket (default: "510k-pdfs")
            public_url_base: Optional public URL base for the bucket (e.g., custom domain)
        """
        self.bucket_name = bucket_name
        self.account_id = account_id
        self.public_url_base = public_url_base
        
        # Initialize S3 client for R2
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3}
            ),
            region_name='auto'  # R2 doesn't use regions, but boto3 requires this
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket '{self.bucket_name}'")
                    
                    # Set bucket to be publicly accessible (for PDF viewing)
                    # Note: R2 bucket policies work differently than S3
                    # You'll need to configure this in Cloudflare dashboard
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    async def upload_pdf(self, k_number: str, pdf_content: bytes, 
                        metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload a PDF to R2 storage.
        
        Args:
            k_number: The K number of the device (e.g., "K123456")
            pdf_content: The PDF content as bytes
            metadata: Optional metadata to store with the PDF
            
        Returns:
            Dictionary containing storage details including URL and key
        """
        logger.info(f"Starting R2 upload for {k_number} (size: {len(pdf_content):,} bytes)")
        try:
            # Generate storage key
            key = f"510k/{k_number}/{k_number}.pdf"
            logger.debug(f"Using storage key: {key}")
            
            # Calculate content hash for integrity
            content_hash = hashlib.sha256(pdf_content).hexdigest()
            logger.debug(f"Content hash: {content_hash}")
            
            # Prepare metadata
            upload_metadata = {
                'k_number': k_number,
                'content_hash': content_hash,
                'content_type': 'application/pdf'
            }
            if metadata:
                upload_metadata.update(metadata)
                logger.debug(f"Upload metadata: {upload_metadata}")
            
            # Upload to R2
            logger.info(f"Uploading to R2 bucket '{self.bucket_name}'...")
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_content,
                ContentType='application/pdf',
                Metadata=upload_metadata
            )
            
            # Generate URL
            url = self._generate_url(key)
            
            logger.info(f"✅ Successfully uploaded PDF for {k_number} to R2")
            logger.info(f"   📍 URL: {url}")
            
            return {
                'success': True,
                'key': key,
                'url': url,
                'bucket': self.bucket_name,
                'size': len(pdf_content),
                'content_hash': content_hash,
                'metadata': upload_metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload PDF for {k_number} to R2: {e}")
            logger.exception("Full upload error details:")
            return {
                'success': False,
                'error': str(e),
                'k_number': k_number
            }
    
    async def get_pdf_bytes(self, k_number: str) -> Optional[bytes]:
        """
        Retrieve PDF content from R2.
        
        Args:
            k_number: The K number of the device
            
        Returns:
            PDF content as bytes, or None if not found
        """
        key = f"510k/{k_number}/{k_number}.pdf"
        logger.info(f"Retrieving PDF from R2 for {k_number} (key: {key})")
        
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            pdf_bytes = response['Body'].read()
            logger.info(f"✅ Successfully retrieved PDF for {k_number} from R2 (size: {len(pdf_bytes):,} bytes)")
            return pdf_bytes
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info(f"📄 PDF not found in R2 for {k_number}")
                return None
            logger.error(f"❌ Error retrieving PDF for {k_number} from R2: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error retrieving PDF for {k_number} from R2: {e}")
            logger.exception("Full retrieval error details:")
            return None
    
    async def get_pdf_url(self, k_number: str) -> Optional[str]:
        """
        Get the public URL for a PDF.
        
        Args:
            k_number: The K number of the device
            
        Returns:
            Public URL string, or None if not found
        """
        key = f"510k/{k_number}/{k_number}.pdf"
        
        # Check if file exists
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return self._generate_url(key)
        except ClientError:
            return None
    
    def _generate_url(self, key: str) -> str:
        """Generate public URL for a given key."""
        if self.public_url_base:
            # Use custom domain if configured
            return f"{self.public_url_base}/{key}"
        else:
            # Use R2 public URL format
            # Note: You need to enable public access in Cloudflare dashboard
            # The actual format will be provided when you set up the bucket
            return f"https://pub-{self.account_id}.r2.dev/{key}"
    
    async def delete_pdf(self, k_number: str) -> bool:
        """
        Delete a PDF from R2.
        
        Args:
            k_number: The K number of the device
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            key = f"510k/{k_number}/{k_number}.pdf"
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted PDF for {k_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete PDF for {k_number}: {e}")
            return False
    
    async def pdf_exists(self, k_number: str) -> bool:
        """
        Check if a PDF exists in R2.
        
        Args:
            k_number: The K number of the device
            
        Returns:
            True if exists, False otherwise
        """
        key = f"510k/{k_number}/{k_number}.pdf"
        logger.debug(f"Checking if PDF exists in R2 for {k_number} (key: {key})")
        
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            logger.debug(f"✅ PDF exists in R2 for {k_number}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.debug(f"📄 PDF does not exist in R2 for {k_number}")
            else:
                logger.debug(f"❌ Error checking PDF existence for {k_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error checking PDF existence for {k_number}: {e}")
            return False
    
    async def list_pdfs(self, prefix: Optional[str] = None, max_keys: int = 1000) -> list:
        """
        List PDFs in the bucket.
        
        Args:
            prefix: Optional prefix to filter results
            max_keys: Maximum number of keys to return
            
        Returns:
            List of PDF keys
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_keys
            }
            if prefix:
                params['Prefix'] = prefix
            
            response = self.client.list_objects_v2(**params)
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except Exception as e:
            logger.error(f"Failed to list PDFs: {e}")
            return []


# Singleton instance (will be initialized with settings)
storage_service: Optional[R2StorageService] = None


def initialize_storage_service(settings) -> R2StorageService:
    """Initialize the storage service with settings."""
    global storage_service
    
    if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY:
        storage_service = R2StorageService(
            account_id=settings.R2_ACCOUNT_ID,
            access_key_id=settings.R2_ACCESS_KEY_ID,
            secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            bucket_name=settings.R2_BUCKET_NAME or "510k-pdfs",
            public_url_base=settings.R2_PUBLIC_URL_BASE
        )
        logger.info("Initialized R2 storage service")
    else:
        logger.warning("R2 credentials not configured - storage service not initialized")
        storage_service = None
    
    return storage_service


def get_storage_service() -> Optional[R2StorageService]:
    """Get the initialized storage service instance."""
    return storage_service