import csv
import logging
import os
import uuid
from datetime import datetime
from io import StringIO

import boto3
import streamlit as st
from dotenv import load_dotenv
from src.database import db
from src.database.db import get_conversation_data
from src.core.rag import rag

load_dotenv()

# Set default OpenAI API key if not in environment
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = (
        "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"
    )

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

st.title("🏥 Medical RAG Assistant")
st.markdown("*Powered by Qdrant Vector Database + Hybrid Search*")

# Initialize the database if not done
if "db_initialized" not in st.session_state:
    with st.spinner("Initializing medical knowledge database..."):
        try:
            from ingest import ingest_data

            ingest_data("../data/medical_qa_metadata_sample.csv")
            st.session_state["db_initialized"] = True
            st.success("Medical database ready!")
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            st.session_state["db_initialized"] = False

if st.session_state.get("db_initialized", False):
    question = st.text_input(
        "Ask a medical question:",
        placeholder="e.g., What antibiotic is safe for pregnant women with UTI?",
    )

    if st.button("🔍 Search & Analyze", type="primary"):
        if question:
            conversation_id = str(uuid.uuid4())

            with st.spinner("Searching medical knowledge base..."):
                try:
                    answer_data = rag(question)

                    # Display the answer
                    st.markdown("### 🤖 AI Medical Assistant Response")
                    st.markdown(f"**Answer:** {answer_data['answer']}")

                    # Display metadata in columns
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Relevance", answer_data["relevance"])
                    with col2:
                        st.metric(
                            "Response Time", f"{answer_data['response_time']:.2f}s"
                        )
                    with col3:
                        st.metric("Total Tokens", answer_data["total_tokens"])

                    # Save conversation
                    db.save_conversation(
                        conversation_id=conversation_id,
                        question=question,
                        answer_data=answer_data,
                    )

                    st.session_state["conversation_id"] = conversation_id

                except Exception as e:
                    st.error(f"Error processing question: {e}")
                    # Fall back to search-only mode
                    st.markdown("### 🔍 Search Results (Fallback Mode)")
                    try:
                        from ingest import hybrid_query_rrf

                        results = hybrid_query_rrf(question)

                        for i, result in enumerate(results[:3], 1):
                            with st.expander(
                                f"Result {i}: {result.get('medical_department', 'N/A')} - Score: {result.get('fusion_score', 0):.4f}"
                            ):
                                st.write(
                                    f"**Question:** {result.get('question', '')[:200]}..."
                                )
                                st.write(
                                    f"**Answer:** {result.get('answer', '')[:300]}..."
                                )
                                st.write(
                                    f"**Department:** {result.get('medical_department', 'N/A')}"
                                )
                                st.write(
                                    f"**Severity:** {result.get('severity', 'N/A')}"
                                )
                    except Exception as e2:
                        st.error(f"Search also failed: {e2}")
        else:
            st.warning("Please enter a medical question.")

if "conversation_id" in st.session_state:
    st.write("Was this answer helpful?")
    col1, col2 = st.columns(2)

    if col1.button("👍"):
        db.save_feedback(
            conversation_id=st.session_state["conversation_id"], feedback=1
        )
        st.success("Thank you for your feedback!")
        del st.session_state["conversation_id"]

    if col2.button("👎"):
        db.save_feedback(
            conversation_id=st.session_state["conversation_id"], feedback=-1
        )
        st.success("Thank you for your feedback!")
        del st.session_state["conversation_id"]

# Set up logging
logging.basicConfig(level=logging.INFO)


def upload_csv_to_s3(data, bucket_name, file_name):
    try:
        # Create a CSV file in memory
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write CSV headers
        csv_writer.writerow(["ID", "Question", "Answer", "Feedback"])

        # Write conversation data to CSV
        for row in data:
            csv_writer.writerow(
                [
                    str(row.get("id", "")),
                    str(row.get("question", "")),
                    str(row.get("answer", "")),
                    str(row.get("feedback", "")),
                ]
            )

        # Debug: Print bucket name and file name
        logging.info(f"Uploading to bucket: {bucket_name}, file: {file_name}")

        # Upload to S3
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue()
        )
        logging.info(f"File uploaded to S3: {bucket_name}/{file_name}")
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}")


def generate_csv_file_name():
    return f'medical_assistant/conversations_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'


st.title("Medical Assistant with RAG")

if st.button("Export to CSV and Upload to S3"):
    # Get conversation data from the database
    conversation_data = get_conversation_data()

    CSV_FILE_NAME = generate_csv_file_name()

    # Upload CSV to S3
    upload_csv_to_s3(conversation_data, S3_BUCKET_NAME, CSV_FILE_NAME)

    st.success(
        f'CSV file uploaded to S3 bucket "{S3_BUCKET_NAME}" in "medical_assistant/" as "{CSV_FILE_NAME}"'
    )
