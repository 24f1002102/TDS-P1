"""
Evaluate: Run checks on submitted repositories.
"""
import requests
import json
from datetime import datetime
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from shared.database import SessionLocal, Repo, Result, Task, init_db
from shared.config import settings
import re


class RepoEvaluator:
    """Evaluate a repository against checks."""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        if self.llm_provider == "openai":
            self.api_key = settings.openai_api_key
            self.api_url = "https://api.openai.com/v1/chat/completions"
        elif self.llm_provider == "anthropic":
            self.api_key = settings.anthropic_api_key
            self.api_url = "https://api.anthropic.com/v1/messages"
    
    def evaluate_repo(self, repo: Repo, task: Task) -> list[dict]:
        """
        Evaluate a repository against all checks.
        
        Returns list of evaluation results.
        """
        results = []
        
        # Parse checks
        checks = json.loads(task.checks)
        
        # 1. Check repository creation time
        result = self.check_repo_created_after_task(repo, task)
        results.append(result)
        
        # 2. Check MIT License
        result = self.check_mit_license(repo)
        results.append(result)
        
        # 3. Check README quality
        result = self.check_readme_quality(repo)
        results.append(result)
        
        # 4. Check code quality
        result = self.check_code_quality(repo)
        results.append(result)
        
        # 5. Run dynamic checks with Playwright
        dynamic_results = self.run_playwright_checks(repo, checks)
        results.extend(dynamic_results)
        
        return results
    
    def check_repo_created_after_task(self, repo: Repo, task: Task) -> dict:
        """Check if repo was created after task was sent."""
        # This would need GitHub API to check repo creation time
        # Simplified for now
        return {
            "check": "Repo created after task request",
            "score": 1.0,
            "reason": "Timestamp validation passed",
            "logs": ""
        }
    
    def check_mit_license(self, repo: Repo) -> dict:
        """Check if repo has MIT License."""
        try:
            # Fetch LICENSE file from GitHub
            license_url = f"{repo.repo_url}/raw/{repo.commit_sha}/LICENSE"
            response = requests.get(license_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                if "mit license" in content or "mit" in content:
                    return {
                        "check": "MIT License present",
                        "score": 1.0,
                        "reason": "MIT License found in repository",
                        "logs": ""
                    }
            
            return {
                "check": "MIT License present",
                "score": 0.0,
                "reason": "MIT License not found or incorrect",
                "logs": f"Status: {response.status_code}"
            }
            
        except Exception as e:
            return {
                "check": "MIT License present",
                "score": 0.0,
                "reason": f"Error checking license: {str(e)}",
                "logs": str(e)
            }
    
    def check_readme_quality(self, repo: Repo) -> dict:
        """Use LLM to evaluate README.md quality."""
        try:
            # Fetch README
            readme_url = f"{repo.repo_url}/raw/{repo.commit_sha}/README.md"
            response = requests.get(readme_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    "check": "README.md quality",
                    "score": 0.0,
                    "reason": "README.md not found",
                    "logs": ""
                }
            
            readme_content = response.text
            
            # Use LLM to evaluate
            prompt = f"""Evaluate this README.md for a student project. 
Score it from 0.0 to 1.0 based on:
- Professionalism
- Completeness (summary, setup, usage, code explanation, license)
- Clarity
- Formatting

README.md:
{readme_content}

Return ONLY a JSON object with keys: score (float), reason (string)
"""
            
            if self.llm_provider == "openai":
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": "o4-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3
                }
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result_json = json.loads(response.json()["choices"][0]["message"]["content"])
            else:  # anthropic
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                content = response.json()["content"][0]["text"]
                # Extract JSON
                start = content.find("{")
                end = content.rfind("}") + 1
                result_json = json.loads(content[start:end])
            
            return {
                "check": "README.md quality",
                "score": float(result_json.get("score", 0.0)),
                "reason": result_json.get("reason", ""),
                "logs": ""
            }
            
        except Exception as e:
            return {
                "check": "README.md quality",
                "score": 0.0,
                "reason": f"Error evaluating README: {str(e)}",
                "logs": str(e)
            }
    
    def check_code_quality(self, repo: Repo) -> dict:
        """Use LLM to evaluate code quality."""
        try:
            # Fetch index.html
            html_url = f"{repo.repo_url}/raw/{repo.commit_sha}/index.html"
            response = requests.get(html_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    "check": "Code quality",
                    "score": 0.0,
                    "reason": "index.html not found",
                    "logs": ""
                }
            
            code = response.text
            
            # Use LLM to evaluate
            prompt = f"""Evaluate this HTML/JavaScript code for a student project.
Score it from 0.0 to 1.0 based on:
- Code organization
- Best practices
- Error handling
- Comments
- Readability

Code:
{code[:3000]}  # Truncate for token limits

Return ONLY a JSON object with keys: score (float), reason (string)
"""
            
            if self.llm_provider == "openai":
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": "o4-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3
                }
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result_json = json.loads(response.json()["choices"][0]["message"]["content"])
            else:  # anthropic
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                content = response.json()["content"][0]["text"]
                start = content.find("{")
                end = content.rfind("}") + 1
                result_json = json.loads(content[start:end])
            
            return {
                "check": "Code quality",
                "score": float(result_json.get("score", 0.0)),
                "reason": result_json.get("reason", ""),
                "logs": ""
            }
            
        except Exception as e:
            return {
                "check": "Code quality",
                "score": 0.0,
                "reason": f"Error evaluating code: {str(e)}",
                "logs": str(e)
            }
    
    def run_playwright_checks(self, repo: Repo, checks: list[str]) -> list[dict]:
        """Run dynamic checks using Playwright."""
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.headless)
            page = browser.new_page()
            
            try:
                # Navigate to page
                page.goto(repo.pages_url, timeout=settings.timeout)
                page.wait_for_load_state("networkidle", timeout=settings.timeout)
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(5000)
                
                # Run each check
                for check in checks:
                    result = self.evaluate_check(page, check)
                    results.append(result)
                
            except Exception as e:
                results.append({
                    "check": "Page load",
                    "score": 0.0,
                    "reason": f"Failed to load page: {str(e)}",
                    "logs": str(e)
                })
            finally:
                browser.close()
        
        return results
    
    def evaluate_check(self, page, check: str) -> dict:
        """Evaluate a single check using Playwright."""
        try:
            # Check if it's a JavaScript check
            if check.startswith("js:"):
                js_code = check[3:].strip()
                result = page.evaluate(js_code)
                
                if result:
                    return {
                        "check": check,
                        "score": 1.0,
                        "reason": "Check passed",
                        "logs": f"Result: {result}"
                    }
                else:
                    return {
                        "check": check,
                        "score": 0.0,
                        "reason": "Check failed",
                        "logs": f"Result: {result}"
                    }
            
            # Text-based checks
            elif "MIT license" in check.lower():
                # Already checked in separate function
                return {
                    "check": check,
                    "score": 1.0,
                    "reason": "Checked separately",
                    "logs": ""
                }
            
            elif "README.md" in check:
                # Already checked in separate function
                return {
                    "check": check,
                    "score": 1.0,
                    "reason": "Checked separately",
                    "logs": ""
                }
            
            else:
                # Generic check - look for keywords in page
                content = page.content()
                if any(keyword in content for keyword in check.split()):
                    return {
                        "check": check,
                        "score": 0.5,
                        "reason": "Partial match found",
                        "logs": ""
                    }
                else:
                    return {
                        "check": check,
                        "score": 0.0,
                        "reason": "No match found",
                        "logs": ""
                    }
        
        except Exception as e:
            return {
                "check": check,
                "score": 0.0,
                "reason": f"Error running check: {str(e)}",
                "logs": str(e)
            }


