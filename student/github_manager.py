"""
GitHub integration for repository management.
"""
import os
import tempfile
import shutil
from pathlib import Path
from github import Github
from git import Repo
from shared.config import settings


class GitHubManager:
    """Manage GitHub repository operations."""
    
    def __init__(self):
        self.github = Github(settings.github_token)
        self.user = self.github.get_user()
    
    def create_and_deploy_repo(
        self, 
        repo_name: str, 
        files: dict[str, str],
        enable_pages: bool = True
    ) -> tuple[str, str, str]:
        """
        Create a GitHub repository, push files, and optionally enable Pages.
        
        Args:
            repo_name: Name for the new repository
            files: Dictionary of filename: content
            enable_pages: Whether to enable GitHub Pages
            
        Returns:
            Tuple of (repo_url, commit_sha, pages_url)
        """
        # Create repository
        repo = self.user.create_repo(
            name=repo_name,
            private=False,
            auto_init=False,
            description=f"Auto-generated application: {repo_name}"
        )
        
        # Clone to temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            # Initialize git repo
            local_repo = Repo.init(temp_dir)
            
            # Write files
            for filename, content in files.items():
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
            
            # Git operations
            local_repo.git.add(A=True)
            local_repo.index.commit("Initial commit: Auto-generated application")
            
            # Create and checkout main branch explicitly
            try:
                local_repo.git.branch('-M', 'main')
            except:
                # If branch already named main, this will fail, that's ok
                pass
            
            # Add remote and push
            origin = local_repo.create_remote('origin', repo.clone_url.replace(
                'https://',
                f'https://{settings.github_username}:{settings.github_token}@'
            ))
            
            # Push to main branch
            try:
                origin.push(refspec='HEAD:refs/heads/main', force=True)
            except Exception as e:
                print(f"Warning: Push to main failed: {e}")
                # Try pushing to master as fallback
                origin.push(refspec='HEAD:refs/heads/master', force=True)
            
            # Get commit SHA
            commit_sha = local_repo.head.commit.hexsha
            
            # Enable GitHub Pages if requested
            pages_url = f"https://{settings.github_username}.github.io/{repo_name}/"
            if enable_pages:
                try:
                    # Try method 1: Using PyGithub's built-in method
                    repo.create_pages_site(branch="main", path="/")
                    print(f"✅ GitHub Pages enabled via create_pages_site")
                except Exception as e1:
                    print(f"⚠️  create_pages_site failed: {e1}")
                    # Method 2: Direct API call
                    try:
                        import requests
                        headers = {
                            "Authorization": f"token {settings.github_token}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                        pages_data = {
                            "source": {
                                "branch": "main",
                                "path": "/"
                            }
                        }
                        response = requests.post(
                            f"https://api.github.com/repos/{settings.github_username}/{repo_name}/pages",
                            headers=headers,
                            json=pages_data
                        )
                        if response.status_code in [201, 409]:  # 409 means already exists
                            print(f"✅ GitHub Pages enabled via API (status: {response.status_code})")
                        else:
                            print(f"⚠️  GitHub Pages API returned: {response.status_code}")
                            print(f"Response: {response.text}")
                    except Exception as e2:
                        print(f"⚠️  GitHub Pages API call failed: {e2}")
                        print(f"⚠️  You may need to enable Pages manually in repo settings")
            
            return repo.html_url, commit_sha, pages_url
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def update_repo(
        self, 
        repo_name: str, 
        files: dict[str, str]
    ) -> tuple[str, str]:
        """
        Update an existing repository with new files.
        
        Args:
            repo_name: Name of the repository
            files: Dictionary of filename: content
            
        Returns:
            Tuple of (repo_url, commit_sha)
        """
        repo = self.user.get_repo(repo_name)
        
        # Clone to temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            # Clone repository
            local_repo = Repo.clone_from(
                repo.clone_url.replace(
                    'https://',
                    f'https://{settings.github_username}:{settings.github_token}@'
                ),
                temp_dir
            )
            
            # Update files
            for filename, content in files.items():
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
            
            # Git operations
            local_repo.git.add(A=True)
            local_repo.index.commit("Update: Modified application based on new requirements")
            
            # Push changes
            origin = local_repo.remote('origin')
            origin.push()
            
            # Get commit SHA
            commit_sha = local_repo.head.commit.hexsha
            
            return repo.html_url, commit_sha
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def get_repo_url(self, repo_name: str) -> str:
        """Get the URL of a repository."""
        repo = self.user.get_repo(repo_name)
        return repo.html_url
    
    def get_pages_url(self, repo_name: str) -> str:
        """Get the GitHub Pages URL for a repository."""
        return f"https://{settings.github_username}.github.io/{repo_name}/"
