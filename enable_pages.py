#!/usr/bin/env python3
"""
Script to enable GitHub Pages for a repository.
"""
import sys
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def enable_pages(repo_name):
    """Enable GitHub Pages for a repository."""
    github_token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USERNAME")
    
    if not github_token or not github_username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found in .env")
        return False
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Enable Pages
    pages_data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    print(f"Enabling GitHub Pages for {github_username}/{repo_name}...")
    
    response = requests.post(
        f"https://api.github.com/repos/{github_username}/{repo_name}/pages",
        headers=headers,
        json=pages_data
    )
    
    if response.status_code == 201:
        print("✅ GitHub Pages enabled successfully!")
        print(f"📄 URL: https://{github_username}.github.io/{repo_name}/")
        return True
    elif response.status_code == 409:
        print("✅ GitHub Pages already enabled!")
        print(f"📄 URL: https://{github_username}.github.io/{repo_name}/")
        return True
    else:
        print(f"❌ Failed to enable GitHub Pages: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python enable_pages.py <repo-name>")
        print("Example: python enable_pages.py test-hello-1234-r1")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    success = enable_pages(repo_name)
    sys.exit(0 if success else 1)