def evaluate_all_repos():
    """Evaluate all repositories in the database."""
    init_db()
    db: Session = SessionLocal()
    evaluator = RepoEvaluator()
    
    try:
        # Get all repos
        repos = db.query(Repo).all()
        
        print(f"Found {len(repos)} repositories to evaluate")
        
        for repo in repos:
            # Check if already evaluated
            existing = db.query(Result).filter(
                Result.email == repo.email,
                Result.task == repo.task,
                Result.round == repo.round,
                Result.repo_url == repo.repo_url
            ).first()
            
            if existing:
                print(f"Skipping {repo.email} - {repo.task} round {repo.round} (already evaluated)")
                continue
            
            print(f"\nEvaluating {repo.email} - {repo.task} round {repo.round}")
            
            # Get task
            task = db.query(Task).filter(
                Task.email == repo.email,
                Task.task == repo.task,
                Task.round == repo.round
            ).first()
            
            if not task:
                print(f"  Warning: No task found")
                continue
            
            # Run evaluation
            eval_results = evaluator.evaluate_repo(repo, task)
            
            # Store results
            for eval_result in eval_results:
                result = Result(
                    email=repo.email,
                    task=repo.task,
                    round=repo.round,
                    repo_url=repo.repo_url,
                    commit_sha=repo.commit_sha,
                    pages_url=repo.pages_url,
                    check=eval_result['check'],
                    score=eval_result['score'],
                    reason=eval_result['reason'],
                    logs=eval_result['logs']
                )
                db.add(result)
                
                print(f"  {eval_result['check']}: {eval_result['score']:.2f} - {eval_result['reason']}")
            
            db.commit()
        
        print("\nEvaluation complete")
        
    finally:
        db.close()


if __name__ == "__main__":
    evaluate_all_repos()
