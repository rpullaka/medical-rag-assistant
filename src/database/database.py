"""
Professional Medical RAG Database Module
Handles PostgreSQL operations with metrics tracking for HR and MRR
"""

import json
import logging
import os
from datetime import datetime, timezone
from io import StringIO
from typing import Any, Dict, List, Optional

import boto3
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor

# Import S3 service
from src.services.s3_service import (is_s3_available, upload_conversation_to_s3,
                                      upload_feedback_to_s3)

# Configuration
TZ_INFO = os.getenv("TZ", "UTC")
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            dbname=os.getenv("POSTGRES_DB", "medical_rag"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Drop existing tables
            cur.execute("DROP TABLE IF EXISTS metrics CASCADE")
            cur.execute("DROP TABLE IF EXISTS feedback CASCADE")
            cur.execute("DROP TABLE IF EXISTS conversations CASCADE")

            # Conversations table
            cur.execute(
                """
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    total_cost FLOAT NOT NULL,
                    search_results_count INTEGER NOT NULL,
                    token_stats JSONB NOT NULL,
                    search_results JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """
            )

            # Feedback table
            cur.execute(
                """
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL CHECK (feedback IN (-1, 1)),
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """
            )

            # Metrics table for HR and MRR tracking
            cur.execute(
                """
                CREATE TABLE metrics (
                    id SERIAL PRIMARY KEY,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value FLOAT NOT NULL,
                    query_text TEXT,
                    expected_rank INTEGER,
                    actual_rank INTEGER,
                    hit BOOLEAN,
                    conversation_id TEXT REFERENCES conversations(id),
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """
            )

            # Indexes for better performance
            cur.execute(
                "CREATE INDEX idx_conversations_timestamp ON conversations(timestamp)"
            )
            cur.execute(
                "CREATE INDEX idx_feedback_conversation_id ON feedback(conversation_id)"
            )
            cur.execute("CREATE INDEX idx_feedback_timestamp ON feedback(timestamp)")
            cur.execute(
                "CREATE INDEX idx_metrics_type_name ON metrics(metric_type, metric_name)"
            )
            cur.execute("CREATE INDEX idx_metrics_timestamp ON metrics(timestamp)")

        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()


def save_conversation(conversation_id: str, question: str, answer_data: Dict):
    """Save conversation data to database and S3"""
    conn = get_db_connection()
    try:
        timestamp = datetime.now(timezone.utc)

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, answer, model_used, response_time, relevance, 
                 relevance_explanation, total_cost, search_results_count, 
                 token_stats, search_results, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    conversation_id,
                    question,
                    answer_data.get("answer", ""),
                    answer_data.get("model_used", ""),
                    answer_data.get("response_time", 0.0),
                    answer_data.get("relevance", "UNKNOWN"),
                    answer_data.get("relevance_explanation", ""),
                    answer_data.get("total_cost", 0.0),
                    answer_data.get("search_results_count", 0),
                    json.dumps(answer_data.get("token_stats", {})),
                    json.dumps(answer_data.get("search_results", [])),
                    timestamp,
                ),
            )
        conn.commit()

        # Calculate and save HR/MRR metrics
        _calculate_and_save_metrics(conversation_id, question, answer_data)

        # Upload to S3 if enabled
        if (
            os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true"
            and is_s3_available()
        ):
            s3_data = {
                "conversation_id": conversation_id,
                "question": question,
                "answer": answer_data.get("answer", ""),
                "model_used": answer_data.get("model_used", ""),
                "response_time": answer_data.get("response_time", 0.0),
                "relevance": answer_data.get("relevance", "UNKNOWN"),
                "relevance_explanation": answer_data.get("relevance_explanation", ""),
                "total_cost": answer_data.get("total_cost", 0.0),
                "search_results_count": answer_data.get("search_results_count", 0),
                "token_stats": answer_data.get("token_stats", {}),
                "search_results": answer_data.get("search_results", []),
                "timestamp": timestamp.isoformat(),
            }
            upload_conversation_to_s3(s3_data)

    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving conversation {conversation_id}: {e}")
        raise
    finally:
        conn.close()


