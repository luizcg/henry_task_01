# Recorded Runs - Evidence of JSON Output and Metrics

This document provides evidence of at least one recorded run producing JSON and metrics, as required by the assignment.

## Sample Run 1: Password Reset Query

**Command executed:**
```bash
python3 src/run_query.py "How do I reset my password?"
```

**JSON Output:**
```json
{
  "status": "success",
  "data": {
    "answer": "To reset your password, go to the login page and click on 'Forgot Password'. Enter your registered email address, and you will receive instructions to reset your password via email. Make sure to check your spam folder if you don't see the email promptly.",
    "confidence": 0.95,
    "actions": [
      "Send password reset link to the customer's email",
      "Verify the email address is correct in the system",
      "Remind the customer to check their spam folder"
    ],
    "category": "account",
    "requires_escalation": false
  },
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt": 903,
      "completion": 124,
      "total": 1027
    },
    "latency_ms": 4587.28,
    "estimated_cost_usd": 0.00021
  }
}
```

**Corresponding Metrics Entry (from metrics/metrics.csv):**
```csv
timestamp,question,model,tokens_prompt,tokens_completion,total_tokens,latency_ms,estimated_cost_usd,safety_flagged
2025-11-03T03:40:45.296786,How do I reset my password?,gpt-4o-mini,903,124,1027,4587.28,0.00021,False
```

---

## Sample Run 2: Billing Issue Query

**Command executed:**
```bash
python3 src/run_query.py "I was charged twice for the same order"
```

**JSON Output:**
```json
{
  "status": "success",
  "data": {
    "answer": "I apologize for the duplicate charge. This could be a pending authorization or an actual duplicate transaction. I will review your recent transactions to address this issue promptly.",
    "confidence": 0.8,
    "actions": [
      "Review customer's transaction history for the last 14 days",
      "Check for pending vs. completed charges",
      "Initiate refund if duplicate charge is confirmed",
      "Escalate to billing team if issue persists"
    ],
    "category": "billing",
    "requires_escalation": true
  },
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt": 905,
      "completion": 116,
      "total": 1021
    },
    "latency_ms": 5191.31,
    "estimated_cost_usd": 0.000205
  }
}
```

---

## Sample Run 3: General Knowledge Query

**Command executed:**
```bash
python3 src/run_query.py "What is the capital of Brasil?"
```

**JSON Output:**
```json
{
  "status": "success",
  "data": {
    "answer": "The capital of Brazil is Brasília. It was officially inaugurated as the capital in 1960 and is known for its modernist architecture and unique urban planning.",
    "confidence": 0.95,
    "actions": [
      "Provide the customer with additional information about Brasília",
      "Suggest resources for learning more about Brazilian cities",
      "Answer any follow-up questions the customer may have"
    ],
    "category": "general",
    "requires_escalation": false
  },
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt": 903,
      "completion": 104,
      "total": 1007
    },
    "latency_ms": 5041.81,
    "estimated_cost_usd": 0.000198
  }
}
```

---

## Metrics Summary

**Cumulative Statistics (from all recorded runs):**

```bash
Total Queries: 9
Total Cost: $0.001830
Average Cost per Query: $0.000203
Average Latency: 4743.80ms
Total Tokens Used: 9,160
Average Tokens per Query: 1017.8
Safety Flags: 0
```

**Source:** Run `python3 -c "import sys; sys.path.insert(0, 'src'); from metrics_logger import MetricsLogger; print(MetricsLogger().get_summary_statistics())"`

---

## Files Containing Recorded Data

### 1. **Sample Output File**
- Location: `sample_output.json`
- Contains: Complete JSON response from a single run

### 2. **Metrics JSON Log**
- Location: `metrics/metrics.json`
- Contains: Detailed JSON records of all runs
- Fields: timestamp, question, model, tokens, latency, cost, safety flags

### 3. **Metrics CSV Log**
- Location: `metrics/metrics.csv`
- Contains: Same data in CSV format for spreadsheet analysis
- Easily imported into Excel, Google Sheets, or data analysis tools

---

## Verification Steps

To verify these recorded runs yourself:

1. **View the sample JSON output:**
   ```bash
   cat sample_output.json
   ```

2. **View recent metrics entries:**
   ```bash
   tail -10 metrics/metrics.csv
   ```

3. **Generate summary statistics:**
   ```bash
   python3 -c "
   import sys, json
   sys.path.insert(0, 'src')
   from metrics_logger import MetricsLogger
   summary = MetricsLogger().get_summary_statistics()
   print(json.dumps(summary, indent=2))
   "
   ```

4. **Run a new query and observe:**
   ```bash
   python3 src/run_query.py "Your question here"
   ```

---

## Reproducibility

All runs are fully reproducible with the same API key by running:

```bash
python3 src/run_query.py "<your question>"
```

Each run will:
- ✅ Return valid JSON with all 5 required fields
- ✅ Log metrics to both `metrics.json` and `metrics.csv`
- ✅ Track tokens, latency, and estimated cost
- ✅ Optionally perform safety checks

---

**Document generated:** November 3, 2025  
**Model used:** gpt-4o-mini (confirmed working)
