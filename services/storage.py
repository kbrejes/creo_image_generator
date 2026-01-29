"""Storage service for managing generated files."""

import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import aiofiles
import boto3
from botocore.exceptions import ClientError

from config import get_settings


class StorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def save(
        self,
        data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        folder: str = "",
    ) -> tuple[str, str]:
        """
        Save data to storage.

        Args:
            data: Binary data to save
            filename: Optional filename (generated if not provided)
            content_type: MIME type of the content
            folder: Optional subfolder

        Returns:
            Tuple of (filename, public_url)
        """
        pass

    @abstractmethod
    async def delete(self, filename: str, folder: str = "") -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    async def get_url(self, filename: str, folder: str = "") -> str:
        """Get public URL for a file."""
        pass

    def generate_filename(self, extension: str = "png") -> str:
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}_{unique_id}.{extension}"


class LocalStorageService(StorageService):
    """Local filesystem storage service."""

    def __init__(self):
        settings = get_settings()
        self.base_path = Path(settings.storage_local_path)
        self.base_url = settings.base_url.rstrip("/")

        # Ensure the storage directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        folder: str = "",
    ) -> tuple[str, str]:
        """Save data to local filesystem."""
        # Determine extension from content type
        ext_map = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/webp": "webp",
            "image/gif": "gif",
            "video/mp4": "mp4",
            "video/webm": "webm",
        }
        extension = ext_map.get(content_type, "png")

        # Generate filename if not provided
        if not filename:
            filename = self.generate_filename(extension)

        # Create folder if specified
        save_path = self.base_path
        if folder:
            save_path = save_path / folder
            save_path.mkdir(parents=True, exist_ok=True)

        # Save the file
        file_path = save_path / filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)

        # Generate URL
        url_path = f"/files/{folder}/{filename}" if folder else f"/files/{filename}"
        url = f"{self.base_url}{url_path}"

        return filename, url

    async def delete(self, filename: str, folder: str = "") -> bool:
        """Delete a file from local storage."""
        file_path = self.base_path
        if folder:
            file_path = file_path / folder
        file_path = file_path / filename

        try:
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    async def get_url(self, filename: str, folder: str = "") -> str:
        """Get URL for a local file."""
        url_path = f"/files/{folder}/{filename}" if folder else f"/files/{filename}"
        return f"{self.base_url}{url_path}"


class S3StorageService(StorageService):
    """S3-compatible storage service."""

    def __init__(self):
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.base_url = settings.base_url.rstrip("/")

        # Create S3 client
        client_kwargs = {
            "region_name": settings.s3_region,
            "aws_access_key_id": settings.s3_access_key,
            "aws_secret_access_key": settings.s3_secret_key,
        }
        if settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3_endpoint_url

        self.client = boto3.client("s3", **client_kwargs)

    async def save(
        self,
        data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        folder: str = "",
    ) -> tuple[str, str]:
        """Save data to S3."""
        # Determine extension from content type
        ext_map = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/webp": "webp",
            "image/gif": "gif",
            "video/mp4": "mp4",
            "video/webm": "webm",
        }
        extension = ext_map.get(content_type, "png")

        # Generate filename if not provided
        if not filename:
            filename = self.generate_filename(extension)

        # Build S3 key
        key = f"{folder}/{filename}" if folder else filename

        # Upload to S3
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            ACL="public-read",
        )

        # Generate URL
        url = f"{self.base_url}/files/{key}"

        return filename, url

    async def delete(self, filename: str, folder: str = "") -> bool:
        """Delete a file from S3."""
        key = f"{folder}/{filename}" if folder else filename

        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    async def get_url(self, filename: str, folder: str = "") -> str:
        """Get URL for an S3 file."""
        key = f"{folder}/{filename}" if folder else filename
        return f"{self.base_url}/files/{key}"


@lru_cache
def get_storage_service() -> StorageService:
    """Get the configured storage service instance."""
    settings = get_settings()

    if settings.storage_type == "s3":
        return S3StorageService()
    else:
        return LocalStorageService()
