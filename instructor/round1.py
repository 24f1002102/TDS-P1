"""
Round 1: Send initial task requests to students.
"""
import csv
import requests
import uuid
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from shared.database import SessionLocal, Task, init_db
from instructor.task_templates import (
    TASK_TEMPLATES,
    get_seed,
    parametrize_template,
    generate_attachments
)
import random
import json


def send_round1_tasks(submissions_csv: str, evaluation_url: str):
    """
    Send round 1 tasks to all students in submissions.csv
    
    Args:
        submissions_csv: Path to CSV with columns: timestamp,email,endpoint,secret
        evaluation_url: URL where students should submit their repos
    """
    # Initialize database
    init_db()
    db: Session = SessionLocal()
    
    try:
        # Read submissions
        with open(submissions_csv, 'r') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
        
        print(f"Found {len(submissions)} submissions")
        
        for submission in submissions:
            email = submission['email']
            endpoint = submission['endpoint']
            secret = submission['secret']
            
            # Check if round 1 already sent successfully
            existing = db.query(Task).filter(
                Task.email == email,
                Task.round == 1,
                Task.statuscode == 200
            ).first()
            
            if existing:
                print(f"Skipping {email} - Round 1 already completed")
                continue
            
            # Generate seed
            seed = get_seed(email)
            
            # Pick a random template
            template = random.choice(TASK_TEMPLATES)
            
            # Parametrize template
            parametrized = parametrize_template(template, seed)
            
            # Generate task ID
            brief_hash = hashlib.sha256(
                json.dumps(parametrized).encode()
            ).hexdigest()[:5]
            task_id = f"{parametrized['id']}-{brief_hash}"
            
            # Generate attachments
            attachments = generate_attachments(
                parametrized.get('attachments', []),
                seed
            )
            
            # Generate nonce
            nonce = str(uuid.uuid4())
            
            # Create task request
            task_request = {
                "email": email,
                "secret": secret,
                "task": task_id,
                "round": 1,
                "nonce": nonce,
                "brief": parametrized['brief'],
                "checks": parametrized['checks'],
                "evaluation_url": evaluation_url,
                "attachments": attachments
            }
            
            # Send request
            try:
                print(f"Sending Round 1 task to {email} at {endpoint}")
                response = requests.post(
                    endpoint,
                    json=task_request,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                status_code = response.status_code
                print(f"  Status: {status_code}")
                
            except Exception as e:
                print(f"  Error: {e}")
                status_code = 0
            
            # Log to database
            task = Task(
                email=email,
                task=task_id,
                round=1,
                nonce=nonce,
                brief=parametrized['brief'],
                attachments=json.dumps(attachments),
                checks=json.dumps(parametrized['checks']),
                evaluation_url=evaluation_url,
                endpoint=endpoint,
                statuscode=status_code,
                secret=secret
            )
            db.add(task)
            db.commit()
            
        print("Round 1 tasks sent successfully")
        
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python round1.py <submissions.csv> <evaluation_url>")
        sys.exit(1)
    
    submissions_csv = sys.argv[1]
    evaluation_url = sys.argv[2]
    
    send_round1_tasks(submissions_csv, evaluation_url)
