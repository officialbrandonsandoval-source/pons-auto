"""Image upload and storage service with AWS S3 support."""

import os
import uuid
from typing import Any, Dict, List, Tuple
from fastapi import UploadFile, HTTPException
import io

PILLOW_AVAILABLE = False
BOTO3_AVAILABLE = False

try:
    from PIL import Image  # type: ignore[import-untyped]
    PILLOW_AVAILABLE = True  # type: ignore[misc]
except ImportError:
    Image = None  # type: ignore[assignment, misc]

try:
    import boto3  # type: ignore[import-untyped]
    from botocore.exceptions import ClientError  # type: ignore[import-untyped]
    BOTO3_AVAILABLE = True  # type: ignore[misc]
except ImportError:
    boto3 = None  # type: ignore[assignment]
    ClientError = Exception  # type: ignore[assignment, misc]


class ImageService:
    """Handle vehicle image uploads and storage."""
    
    def __init__(self):
        self.use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
        self.local_upload_dir = "uploads/vehicles"
        
        if self.use_s3:
            if not BOTO3_AVAILABLE or boto3 is None:
                raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
            self.s3_client: Any = boto3.client(  # type: ignore[misc]
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            self.bucket_name = os.getenv("AWS_S3_BUCKET", "")
        else:
            os.makedirs(self.local_upload_dir, exist_ok=True)
    
    async def upload_image(
        self, 
        file: UploadFile, 
        vin: str,
        optimize: bool = True
    ) -> Dict[str, str]:
        """
        Upload a vehicle image.
        
        Args:
            file: The uploaded image file
            vin: Vehicle VIN
            optimize: Whether to optimize/resize the image
            
        Returns:
            Dictionary with image URL and metadata
        """
        # Validate file type
        content_type = file.content_type or "application/octet-stream"
        if not content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        # Generate unique filename
        filename = file.filename or "upload.jpg"
        file_ext = filename.split('.')[-1]
        unique_filename = f"{vin}/{uuid.uuid4()}.{file_ext}"
        
        # Read file content
        content = await file.read()
        
        # Optimize image if requested
        if optimize:
            content = await self._optimize_image(content, max_size=(1920, 1080))
        
        # Upload to storage
        if self.use_s3:
            url = await self._upload_to_s3(unique_filename, content, content_type)
        else:
            url = await self._upload_to_local(unique_filename, content)
        
        return {
            "url": url,
            "filename": unique_filename,
            "size": str(len(content)),
            "content_type": content_type
        }
    
    async def upload_multiple_images(
        self,
        files: List[UploadFile],
        vin: str,
        optimize: bool = True
    ) -> List[Dict[str, Any]]:
        """Upload multiple images for a vehicle."""
        results: List[Dict[str, Any]] = []
        
        for file in files:
            try:
                result = await self.upload_image(file, vin, optimize)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "filename": file.filename
                })
        
        return results
    
    async def delete_image(self, filename: str) -> bool:
        """Delete an image from storage."""
        try:
            if self.use_s3:
                self.s3_client.delete_object(  # type: ignore[attr-defined]
                    Bucket=self.bucket_name,
                    Key=filename
                )
            else:
                file_path = os.path.join(self.local_upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    async def _optimize_image(self, content: bytes, max_size: Tuple[int, int]) -> bytes:
        """Optimize and resize image."""
        if not PILLOW_AVAILABLE or Image is None:
            return content
            
        try:
            image = Image.open(io.BytesIO(content))  # type: ignore[attr-defined]
            
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Resize if larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)  # type: ignore[attr-defined]
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return content
    
    async def _upload_to_s3(self, filename: str, content: bytes, content_type: str) -> str:
        """Upload image to AWS S3."""
        try:
            self.s3_client.put_object(  # type: ignore[attr-defined]
                Bucket=self.bucket_name,
                Key=filename,
                Body=content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            return f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
            
        except ClientError as e:
            raise HTTPException(500, f"S3 upload failed: {str(e)}")
    
    async def _upload_to_local(self, filename: str, content: bytes) -> str:
        """Upload image to local filesystem."""
        file_path = os.path.join(self.local_upload_dir, filename)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return f"/uploads/vehicles/{filename}"


# Service instance
image_service = ImageService()
