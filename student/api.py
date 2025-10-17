"""
Student API endpoint for receiving task requests and deploying apps.
"""
import os
import asyncio
import httpx
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from shared.models import TaskRequest, RepoSubmission
from shared.config import settings
from student.llm_generator import LLMGenerator
from student.github_manager import GitHubManager
from student.task_tracker import TaskTracker

app = FastAPI(title="TDS Student API")

# Enable CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Persistent task tracking
task_tracker = TaskTracker()

print(f"✅ Task tracker initialized: {task_tracker.count()} tasks already processed")


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
    if task_tracker.is_processed(task_key):
        print(f"⚠️  Task already processed: {task_key}")
        return JSONResponse(
            status_code=200,
            content={"message": "Task already processed", "task": request.task}
        )
    
    # Mark as processing
    task_tracker.mark_processed(task_key)
    print(f"✅ New task accepted: {task_key}")
    
    # Process task in background
    background_tasks.add_task(
        process_task,
        request
    )
    
    return JSONResponse(
        status_code=200,
        content={"message": "Task received and processing", "task": request.task}
    )


async def process_task(request: TaskRequest):
    """Process the task: generate, deploy, and notify."""
    start_time = time.time()
    timeout_seconds = 600  # 10 minutes
    
    def check_timeout() -> float:
        """Check if timeout exceeded and return elapsed time."""
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Task processing exceeded {timeout_seconds}s limit")
        return elapsed
    
    try:
        print(f"\n{'='*60}")
        print(f"🚀 PROCESSING TASK: {request.task} (Round {request.round})")
        print(f"{'='*60}")
        
        # Step 1: Generate application using LLM
        elapsed = check_timeout()
        print(f"\n[{elapsed:.1f}s] 🤖 Generating application with LLM...")
        generator = LLMGenerator()
        files = generator.generate_app(
            brief=request.brief,
            checks=request.checks,
            attachments=request.attachments
        )
        elapsed = check_timeout()
        print(f"[{elapsed:.1f}s] ✅ Generated {len(files)} files")
        
        # Step 2: Prepare GitHub deployment
        repo_name = f"{request.task}-r{request.round}"
        github_manager = GitHubManager()
        
        elapsed = check_timeout()
        print(f"\n[{elapsed:.1f}s] 📦 Deploying to GitHub...")
        
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
        
        elapsed = check_timeout()
        print(f"[{elapsed:.1f}s] ✅ GitHub deployment complete")
        print(f"   📍 Repo: {repo_url}")
        print(f"   🌐 Pages: {pages_url}")
        
        # Step 3: Verify GitHub Pages is accessible
        elapsed = check_timeout()
        print(f"\n[{elapsed:.1f}s] ⏳ Verifying GitHub Pages deployment...")
        await asyncio.sleep(5)  # Initial wait
        
        elapsed = check_timeout()
        is_live = await github_manager.verify_pages_deployed(pages_url, timeout=120)
        elapsed = check_timeout()
        
        if is_live:
            print(f"[{elapsed:.1f}s] ✅ GitHub Pages is live and accessible!")
        else:
            print(f"[{elapsed:.1f}s] ⚠️  Pages verification timed out, but continuing...")
        
        # Step 4: Submit to evaluation API
        elapsed = check_timeout()
        print(f"\n[{elapsed:.1f}s] 📤 Submitting to evaluation API...")
        
        submission = RepoSubmission(
            email=request.email,
            task=request.task,
            round=request.round,
            nonce=request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        await submit_with_retry(request.evaluation_url, submission)
        
        elapsed = check_timeout()
        print(f"\n[{elapsed:.1f}s] 🎉 TASK COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
    except TimeoutError as e:
        elapsed = time.time() - start_time
        print(f"\n[{elapsed:.1f}s] ⏱️  TIMEOUT: {e}")
        print(f"{'='*60}\n")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[{elapsed:.1f}s] ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")


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


@app.get("/stats")
async def stats():
    """Get statistics about processed tasks."""
    processed = task_tracker.get_processed_tasks()
    return {
        "status": "ok",
        "total_processed": len(processed),
        "tasks": processed
    }


if __name__ == "__main__":
    import uvicorn
    
    # Display configuration at startup
    print("\n" + "="*60)
    print("🚀 TDS Student API Starting...")
    print("="*60)
    
    # Verify GitHub credentials
    try:
        test_manager = GitHubManager()
        print(f"✅ GitHub Account: {test_manager.username}")
        print(f"✅ GitHub Pages URL: https://{test_manager.username}.github.io/")
    except Exception as e:
        print(f"⚠️  Warning: Could not verify GitHub credentials: {e}")
    
    print(f"✅ Student Email: {settings.student_email}")
    print(f"✅ API Port: {settings.api_port}")
    print("="*60 + "\n")
    
    # Use PORT from environment (Render sets this)
    port = int(os.environ.get("PORT", settings.api_port))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
