"""
Evaluation API endpoint for receiving student submissions.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from shared.models import RepoSubmission
from shared.database import get_db, Repo, Task, init_db
from shared.config import settings
from datetime import datetime

app = FastAPI(title="TDS Evaluation API")

# Initialize database
init_db()


@app.post("/api/evaluate")
async def receive_submission(submission: RepoSubmission):
    """
    Receive repository submission from students.
    
    Validates the submission against the task table and stores in repos table.
    """
    db: Session = next(get_db())
    
    try:
        # Find matching task
        task = db.query(Task).filter(
            Task.email == submission.email,
            Task.task == submission.task,
            Task.round == submission.round,
            Task.nonce == submission.nonce
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=400,
                detail="No matching task found. Check email, task, round, and nonce."
            )
        
        # Check if already submitted
        existing = db.query(Repo).filter(
            Repo.email == submission.email,
            Repo.task == submission.task,
            Repo.round == submission.round,
            Repo.nonce == submission.nonce
        ).first()
        
        if existing:
            # Update existing submission
            existing.repo_url = submission.repo_url
            existing.commit_sha = submission.commit_sha
            existing.pages_url = submission.pages_url
            existing.timestamp = datetime.utcnow()
        else:
            # Create new submission
            repo = Repo(
                email=submission.email,
                task=submission.task,
                round=submission.round,
                nonce=submission.nonce,
                repo_url=submission.repo_url,
                commit_sha=submission.commit_sha,
                pages_url=submission.pages_url
            )
            db.add(repo)
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Submission received successfully",
                "task": submission.task,
                "round": submission.round
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "TDS Evaluation API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.evaluation_api_host,
        port=settings.evaluation_api_port
    )
