# Multi-Task Text Utility - Customer Support Helper

A production-ready AI-powered customer support assistant that provides structured JSON responses with comprehensive metrics tracking and safety features.

## 🎯 Overview

This system helps customer support agents by analyzing incoming questions and returning structured, actionable responses with confidence scores, recommended actions, and performance metrics. It's designed for reliability, observability, and safe operation.

## ✨ Features

- **Structured JSON Output**: Consistent response format with answer, confidence, actions, category, and escalation flag
- **Comprehensive Metrics**: Track tokens, latency, and costs per query
- **Safety Layer**: Built-in content moderation and adversarial prompt detection
- **Prompt Engineering**: Uses instruction-based prompting with few-shot examples and JSON schema enforcement
- **Dual Logging**: Metrics saved in both JSON and CSV formats for analysis
- **Full Test Coverage**: Automated tests for validation, metrics, and safety

## 📝 Recorded Runs & Evidence

**See `RECORDED_RUNS.md`** for documented evidence of:
- ✅ Multiple recorded runs producing valid JSON
- ✅ Metrics logged to `metrics/metrics.json` and `metrics/metrics.csv`
- ✅ Sample output saved in `sample_output.json`
- ✅ Complete token counts, latency measurements, and cost calculations

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in `requirements.txt`

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd henry_task_01

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

**Important**: Never commit your actual API key. The `.env` file is gitignored.

### 3. Run the Application

#### Run with default test questions:

```bash
cd src
python run_query.py
```

#### Run with a specific question:

```bash
cd src
python run_query.py "How do I cancel my subscription?"
```

#### Or use as a module:

```python
from run_query import CustomerSupportHelper

helper = CustomerSupportHelper()
result = helper.process_query("How do I reset my password?")
print(result)
```

## 📊 Sample Output

```json
{
  "status": "success",
  "data": {
    "answer": "To reset your password, click 'Forgot Password' on the login page, enter your email, and follow the instructions in the reset email (check spam folder if needed).",
    "confidence": 0.95,
    "actions": [
      "Send password reset link to customer's email",
      "Verify email address is correct in system",
      "Ask customer to check spam folder"
    ],
    "category": "account",
    "requires_escalation": false
  },
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt": 423,
      "completion": 87,
      "total": 510
    },
    "latency_ms": 1247.32,
    "estimated_cost_usd": 0.000116
  }
}
```

## 📈 Metrics Tracking

Metrics are automatically logged to:
- `metrics/metrics.json` - Detailed JSON log
- `metrics/metrics.csv` - CSV format for spreadsheet analysis

Each entry includes:
- Timestamp
- Question (truncated)
- Model used
- Token counts (prompt, completion, total)
- Latency in milliseconds
- Estimated cost in USD
- Safety flags

### View Summary Statistics

```python
from metrics_logger import MetricsLogger

logger = MetricsLogger()
summary = logger.get_summary_statistics()
print(summary)
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/test_core.py -v

# Run with coverage
pytest tests/test_core.py -v --cov=src --cov-report=html

# Run specific test class
pytest tests/test_core.py::TestJSONValidation -v
```

Tests cover:
- ✅ JSON schema validation
- ✅ Token counting and cost calculation
- ✅ Metrics logging
- ✅ Safety/moderation checks
- ✅ Error handling
- ✅ Response structure validation

## 🛡️ Safety Features

The system includes two layers of safety:

### 1. Content Moderation (OpenAI Moderation API)
Checks for:
- Hate speech
- Self-harm content
- Sexual content
- Violence
- Other harmful categories

### 2. Adversarial Prompt Detection
Detects injection attempts like:
- "Ignore previous instructions"
- "You are now..."
- "Disregard all rules"
- System prompt overrides

### Testing Safety Features

```bash
cd src
python safety.py
```

## 🎨 Prompt Engineering Techniques

This implementation uses **multiple prompt engineering techniques**:

### 1. Instruction-Based Prompting
Clear, explicit instructions for task and format

### 2. Few-Shot Learning
Three diverse examples covering:
- Simple technical questions
- Billing concerns
- Complex technical issues

### 3. JSON Schema Enforcement
- Explicit JSON structure definition
- Field-by-field specifications
- OpenAI's JSON mode enabled

### 4. Chain-of-Thought Guidance
Embedded reasoning in examples showing:
- How to assess confidence
- When to escalate
- How to categorize issues

See `prompts/main_prompt.txt` for the complete prompt template.

## 📁 Project Structure

```
henry_task_01/
├── src/
│   ├── run_query.py          # Main application
│   ├── metrics_logger.py     # Metrics tracking
│   ├── safety.py             # Safety/moderation
│   └── __init__.py
├── tests/
│   ├── test_core.py          # Automated tests
│   └── __init__.py
├── prompts/
│   └── main_prompt.txt       # Prompt template
├── metrics/                  # Generated metrics logs
│   ├── metrics.json
│   └── metrics.csv
├── reports/
│   └── PI_report_en.md       # Technical report
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## 💰 Cost Estimates

Using `gpt-4o-mini` (default):
- ~$0.00015 per 1K prompt tokens
- ~$0.0006 per 1K completion tokens
- Typical query: 400-600 tokens total
- **Average cost per query: $0.0001-0.0003** (0.01-0.03 cents)

For 1000 queries/day:
- ~$0.10-0.30 per day
- ~$3-9 per month

## 🔧 Configuration Options

Edit values in `src/run_query.py`:

```python
# Change model (affects cost/quality)
self.model = "gpt-4o-mini"  # Options: gpt-4o, gpt-4o-mini, gpt-3.5-turbo

# Adjust temperature (creativity)
temperature=0.7  # Lower = more consistent, Higher = more creative

# Adjust max tokens (response length)
max_tokens=500  # Increase for longer responses
```

## 🐛 Troubleshooting

### API Key Issues
```
Error: OPENAI_API_KEY not found
```
**Solution**: Ensure `.env` file exists with valid API key

### Module Import Errors
```
ModuleNotFoundError: No module named 'openai'
```
**Solution**: Run `pip install -r requirements.txt`

### Test Failures
```
SKIPPED - OPENAI_API_KEY not set
```
**Solution**: This is expected for integration tests without API key. Unit tests will still run.

## 🚧 Known Limitations

1. **Rate Limits**: Subject to OpenAI API rate limits
2. **Language**: Optimized for English; other languages may have reduced quality
3. **Context**: No conversation history; each query is independent
4. **Latency**: Network-dependent; typical 1-3 seconds per query

## 🔮 Future Improvements

- Add conversation history/context management
- Implement caching for common questions
- Support multiple languages
- Add custom fine-tuning for domain-specific knowledge
- Implement fallback to local models
- Add A/B testing framework for prompt variants
- Real-time dashboard for metrics visualization

## 📚 Documentation

- **Technical Report**: See `reports/PI_report_en.md` for detailed architecture and analysis
- **Prompt Template**: See `prompts/main_prompt.txt` for prompt engineering details
- **API Documentation**: See OpenAI docs at https://platform.openai.com/docs

## 🤝 Contributing

This is a project submission. For questions or issues:
1. Check the technical report in `reports/PI_report_en.md`
2. Review test cases in `tests/test_core.py`
3. Examine the metrics logs in `metrics/`

## 📝 License

This project is submitted as part of an academic assignment.

## 🙏 Acknowledgments

- OpenAI API for GPT models and moderation
- Assignment requirements from course materials
- Prompt engineering techniques from class lectures

---

**Built with ❤️ for reliable, observable, and safe AI systems**
