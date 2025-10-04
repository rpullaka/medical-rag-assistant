"""
S3 Service Module for Medical RAG Assistant
Handles all S3 operations including logs and user feedback storage
"""

import gzip
import io
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logger = logging.getLogger(__name__)


class S3Service:
    """
    S3 Service for handling logs, feedback, and data storage
    """

    def __init__(self):
        """Initialize S3 service with configuration from environment variables"""
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "medical-rag-logs")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.use_access_point = (
            os.getenv("S3_USE_ACCESS_POINT", "false").lower() == "true"
        )

        # Initialize S3 client
        self.s3_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize S3 client with proper error handling"""
        try:
            # Check different access methods
            use_public = os.getenv("S3_USE_PUBLIC_ACCESS", "false").lower() == "true"
            use_access_point = self.use_access_point

            if use_access_point:
                # For S3 access points, use anonymous access
                from botocore import UNSIGNED
                from botocore.client import Config

                self.s3_client = boto3.client(
                    "s3",
                    region_name=self.aws_region,
                    config=Config(signature_version=UNSIGNED),
                )
                logger.info(
                    f"S3 client initialized for access point: {self.bucket_name}"
                )

            elif use_public or (self.aws_access_key and self.aws_secret_key):
                # For public buckets or with credentials
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.aws_access_key or "anonymous",
                    aws_secret_access_key=self.aws_secret_key or "anonymous",
                    region_name=self.aws_region,
                )
            else:
                # Try to use IAM role or default credentials
                self.s3_client = boto3.client("s3", region_name=self.aws_region)

            # Test connection (skip for access points and public buckets)
            if not use_public and not use_access_point:
                self._test_connection()

            logger.info(f"S3 client initialized successfully for: {self.bucket_name}")

        except NoCredentialsError:
            logger.info("Using anonymous access for S3 access point")
            try:
                # Try anonymous access for access points
                from botocore import UNSIGNED
                from botocore.client import Config

                self.s3_client = boto3.client(
                    "s3",
                    region_name=self.aws_region,
                    config=Config(signature_version=UNSIGNED),
                )
                logger.info("Anonymous S3 client initialized for access point")
            except Exception as e2:
                logger.error(f"Failed to initialize anonymous S3 client: {e2}")
                self.s3_client = None
        except Exception as e:
            logger.warning(f"S3 initialization failed: {e}")
            # Try anonymous access as fallback for access points
            if use_access_point:
                try:
                    from botocore import UNSIGNED
                    from botocore.client import Config

                    self.s3_client = boto3.client(
                        "s3",
                        region_name=self.aws_region,
                        config=Config(signature_version=UNSIGNED),
                    )
                    logger.info("Fallback anonymous S3 client initialized")
                except Exception as e2:
                    logger.error(f"All S3 initialization attempts failed: {e2}")
                    self.s3_client = None
            else:
                self.s3_client = None

    def _test_connection(self):
        """Test S3 connection and bucket access"""
        if not self.s3_client:
            return False

        try:
            # Check different access methods
            use_public = os.getenv("S3_USE_PUBLIC_ACCESS", "false").lower() == "true"
            use_access_point = self.use_access_point

            if use_access_point:
                # For access points, try to list objects (they may not support head_bucket)
                self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
                return True
            elif use_public:
                # For public buckets, try to list objects (limited to 1)
                self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
                return True
            else:
                # Standard bucket access test
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                if use_access_point:
                    logger.info(f"Access point {self.bucket_name} - assuming available")
                    return True  # Access points may not support all operations
                else:
                    logger.warning(
                        f"Bucket {self.bucket_name} does not exist. Will attempt to create it."
                    )
                    return self._create_bucket()
            elif error_code in ["403", "Forbidden"]:
                logger.info(
                    f"Access to {self.bucket_name} - assuming available for access point/public bucket"
                )
                return True  # Assume access point/bucket exists
            else:
                logger.info(
                    f"S3 connection test: {e} - proceeding anyway for access point"
                )
                return True if use_access_point else False

    def _create_bucket(self) -> bool:
        """Create S3 bucket if it doesn't exist"""
        if not self.s3_client:
            return False

        try:
            if self.aws_region == "us-east-1":
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.aws_region},
                )

            logger.info(f"Successfully created bucket: {self.bucket_name}")
            return True

        except ClientError as e:
            logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
            return False

    def upload_json(
        self, data: Dict[str, Any], key: str, compress: bool = False
    ) -> bool:
        """
        Upload JSON data to S3

        Args:
            data: Dictionary to upload as JSON
            key: S3 key (path) for the file
            compress: Whether to compress the data with gzip

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Skipping upload.")
            return False

        try:
            json_data = json.dumps(data, default=str, indent=2)

            if compress:
                # Compress the data
                buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=buffer, mode="wb") as f:
                    f.write(json_data.encode("utf-8"))
                content = buffer.getvalue()
                content_type = "application/gzip"
                key = f"{key}.gz" if not key.endswith(".gz") else key
            else:
                content = json_data.encode("utf-8")
                content_type = "application/json"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                Metadata={
                    "upload_timestamp": datetime.utcnow().isoformat(),
                    "service": "medical-rag-assistant",
                },
            )

            logger.info(f"Successfully uploaded to S3: s3://{self.bucket_name}/{key}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def upload_logs(self, log_data: List[Dict[str, Any]], log_type: str) -> bool:
        """
        Upload application logs to S3

        Args:
            log_data: List of log entries
            log_type: Type of logs (api, conversation, error, etc.)

        Returns:
            bool: True if successful, False otherwise
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = f"logs/{log_type}/{timestamp}.json"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "log_type": log_type,
            "count": len(log_data),
            "logs": log_data,
        }

        return self.upload_json(log_entry, key, compress=True)

    def upload_conversation_log(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Upload individual conversation log to S3

        Args:
            conversation_data: Dictionary containing conversation details

        Returns:
            bool: True if successful, False otherwise
        """
        conversation_id = conversation_data.get("conversation_id", "unknown")
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        key = f"conversations/{timestamp}/{conversation_id}.json"

        return self.upload_json(conversation_data, key)

    def upload_feedback_log(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Upload user feedback to S3

        Args:
            feedback_data: Dictionary containing feedback details

        Returns:
            bool: True if successful, False otherwise
        """
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        feedback_id = f"{feedback_data.get('conversation_id', 'unknown')}_{int(datetime.utcnow().timestamp())}"
        key = f"feedback/{timestamp}/{feedback_id}.json"

        return self.upload_json(feedback_data, key)

    def upload_metrics_snapshot(self, metrics_data: Dict[str, Any]) -> bool:
        """
        Upload system metrics snapshot to S3

        Args:
            metrics_data: Dictionary containing system metrics

        Returns:
            bool: True if successful, False otherwise
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = f"metrics/{timestamp}.json"

        metrics_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics_data,
        }

        return self.upload_json(metrics_entry, key)

    def export_daily_data(
        self, conversations: List[Dict], feedback: List[Dict]
    ) -> bool:
        """
        Export daily aggregated data to S3

        Args:
            conversations: List of conversations from the day
            feedback: List of feedback from the day

        Returns:
            bool: True if successful, False otherwise
        """
        date_str = datetime.utcnow().strftime("%Y%m%d")

        daily_export = {
            "date": date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_conversations": len(conversations),
                "total_feedback": len(feedback),
                "positive_feedback": len(
                    [f for f in feedback if f.get("feedback", 0) > 0]
                ),
                "negative_feedback": len(
                    [f for f in feedback if f.get("feedback", 0) < 0]
                ),
            },
            "conversations": conversations,
            "feedback": feedback,
        }

        key = f"daily_exports/{date_str}.json"
        return self.upload_json(daily_export, key, compress=True)

    def list_files(self, prefix: str = "", max_keys: int = 100) -> List[str]:
        """
        List files in S3 bucket with given prefix

        Args:
            prefix: S3 key prefix to filter files
            max_keys: Maximum number of keys to return

        Returns:
            List of S3 keys
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Cannot list files.")
            return []

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix, MaxKeys=max_keys
            )

            files = []
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"]]

            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files

        except Exception as e:
            logger.error(f"Failed to list S3 files: {e}")
            return []

    def is_available(self) -> bool:
        """Check if S3 service is available and configured"""
        return self.s3_client is not None


# Global S3 service instance
s3_service = S3Service()


# Convenience functions for easy import
def upload_conversation_to_s3(conversation_data: Dict[str, Any]) -> bool:
    """Upload conversation log to S3"""
    return s3_service.upload_conversation_log(conversation_data)


def upload_feedback_to_s3(feedback_data: Dict[str, Any]) -> bool:
    """Upload feedback to S3"""
    return s3_service.upload_feedback_log(feedback_data)


def upload_metrics_to_s3(metrics_data: Dict[str, Any]) -> bool:
    """Upload metrics to S3"""
    return s3_service.upload_metrics_snapshot(metrics_data)


def upload_logs_to_s3(log_data: List[Dict[str, Any]], log_type: str) -> bool:
    """Upload logs to S3"""
    return s3_service.upload_logs(log_data, log_type)


def is_s3_available() -> bool:
    """Check if S3 is available"""
    return s3_service.is_available()
