"""
LLM-based code generator for creating applications based on briefs.
"""
import json
import requests
from typing import List, Dict, Optional
from shared.models import Attachment
from shared.config import settings


class LLMGenerator:
    """Generate application code using LLM."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        if self.provider == "openai":
            self.api_key = settings.openai_api_key
            self.api_url = "https://aipipe.org/openai/v1/chat/completions"
            self.model = "gpt-4o-mini"  # Using o4-mini as requested
        elif self.provider == "anthropic":
            self.api_key = settings.anthropic_api_key
            self.api_url = "https://api.anthropic.com/v1/messages"
            self.model = "claude-3-sonnet-20240229"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_app(
        self,
        brief: str,
        checks: List[str],
        attachments: Optional[List[Attachment]] = None
    ) -> Dict[str, str]:
        """
        Generate application files based on the brief.
        
        Returns:
            Dict mapping filenames to their content
        """
        # Build prompt
        prompt = self._build_prompt(brief, checks, attachments or [])
        
        # Generate code
        if self.provider == "openai":
            return self._generate_with_openai(prompt)
        else:
            return self._generate_with_anthropic(prompt)
    
    def _build_prompt(
        self,
        brief: str,
        checks: List[str],
        attachments: List[Attachment]
    ) -> str:
        """Build the prompt for the LLM."""
        
        attachments_text = ""
        if attachments:
            attachments_text = "\n\nAttachments:\n"
            for att in attachments:
                attachments_text += f"- {att.name}: {att.url[:100]}...\n"
        
        checks_text = "\n".join(f"- {check}" for check in checks)
        
        prompt = f"""You are an expert web developer. Create a complete, minimal, single-page web application based on the following requirements.

**Brief**: {brief}

**Checks that must pass**:
{checks_text}
{attachments_text}

**Requirements**:
1. Create a single-page HTML application (index.html)
2. Include all CSS inline in a <style> tag
3. Include all JavaScript inline in a <script> tag
4. Use modern, clean, responsive design
5. Ensure all checks will pass
6. Handle attachments by fetching them from the provided data URIs
7. Use Bootstrap 5 from CDN if needed for styling
8. Make it functional and production-ready
9. Include proper error handling
10. Add comments explaining key functionality

**IMPORTANT OUTPUT FORMAT**:
You must respond with ONLY valid JSON in this exact format:
{{
  "files": {{
    "index.html": "<!DOCTYPE html>...",
    "README.md": "# Project Title\\n\\nDescription..."
  }}
}}

Do not include any text before or after the JSON. The JSON must be valid and parseable.
The index.html must be complete and functional.
The README.md must include:
- Project title and description
- Setup instructions
- Usage instructions
- Brief code explanation
- MIT License reference

Generate the complete application now:"""
        
        return prompt
    
    def _generate_with_openai(self, prompt: str) -> Dict[str, str]:
        """Generate using OpenAI API via HTTP request."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert web developer who creates production-ready single-page applications. You always respond with valid JSON containing the file contents."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        print(f"Calling AI pipe at: {self.api_url}")
        print(f"Using model: {self.model}")
        print(f"API key (first 20 chars): {self.api_key[:20]}...")
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            # Log response details for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"Error response body: {response.text}")
                
            response.raise_for_status()
            
            result = response.json()
            print(f"Response structure: {list(result.keys())}")
            
            # Extract content
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
            elif "content" in result:
                # Alternative format some APIs use
                content = result["content"]
            else:
                raise ValueError(f"Unexpected API response format: {list(result.keys())}")
            
            print(f"Generated content length: {len(content)} characters")
            
            # Parse the JSON response
            files = self._parse_response(content)
            
            # Ensure we have required files
            if "index.html" not in files:
                raise ValueError("Generated code missing index.html")
            if "README.md" not in files:
                files["README.md"] = self._generate_default_readme()
            
            # Add LICENSE file
            files["LICENSE"] = self._get_mit_license()
            
            return files
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error calling AI pipe: {e}")
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error calling AI pipe: {e}")
            raise
        except Exception as e:
            print(f"Error calling AI pipe: {e}")
            raise
    
    def _generate_with_anthropic(self, prompt: str) -> Dict[str, str]:
        """Generate using Anthropic API via HTTP request."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content from Anthropic response
            content = result["content"][0]["text"]
            
            # Parse the JSON response
            files = self._parse_response(content)
            
            # Ensure we have required files
            if "index.html" not in files:
                raise ValueError("Generated code missing index.html")
            if "README.md" not in files:
                files["README.md"] = self._generate_default_readme()
            
            # Add LICENSE file
            files["LICENSE"] = self._get_mit_license()
            
            return files
            
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            raise
    
    def _parse_response(self, content: str) -> Dict[str, str]:
        """Parse the LLM response to extract files."""
        try:
            # Try to find JSON in the response
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Extract files
            if "files" in data:
                return data["files"]
            else:
                # Assume the entire response is the files dict
                return data
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Content preview: {content[:500]}")
            
            # Fallback: try to extract code manually
            return self._extract_files_manually(content)
    
    def _extract_files_manually(self, content: str) -> Dict[str, str]:
        """Manually extract files if JSON parsing fails."""
        files = {}
        
        # Try to find HTML
        if "<!DOCTYPE html>" in content or "<html" in content:
            # Extract everything that looks like HTML
            start = content.find("<!DOCTYPE html>") if "<!DOCTYPE html>" in content else content.find("<html")
            end = content.rfind("</html>") + 7
            if start != -1 and end > start:
                files["index.html"] = content[start:end]
        
        # Generate minimal files if extraction failed
        if "index.html" not in files:
            files["index.html"] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1 id="greeting">Hello World</h1>
    <p>This is a minimal generated application.</p>
</body>
</html>"""
        
        files["README.md"] = self._generate_default_readme()
        
        return files
    
    def _generate_default_readme(self) -> str:
        """Generate a default README.md."""
        return """# Generated Application

This application was automatically generated based on the provided requirements.

## Setup

No setup required. Simply open `index.html` in a web browser.

## Usage

Open the application in any modern web browser. The application is self-contained with all dependencies included.

## Code Explanation

The application consists of a single HTML file with embedded CSS and JavaScript for simplicity and portability.

## License

MIT License - See LICENSE file for details.
"""
    
    def _get_mit_license(self) -> str:
        """Return MIT License text."""
        return """MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
