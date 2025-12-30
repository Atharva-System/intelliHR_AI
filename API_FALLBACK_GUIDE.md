# 🛡️ API Fallback System - Developer Guide

## Overview

This document explains how TalentPulse-AI's intelligent API fallback system works, answering the common question: **"How does an agent using `GoogleGenerativeAI` actually call OpenAI?"**

---

## 🎯 The Problem

When using AI APIs in production, you face several challenges:
- **Quota Limits** - API keys have daily/monthly limits
- **Rate Limiting** - Too many requests can cause temporary blocks
- **Service Interruptions** - APIs can experience downtime
- **Cost Management** - Need to use cheaper options when available

Traditional solutions require:
- Manual intervention when quotas are reached
- Code changes to switch between providers
- Downtime while switching APIs
- Complex error handling in every agent

---

## 💡 The Solution

TalentPulse-AI implements a **transparent, zero-downtime fallback system** that:
1. Automatically rotates between multiple Gemini API keys
2. Falls back across different Gemini models
3. Switches to OpenAI when all Gemini options are exhausted
4. Requires **zero code changes** in agents
5. Automatically recovers when quotas reset

---

## 🏗️ How It Works

### Step 1: Monkey Patching (Interception)

At application startup (`config/Settings.py`), the system patches the Google Generative AI SDK:

```python
# Save original method
_original_generate_content = genai.GenerativeModel.generate_content

# Replace with smart version
genai.GenerativeModel.generate_content = _smart_generate_content
```

**What this means:** Every time ANY code calls `genai.GenerativeModel.generate_content()`, it actually calls our custom `_smart_generate_content()` function instead.

### Step 2: Agent Definition (No Changes Needed)

Agents are defined normally using LangChain's `GoogleGenerativeAI`:

```python
# agents/ai_feedback.py
from langchain_google_genai import GoogleGenerativeAI

llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=settings.api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)
```

**Important:** The agent doesn't know about the fallback system!

### Step 3: Execution Flow

When an agent makes a request:

```
User Request
    ↓
enhance_feedback(request)
    ↓
chain.invoke({"text": "...", "context": "..."})
    ↓
llm.invoke(prompt)  ← LangChain's GoogleGenerativeAI
    ↓
genai.GenerativeModel.generate_content(prompt)  ← Google's SDK
    ↓
🚨 INTERCEPTED! 🚨
    ↓
_smart_generate_content(self, *args, **kwargs)  ← Our custom function
    ↓
[Decision Logic - See below]
    ↓
Response (looks like Gemini response)
    ↓
LangChain processes response
    ↓
Agent receives result
```

### Step 4: Smart Decision Logic

Inside `_smart_generate_content()`:

```python
def _smart_generate_content(self, *args, **kwargs):
    # 1. Check if all APIs have failed
    if settings.all_apis_failed:
        raise QuotaLimitError("All API keys exhausted")
    
    # 2. Periodic check (every hour) - try to restore primary keys
    if time.time() - settings.last_check_time > 3600:
        find_best_config()  # Attempt to restore
    
    # 3. Check if in OpenAI fallback mode
    if settings.api_key == "OPENAI_FALLBACK_MODE":
        return call_openai_fallback(prompt, agent_name)
    
    # 4. Try Gemini API call
    try:
        response = _original_generate_content(self, *args, **kwargs)
        log_token_usage(response)
        return response
    except QuotaError:
        # 5. Rotate to next available config
        find_best_config()
        
        # Check if we switched to OpenAI
        if settings.api_key == "OPENAI_FALLBACK_MODE":
            return call_openai_fallback(prompt, agent_name)
        
        # Retry with new Gemini config
        new_model = genai.GenerativeModel(settings.model)
        return _original_generate_content(new_model, *args, **kwargs)
```

---

## 🔄 Fallback Scenarios

### Scenario A: Normal Operation
```
┌─────────────────────────────────────┐
│ Agent calls llm.invoke()            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ _smart_generate_content() checks:   │
│ ✓ Not in fallback mode              │
│ ✓ API not failed                    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Call Gemini API (API_KEY_1)         │
│ Model: gemini-2.5-flash             │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ ✅ Success! Return response          │
└─────────────────────────────────────┘
```

