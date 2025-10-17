# OpenAI o4-mini API Usage Guide

## Overview

This project uses direct HTTP requests to the OpenAI API instead of the official Python SDK. This provides better control and reduces dependencies.

## Configuration

In your `.env` file:
```env
OPENAI_API_KEY=sk-your-api-key-here
LLM_PROVIDER=openai
```

## Model Information

- **Model**: `o4-mini`
- **API Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Response Format**: JSON object
- **Temperature**: 0.7 (for generation), 0.3 (for evaluation)
- **Timeout**: 120 seconds (2 minutes)

## HTTP Request Format

### Headers
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
```

### Request Body
```json
{
  "model": "o4-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert web developer. Always return valid JSON."
    },
    {
      "role": "user",
      "content": "Your prompt here"
    }
  ],
  "response_format": {
    "type": "json_object"
  },
  "temperature": 0.7
}
```

### Response Format
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "o4-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"key\": \"value\"}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  }
}
```

## Implementation Details

### In `student/llm_generator.py`

The LLM generator makes HTTP POST requests to generate application code:

1. **Builds prompt** with brief, checks, and attachments
2. **Sends request** to OpenAI API
3. **Parses JSON response** from the model
4. **Ensures required files** (LICENSE, README.md) are included
5. **Returns file dictionary** for GitHub deployment

### In `instructor/evaluate.py`

The evaluator uses HTTP requests for:

1. **README.md quality evaluation** - Scores professionalism and completeness
2. **Code quality evaluation** - Scores organization and best practices

## Error Handling

```python
try:
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=120
    )
    response.raise_for_status()  # Raises HTTPError for bad status codes
    
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    files = json.loads(content)
    
except requests.exceptions.RequestException as e:
    print(f"Error calling OpenAI API: {e}")
    raise
except (KeyError, json.JSONDecodeError) as e:
    print(f"Error parsing OpenAI response: {e}")
    raise
```

## Testing the API

### Using curl
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "o4-mini",
    "messages": [
      {
        "role": "user",
        "content": "Create a simple HTML page with Hello World"
      }
    ],
    "response_format": {"type": "json_object"},
    "temperature": 0.7
  }'
```

### Using Python
```python
import requests
import json

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "o4-mini",
    "messages": [
        {"role": "user", "content": "Test prompt"}
    ],
    "response_format": {"type": "json_object"},
    "temperature": 0.7
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

result = response.json()
print(result["choices"][0]["message"]["content"])
```

## Rate Limits

- **RPM (Requests Per Minute)**: Check your OpenAI account tier
- **TPM (Tokens Per Minute)**: Check your OpenAI account tier
- **Handle rate limits**: Implement exponential backoff if needed

## Cost Optimization

1. **Use appropriate timeout**: 120s for generation, 60s for evaluation
2. **Truncate input**: Code evaluation uses only first 3000 characters
3. **Lower temperature for evaluation**: 0.3 for more deterministic results
4. **Cache results**: Avoid re-evaluating same content

## Switching to Anthropic

If you prefer to use Anthropic Claude instead:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_PROVIDER=anthropic
```

The code automatically switches to:
- **Model**: `claude-3-5-sonnet-20241022`
- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Headers**: Includes `x-api-key` and `anthropic-version`

## Troubleshooting

### Invalid API Key
```
Error: 401 Unauthorized
Solution: Verify OPENAI_API_KEY in .env file
```

### Rate Limit Exceeded
```
Error: 429 Too Many Requests
Solution: Wait and retry, or upgrade API tier
```

### Timeout
```
Error: ReadTimeout
Solution: Increase timeout or retry request
```

### Invalid JSON Response
```
Error: JSONDecodeError
Solution: Check response format, may need to extract JSON from text
```

## References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
