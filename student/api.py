"""
Student API endpoint for receiving task requests and deploying apps.
"""
import os
import asyncio
import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from shared.models import TaskRequest, RepoSubmission
from shared.config import settings
from student.llm_generator import LLMGenerator
from student.github_manager import GitHubManager
import time

app = FastAPI(title="TDS Student API")

# Enable CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Store processed tasks to avoid duplicates
processed_tasks = set()


@app.post("/api/task")
async def receive_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Receive a task request, generate app, deploy to GitHub, and notify evaluation API.
    """
    # Verify secret
    if request.secret != settings.student_secret:
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    # Verify email
    if request.email != settings.student_email:
        raise HTTPException(status_code=400, detail="Email mismatch")
    
    # Check if task already processed
    task_key = f"{request.task}-{request.round}-{request.nonce}"
    if task_key in processed_tasks:
        return JSONResponse(
            status_code=200,
            content={"message": "Task already processed"}
        )
    
    processed_tasks.add(task_key)
    
    # Process task in background
    background_tasks.add_task(
        process_task,
        request
    )
    
    return JSONResponse(
        status_code=200,
        content={"message": "Task received and processing"}
    )


async def process_task(request: TaskRequest):
    """Process the task: generate, deploy, and notify."""
    try:
        print(f"Processing task: {request.task}, round {request.round}")
        
        # Generate application using LLM
        generator = LLMGenerator()
        files = generator.generate_app(
            brief=request.brief,
            checks=request.checks,
            attachments=request.attachments
        )
        
        # Create unique repo name
        repo_name = f"{request.task}-r{request.round}"
        
        # Deploy to GitHub
        github_manager = GitHubManager()
        
        if request.round == 1:
            # Create new repo
            repo_url, commit_sha, pages_url = github_manager.create_and_deploy_repo(
                repo_name=repo_name,
                files=files,
                enable_pages=True
            )
        else:
            # Update existing repo
            base_repo_name = f"{request.task}-r1"
            
            # Update the round 1 repo or create new round 2 repo
            try:
                repo_url, commit_sha = github_manager.update_repo(
                    repo_name=base_repo_name,
                    files=files
                )
                pages_url = github_manager.get_pages_url(base_repo_name)
            except:
                # If update fails, create new repo
                repo_url, commit_sha, pages_url = github_manager.create_and_deploy_repo(
                    repo_name=repo_name,
                    files=files,
                    enable_pages=True
                )
        
        # Wait a bit for GitHub Pages to deploy
        await asyncio.sleep(5)
        
        # Submit to evaluation API
        submission = RepoSubmission(
            email=request.email,
            task=request.task,
            round=request.round,
            nonce=request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        # Retry logic with exponential backoff
        await submit_with_retry(request.evaluation_url, submission)
        
        print(f"Task {request.task} round {request.round} completed successfully")
        
    except Exception as e:
        print(f"Error processing task {request.task}: {e}")
        import traceback
        traceback.print_exc()


async def submit_with_retry(url: str, submission: RepoSubmission, max_retries: int = 5):
    """Submit to evaluation API with exponential backoff."""
    delays = [1, 2, 4, 8, 16]  # seconds
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    url,
                    json=submission.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"Successfully submitted to {url}")
                    return
                else:
                    print(f"Attempt {attempt + 1}: Got status {response.status_code}")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                await asyncio.sleep(delays[attempt])
        
        print(f"Failed to submit to {url} after {max_retries} attempts")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "TDS Student API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment (Render sets this)
    port = int(os.environ.get("PORT", settings.api_port))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
