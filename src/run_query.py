#!/usr/bin/env python3
"""
Multi-Task Text Utility - Customer Support Helper
Main script for processing user queries and returning structured JSON responses.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from metrics_logger import MetricsLogger
from safety import SafetyChecker


class CustomerSupportHelper:
    """
    Customer support helper that processes user questions and returns
    structured JSON responses with metrics tracking.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the helper with OpenAI API key.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.metrics_logger = MetricsLogger()
        self.safety_checker = SafetyChecker(self.client)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
        
        # Pricing per 1K tokens (updated November 2025 from openai.com/api/pricing)
        # Converted from per 1M tokens to per 1K tokens (divide by 1000)
        self.pricing = {
            # GPT-5 family (newest flagship models)
            "gpt-5": {"prompt": 0.00125, "completion": 0.01},
            "gpt-5-mini": {"prompt": 0.00025, "completion": 0.002},
            "gpt-5-nano": {"prompt": 0.00005, "completion": 0.0004},
            
            # GPT-4.1 family (improved GPT-4)
            "gpt-4.1": {"prompt": 0.002, "completion": 0.008},
            "gpt-4.1-mini": {"prompt": 0.0004, "completion": 0.0016},
            "gpt-4.1-nano": {"prompt": 0.0001, "completion": 0.0004},
            
            # GPT-4o family (current production models)
            "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
            
            # o-series (reasoning models)
            "o1": {"prompt": 0.015, "completion": 0.06},
            "o1-mini": {"prompt": 0.0011, "completion": 0.0044},
            "o3": {"prompt": 0.002, "completion": 0.008},
            "o3-mini": {"prompt": 0.0011, "completion": 0.0044},
            "o4-mini": {"prompt": 0.0011, "completion": 0.0044},
        }
        self.model = "gpt-4o-mini"  # Default model - proven reliable with JSON mode
    
    def _load_prompt_template(self) -> str:
        """Load the main prompt template from file."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "main_prompt.txt"
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to embedded template
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Return default prompt template if file is not found."""
        return """You are a customer support assistant. Analyze the user's question and provide a helpful response.

Your response MUST be valid JSON with exactly these fields:
- answer: string (concise, helpful answer to the question)
- confidence: float (0.0-1.0, your confidence in the answer)
- actions: array of strings (recommended next steps for the support agent)
- category: string (category of the question: technical, billing, account, general)
- requires_escalation: boolean (true if human escalation is needed)

Question: {question}"""
    
    def _format_prompt(self, question: str) -> str:
        """
        Format the prompt template with the user question.
        
        Args:
            question: User's question
            
        Returns:
            Formatted prompt string
        """
        return self.prompt_template.format(question=question)
    
    def _calculate_cost(
        self, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ) -> float:
        """
        Calculate the estimated cost in USD for the API call.
        
        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Estimated cost in USD
        """
        pricing = self.pricing.get(model, self.pricing["gpt-4o-mini"])
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def process_query(
        self, 
        question: str,
        enable_safety_check: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user question and return structured JSON response with metrics.
        
        This method implements instruction-based prompting with JSON schema enforcement
        and chain-of-thought guidance for complex queries.
        
        Args:
            question: User's question to process
            enable_safety_check: Whether to perform safety moderation check
            
        Returns:
            Dictionary containing the response and metrics
        """
        start_time = time.time()
        
        # Safety check (bonus feature)
        if enable_safety_check:
            safety_result = self.safety_checker.check_content(question)
            if safety_result["flagged"]:
                return self._create_safety_response(question, safety_result, start_time)
        
        # Format prompt with question
        formatted_prompt = self._format_prompt(question)
        
        try:
            # Determine model-specific parameters
            # Newer models (gpt-5, o-series) use max_completion_tokens and temperature=1 only
            is_newer_model = any(self.model.startswith(prefix) for prefix in ["gpt-5", "o1", "o3", "o4"])
            
            # Build API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful customer support assistant. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                "response_format": {"type": "json_object"},
            }
            
            # Add appropriate parameters based on model type
            if is_newer_model:
                api_params["max_completion_tokens"] = 500
                api_params["temperature"] = 1  # Newer models only support temperature=1
            else:
                api_params["max_tokens"] = 500
                api_params["temperature"] = 0.7
            
            # Call OpenAI API with JSON mode for structured output
            response = self.client.chat.completions.create(**api_params)
            
            # Extract response and usage data
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            estimated_cost = self._calculate_cost(
                self.model, 
                prompt_tokens, 
                completion_tokens
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Validate required fields
            required_fields = ["answer", "confidence", "actions", "category", "requires_escalation"]
            if not all(field in result for field in required_fields):
                result = self._ensure_schema(result)
            
            # Log metrics
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "question": question[:100],  # Truncate for logging
                "model": self.model,
                "tokens_prompt": prompt_tokens,
                "tokens_completion": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": round(latency_ms, 2),
                "estimated_cost_usd": round(estimated_cost, 6),
                "safety_flagged": False
            }
            
            self.metrics_logger.log(metrics)
            
            # Combine result with metadata
            full_response = {
                "status": "success",
                "data": result,
                "metadata": {
                    "model": self.model,
                    "tokens": {
                        "prompt": prompt_tokens,
                        "completion": completion_tokens,
                        "total": total_tokens
                    },
                    "latency_ms": round(latency_ms, 2),
                    "estimated_cost_usd": round(estimated_cost, 6)
                }
            }
            
            return full_response
            
        except json.JSONDecodeError as e:
            return self._create_error_response(
                question, 
                f"JSON parsing error: {str(e)}", 
                start_time
            )
        except Exception as e:
            return self._create_error_response(
                question, 
                f"API error: {str(e)}", 
                start_time
            )
    
    def _ensure_schema(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the result has all required fields with defaults."""
        defaults = {
            "answer": result.get("answer", "Unable to provide answer"),
            "confidence": result.get("confidence", 0.5),
            "actions": result.get("actions", ["Review question with supervisor"]),
            "category": result.get("category", "general"),
            "requires_escalation": result.get("requires_escalation", True)
        }
        return defaults
    
    def _create_safety_response(
        self, 
        question: str, 
        safety_result: Dict[str, Any],
        start_time: float
    ) -> Dict[str, Any]:
        """Create response for flagged content."""
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Log safety metrics
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": question[:100],
            "model": "moderation",
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "total_tokens": 0,
            "latency_ms": round(latency_ms, 2),
            "estimated_cost_usd": 0.0,
            "safety_flagged": True,
            "safety_categories": safety_result.get("categories", [])
        }
        
        self.metrics_logger.log(metrics)
        
        return {
            "status": "blocked",
            "data": {
                "answer": "This query has been flagged by our content moderation system.",
                "confidence": 1.0,
                "actions": [
                    "Review content policy with user",
                    "Escalate to content moderation team",
                    "Document incident"
                ],
                "category": "policy_violation",
                "requires_escalation": True
            },
            "metadata": {
                "safety_flagged": True,
                "flagged_categories": safety_result.get("categories", []),
                "latency_ms": round(latency_ms, 2)
            }
        }
    
    def _create_error_response(
        self, 
        question: str, 
        error_message: str,
        start_time: float
    ) -> Dict[str, Any]:
        """Create response for errors."""
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "status": "error",
            "error": error_message,
            "data": {
                "answer": "An error occurred processing your request.",
                "confidence": 0.0,
                "actions": ["Retry request", "Contact technical support"],
                "category": "system_error",
                "requires_escalation": True
            },
            "metadata": {
                "latency_ms": round(latency_ms, 2)
            }
        }


def main():
    """Main entry point for running queries from command line."""
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        # Default test questions
        test_questions = [
            "How do I reset my password?",
            "My account was charged twice for the same transaction",
            "The application keeps crashing when I try to upload files",
            "What are your business hours?",
            "I want to cancel my subscription"
        ]
        
        print("No question provided. Running with test questions...\n")
        
        helper = CustomerSupportHelper()
        
        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"Question: {question}")
            print(f"{'='*60}")
            
            result = helper.process_query(question)
            print(json.dumps(result, indent=2))
            print()
        
        print(f"\n{'='*60}")
        print("Metrics saved to: metrics/metrics.json")
        print(f"{'='*60}")
        return
    
    # Process single question
    helper = CustomerSupportHelper()
    result = helper.process_query(question)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