### Scenario B: Quota Exceeded - Key Rotation
```
┌─────────────────────────────────────┐
│ Agent calls llm.invoke()            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Call Gemini API (API_KEY_1)         │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ ❌ 429 Error: Quota Exceeded         │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ find_best_config() tests:           │
│ ❌ API_KEY_1 + gemini-2.5-flash      │
│ ❌ API_KEY_1 + gemini-1.5-flash      │
│ ✅ API_KEY_2 + gemini-2.5-flash      │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Update: settings.api_key = API_KEY_2│
│         settings.model = 2.5-flash  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Retry with new config               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ ✅ Success! Return response          │
└─────────────────────────────────────┘
```

### Scenario C: All Gemini Keys Exhausted
```
┌─────────────────────────────────────┐
│ Agent calls llm.invoke()            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ All Gemini keys tested and failed  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ find_best_config() sets:            │
│ settings.api_key =                  │
│   "OPENAI_FALLBACK_MODE"            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ _smart_generate_content() detects  │
│ fallback mode                       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ call_openai_fallback():             │
│ 1. Extract prompt from args         │
│ 2. Convert to OpenAI format         │
│ 3. Call OpenAI API (gpt-4o-mini)    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Transform OpenAI response:          │
│ MockGeminiResponse(                 │
│   text=openai_response,             │
│   usage_metadata=converted_usage    │
│ )                                   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Return to LangChain                 │
│ (thinks it's a Gemini response!)    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ ✅ Agent receives response           │
│ (unaware of OpenAI switch)          │
└─────────────────────────────────────┘
```

---

## 🎭 Response Transformation Magic

### The Challenge
OpenAI and Gemini have different response formats:

**OpenAI Response:**
```python
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "This is the AI response"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

**Gemini Response:**
```python
{
  "text": "This is the AI response",
  "candidates": [
    {
      "content": {
        "parts": [
          {"text": "This is the AI response"}
        ]
      }
    }
  ],
  "usage_metadata": {
    "prompt_token_count": 150,
    "candidates_token_count": 75,
    "total_token_count": 225
  }
}
```

### The Solution: Mock Objects

We create mock classes that mimic Gemini's structure:

```python
class MockPart:
    def __init__(self, text):
        self.text = text

class MockContent:
    def __init__(self, text):
        self.parts = [MockPart(text)]

class MockCandidate:
    def __init__(self, text):
        self.content = MockContent(text)

class MockGeminiResponse:
    def __init__(self, text, usage):
        self.text = text
        self.usage_metadata = usage
        self.candidates = [MockCandidate(text)]
```

### Transformation Process

```python
def call_openai_fallback(prompt, agent_name):
    # 1. Call OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 2. Extract content
    content = response.choices[0].message.content
    usage = response.usage
    
    # 3. Map usage to Gemini format
    gemini_usage = type('Usage', (), {})()
    gemini_usage.prompt_token_count = usage.prompt_tokens
    gemini_usage.candidates_token_count = usage.completion_tokens
    gemini_usage.total_token_count = usage.total_tokens
    
    # 4. Create mock Gemini response
    return MockGeminiResponse(content, gemini_usage)
```

**Result:** LangChain receives an object that looks, walks, and quacks like a Gemini response!

---

## 🔑 Key Insights

### 1. **Constructor Parameters Are Ignored During Fallback**

```python
# This is what you write:
llm = GoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSy...",
    temperature=0.2
)

# But during fallback, these are IGNORED!
# The system uses:
# - settings.api_key (global state)
# - settings.model (global state)
# - settings.temperature (global state)
```

### 2. **Interception Happens at SDK Level, Not LangChain Level**

```python
# LangChain's GoogleGenerativeAI internally calls:
genai.GenerativeModel(model_name).generate_content(prompt)

# We intercept at THIS level ↑
# Not at the LangChain level
```

### 3. **The Agent Never Knows**

From the agent's perspective:
- It created a `GoogleGenerativeAI` instance
- It invoked it with a prompt
- It received a Gemini-like response
- Everything worked normally

The agent has **zero awareness** of:
- Which API key was used
- Whether it was Gemini or OpenAI
- Any quota errors or retries
- The fallback mechanism

---

## ⚙️ Configuration

### Environment Variables

```env
# Multiple Gemini keys (tested in order)
API_KEY_1=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
API_KEY_2=AIzaSyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
API_KEY_3=AIzaSyZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ

# OpenAI fallback
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Model preference
MODEL=gemini-2.5-flash