def save_feedback(conversation_id: str, feedback: int):
    """Save user feedback to database and S3"""
    conn = get_db_connection()
    try:
        timestamp = datetime.now(timezone.utc)

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (conversation_id, feedback, timestamp)
                VALUES (%s, %s, %s)
            """,
                (conversation_id, feedback, timestamp),
            )
        conn.commit()

        # Upload to S3 if enabled
        if (
            os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true"
            and is_s3_available()
        ):
            s3_data = {
                "conversation_id": conversation_id,
                "feedback": feedback,
                "timestamp": timestamp.isoformat(),
                "feedback_type": (
                    "positive"
                    if feedback > 0
                    else "negative" if feedback < 0 else "neutral"
                ),
            }
            upload_feedback_to_s3(s3_data)

    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving feedback for {conversation_id}: {e}")
        raise
    finally:
        conn.close()


def _calculate_and_save_metrics(conversation_id: str, question: str, answer_data: Dict):
    """Calculate Hit Rate and MRR metrics"""
    conn = get_db_connection()
    try:
        search_results = answer_data.get("search_results", [])

        if not search_results:
            return

        # Calculate Hit Rate (HR) - whether any relevant result was found
        hit = len(search_results) > 0 and any(
            result.get("score", 0) > 0.7
            for result in search_results  # Threshold for relevance
        )

        # Calculate MRR - Mean Reciprocal Rank
        # For this implementation, we assume the first result is the most relevant
        reciprocal_rank = 1.0 if hit and search_results else 0.0
        if hit and len(search_results) > 0:
            # Find the rank of the first highly relevant result
            for idx, result in enumerate(search_results):
                if result.get("score", 0) > 0.7:
                    reciprocal_rank = 1.0 / (idx + 1)
                    break

        with conn.cursor() as cur:
            # Save Hit Rate metric
            cur.execute(
                """
                INSERT INTO metrics 
                (metric_type, metric_name, metric_value, query_text, hit, conversation_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    "retrieval",
                    "hit_rate",
                    1.0 if hit else 0.0,
                    question,
                    hit,
                    conversation_id,
                    datetime.now(timezone.utc),
                ),
            )

            # Save MRR metric
            cur.execute(
                """
                INSERT INTO metrics 
                (metric_type, metric_name, metric_value, query_text, conversation_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    "retrieval",
                    "mrr",
                    reciprocal_rank,
                    question,
                    conversation_id,
                    datetime.now(timezone.utc),
                ),
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating metrics for {conversation_id}: {e}")
    finally:
        conn.close()


def get_metrics() -> Dict[str, Any]:
    """Get aggregated metrics for monitoring dashboard"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get overall statistics
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_conversations,
                    AVG(response_time) as avg_response_time,
                    AVG(total_cost) as avg_cost,
                    COUNT(CASE WHEN relevance = 'RELEVANT' THEN 1 END) * 100.0 / COUNT(*) as relevance_rate
                FROM conversations 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
            """
            )
            stats = dict(cur.fetchone())

            # Get Hit Rate
            cur.execute(
                """
                SELECT AVG(metric_value) * 100 as hit_rate
                FROM metrics 
                WHERE metric_name = 'hit_rate' 
                AND timestamp >= NOW() - INTERVAL '24 hours'
            """
            )
            hit_rate_result = cur.fetchone()
            stats["hit_rate"] = (
                float(hit_rate_result["hit_rate"])
                if hit_rate_result["hit_rate"]
                else 0.0
            )

            # Get MRR
            cur.execute(
                """
                SELECT AVG(metric_value) as mrr
                FROM metrics 
                WHERE metric_name = 'mrr' 
                AND timestamp >= NOW() - INTERVAL '24 hours'
            """
            )
            mrr_result = cur.fetchone()
            stats["mrr"] = float(mrr_result["mrr"]) if mrr_result["mrr"] else 0.0

            # Get feedback statistics
            cur.execute(
                """
                SELECT 
                    COUNT(CASE WHEN feedback = 1 THEN 1 END) * 100.0 / COUNT(*) as positive_feedback_rate,
                    COUNT(*) as total_feedback
                FROM feedback 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
            """
            )
            feedback_stats = dict(cur.fetchone())
            stats.update(feedback_stats)

            return stats

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        return {"error": "Unable to retrieve metrics"}
    finally:
        conn.close()


def upload_to_s3(data: str, key: str):
    """Upload data to S3 for logging and backup"""
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )

        bucket_name = os.getenv("S3_BUCKET_NAME", "medical-rag-logs")

        s3_client.put_object(
            Bucket=bucket_name, Key=key, Body=data, ContentType="application/json"
        )

        logger.info(f"Data uploaded to S3: s3://{bucket_name}/{key}")

    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")


def export_conversations_to_s3():
    """Export recent conversations to S3 for analysis"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM conversations 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                ORDER BY timestamp DESC
            """
            )

            conversations = [dict(row) for row in cur.fetchall()]

            if conversations:
                data = json.dumps(conversations, default=str, indent=2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                key = f"conversations/daily_export_{timestamp}.json"

                upload_to_s3(data, key)

    except Exception as e:
        logger.error(f"Error exporting conversations to S3: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")
