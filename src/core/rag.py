#!/usr/bin/env python3
"""
Medical RAG System - Updated Implementation
Following reference architecture with proper prompt engineering and evaluation
"""

import json
import os
from time import time
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

import sys
# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from ingest import hybrid_query_rrf

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search medical knowledge base using hybrid search

    Args:
        query: Medical query text
        top_k: Number of results to return

    Returns:
        List of relevant medical documents
    """
    return hybrid_query_rrf(query, top_k=top_k)


# Prompt templates following reference implementation
PROMPT_TEMPLATE = """You are a knowledgeable medical assistant. Answer the QUESTION based solely on the information provided in the CONTEXT from the medical database.

Use only the facts from the CONTEXT when formulating your answer.

QUESTION: {question}

CONTEXT:
{context}""".strip()


ENTRY_TEMPLATE = """Medical Case:
Question: {question}
Answer: {answer}
Relevance Score: {score:.3f}
""".strip()


def build_prompt(query: str, search_results: List[Dict]) -> str:
    """
    Build prompt from query and search results following reference implementation

    Args:
        query: User question
        search_results: Retrieved medical cases

    Returns:
        Formatted prompt for LLM
    """
    context = ""

    for doc in search_results:
        context += (
            ENTRY_TEMPLATE.format(
                question=doc.get("question", "N/A"),
                answer=doc.get("answer", "N/A"),
                score=doc.get("score", 0.0),
            )
            + "\n\n"
        )

    return PROMPT_TEMPLATE.format(question=query, context=context.strip())


def llm(prompt: str, model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
    """
    Generate response using OpenAI LLM following reference implementation

    Args:
        prompt: Input prompt for the model
        model: OpenAI model to use

    Returns:
        Tuple of (response_text, token_statistics)
    """
    if not client:
        raise Exception("OpenAI API key not configured")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.1,
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


# Evaluation prompt template following reference implementation
EVALUATION_PROMPT_TEMPLATE = """You are an expert medical reviewer evaluating the quality and relevance of AI-generated medical responses.

You will be given a medical question and a generated answer. Based on the relevance of the generated answer, you will classify it as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}""".strip()


def evaluate_relevance(question: str, answer: str) -> Tuple[Dict, Dict]:
    """
    Evaluate the relevance of generated answer following reference implementation

    Args:
        question: Original medical question
        answer: Generated answer to evaluate

    Returns:
        Tuple of (evaluation_result, token_statistics)
    """
    prompt = EVALUATION_PROMPT_TEMPLATE.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="gpt-4o-mini")

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


def calculate_openai_cost(model: str, tokens: Dict) -> float:
    """
    Calculate OpenAI API cost following reference implementation

    Args:
        model: OpenAI model used
        tokens: Token usage statistics

    Returns:
        Estimated cost in USD
    """
    cost = 0.0

    if model == "gpt-4o-mini":
        cost = (
            tokens.get("prompt_tokens", 0) * 0.00015
            + tokens.get("completion_tokens", 0) * 0.0006
        ) / 1000
    elif model == "gpt-4o":
        cost = (
            tokens.get("prompt_tokens", 0) * 0.03
            + tokens.get("completion_tokens", 0) * 0.06
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return cost


def rag(query: str, model: str = "gpt-4o-mini") -> Dict:
    """
    Complete RAG pipeline following reference implementation exactly

    Args:
        query: Medical question
        model: OpenAI model to use for generation

    Returns:
        Complete response with answer, metrics, and metadata
    """
    # Start timing
    t0 = time()

    # Step 1: Search medical knowledge base
    search_results = search(query)

    # Step 2: Build prompt with retrieved context
    prompt = build_prompt(query, search_results)

    # Step 3: Generate answer using LLM
    answer, token_stats = llm(prompt, model=model)

    # Step 4: Evaluate answer relevance
    relevance, rel_token_stats = evaluate_relevance(query, answer)

    # Calculate timing and costs
    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost("gpt-4o-mini", rel_token_stats)
    openai_cost = openai_cost_rag + openai_cost_eval

    # Return comprehensive response data following reference format
    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "No explanation provided"
        ),
        "total_cost": openai_cost,
        "token_stats": {
            "rag_tokens": token_stats,
            "evaluation_tokens": rel_token_stats,
            "total_prompt_tokens": token_stats.get("prompt_tokens", 0)
            + rel_token_stats.get("prompt_tokens", 0),
            "total_completion_tokens": token_stats.get("completion_tokens", 0)
            + rel_token_stats.get("completion_tokens", 0),
        },
        "search_results_count": len(search_results),
        "search_results": search_results[
            :5
        ],  # Include top 5 search results for database storage
    }

    return answer_data


# Backward compatibility function
def quick_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    Quick search function for testing
    """
    return search(query, top_k=top_k)


if __name__ == "__main__":
    # Test example
    query = "What are the symptoms and treatment options for diabetes?"

    print("Testing Medical RAG System")
    print("=" * 50)
    print(f"Query: {query}")

    try:
        # Test search only
        print("\nTesting vector search...")
        results = search(query, top_k=3)
        print(f"Found {len(results)} medical cases")

        for i, result in enumerate(results, 1):
            print(f"Result {i}: Score {result.get('score', 0):.3f}")

        # Test full RAG if API key available
        if OPENAI_API_KEY and OPENAI_API_KEY != "test-key":
            print("\nTesting full RAG pipeline...")
            answer_data = rag(query)
            print(f"Generated answer: {len(answer_data['answer'])} characters")
            print(f"Relevance: {answer_data['relevance']}")
            print(f"Cost: ${answer_data['total_cost']:.4f}")
            print(f"Time: {answer_data['response_time']:.2f}s")
        else:
            print("\nFull RAG requires valid OpenAI API key")

    except Exception as e:
        print(f"Error: {e}")
