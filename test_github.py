import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USERNAME")

headers = {"Authorization": f"token {token}"}

try:
    response = requests.get(f"https://api.github.com/user", headers=headers)
    response.raise_for_status()
    print("✅ GitHub API connection successful!")
    print(f"Authenticated as: {response.json()['login']}")
    
    # Check repo permissions
    response = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers)
    print(f"Can access repos: {response.status_code == 200}")
except Exception as e:
    print(f"❌ Error: {e}")