# Other settings
TEMPERATURE=0.2
MAX_OUTPUT_TOKENS=10000
```

### Fallback Priority

1. **API_KEY_1** + **gemini-2.5-flash**
2. **API_KEY_1** + **gemini-1.5-flash**
3. **API_KEY_1** + **gemini-1.5-pro**
4. **API_KEY_2** + **gemini-2.5-flash**
5. **API_KEY_2** + **gemini-1.5-flash**
6. **API_KEY_2** + **gemini-1.5-pro**
7. **API_KEY_3** + **gemini-2.5-flash**
8. **API_KEY_3** + **gemini-1.5-flash**
9. **API_KEY_3** + **gemini-1.5-pro**
10. **OPENAI_API_KEY** + **gpt-4o-mini**

---

## 📊 Monitoring

### Log Messages

**Startup:**
```log
🔄 Checking for best available API key and Model...
  > Testing Model: gemini-2.5-flash
✅ Found working config: Model=gemini-2.5-flash, Key=#1 (AIzaSy***)
✅ Smart API Key Rotation initialized.
```

**Normal Operation:**
```log
[ai_feedback] Input Tokens: 245 | Output Tokens: 128 | Total: 373
```

**Key Rotation:**
```log
⚠️ Quota exceeded. Initiating full rotation strategy...
✅ Found working config: Model=gemini-1.5-flash, Key=#2 (AIzaSy***)
```

**OpenAI Fallback:**
```log
⚠️ All Gemini keys/models failed. Switching to OpenAI Fallback Mode.
⚠️ All Gemini keys failed. Falling back to OpenAI (gpt-4o-mini) for agent: ai_feedback
[ai_feedback] (OpenAI Fallback) Input Tokens: 245 | Output Tokens: 128 | Total: 373
```

**Complete Failure:**
```log
❌ All API keys have reached their quota limit. Request rejected.
```

**Automatic Recovery:**
```log
🕐 1 Hour passed. Attempting to restore primary Gemini keys/models...
✅ Found working config: Model=gemini-2.5-flash, Key=#1 (AIzaSy***)
```

---

## 🚨 Error Handling

### In Your Code

```python
from config.Settings import QuotaLimitError

try:
    result = enhance_feedback(request)
    return {"success": True, "data": result}
except QuotaLimitError as e:
    # All APIs exhausted
    return {
        "success": False,
        "error": "Service temporarily unavailable. Please try again later.",
        "code": "QUOTA_EXCEEDED"
    }
except Exception as e:
    # Other errors
    return {
        "success": False,
        "error": str(e),
        "code": "INTERNAL_ERROR"
    }
```

---

## ✅ Benefits

| Feature | Benefit |
|---------|---------|
| **Zero Downtime** | Service continues even when quotas are reached |
| **Transparent** | No code changes needed in agents |
| **Cost Optimized** | Uses cheaper Gemini models first |
| **Resilient** | Multiple fallback layers |
| **Self-Healing** | Automatically recovers when quotas reset |
| **Observable** | Comprehensive logging of all operations |
| **Flexible** | Easy to add more keys or models |

---

## 🔧 Troubleshooting

### Issue: "All API keys have reached their quota limit"

**Solution:**
1. Check if any API keys have available quota
2. Wait for quota reset (usually daily)
3. Add more API keys to `.env`
4. Check OpenAI API key is valid

### Issue: Unexpected API provider being used

**Solution:**
1. Check `app.log` for current configuration
2. Verify which keys are exhausted
3. Check `settings.api_key` value:
   - Actual key = Using Gemini
   - `"OPENAI_FALLBACK_MODE"` = Using OpenAI
   - `"ALL_APIS_FAILED"` = All exhausted

### Issue: Token counts seem wrong

**Solution:**
- Token counting differs between Gemini and OpenAI
- This is expected and logged appropriately
- Check logs for which provider was used

---

## 🎓 Summary

**Question:** How does an agent using `GoogleGenerativeAI` call OpenAI?

**Answer:** 
1. The system **monkey patches** `google.generativeai` at startup
2. All calls to `genai.GenerativeModel.generate_content()` are **intercepted**
3. The interceptor checks global state (`settings.api_key`)
4. If in fallback mode, it **routes to OpenAI** instead
5. OpenAI response is **transformed** to look like Gemini
6. LangChain and the agent **never know** the difference

**The magic:** Transparent interception + response transformation = Zero-code fallback! 🎭

---

## 📚 Related Files

- `config/Settings.py` - Main fallback logic
- `agents/*.py` - All agents (use system transparently)
- `app.log` - Runtime logs
- `.env` - API key configuration

---

**Built with ❤️ for resilient AI applications**
