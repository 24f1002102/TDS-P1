"""
Round 2: Send modification requests to students who completed Round 1.
"""
import requests
import uuid
import hashlib
import json
import random
from sqlalchemy.orm import Session
from shared.database import SessionLocal, Task, Repo, init_db
from instructor.task_templates import (
    TASK_TEMPLATES,
    get_seed,
    parametrize_template,
    generate_attachments
)


def send_round2_tasks():
    """
    Send round 2 tasks to all students who completed round 1.
    """
    # Initialize database
    init_db()
    db: Session = SessionLocal()
    
    try:
        # Get all round 1 submissions
        round1_repos = db.query(Repo).filter(Repo.round == 1).all()
        
        print(f"Found {len(round1_repos)} Round 1 submissions")
        
        for repo in round1_repos:
            email = repo.email
            base_task = repo.task
            
            # Check if round 2 already sent successfully
            existing = db.query(Task).filter(
                Task.email == email,
                Task.task == base_task,
                Task.round == 2,
                Task.statuscode == 200
            ).first()
            
            if existing:
                print(f"Skipping {email} - Round 2 already completed")
                continue
            
            # Get original round 1 task
            round1_task = db.query(Task).filter(
                Task.email == email,
                Task.task == base_task,
                Task.round == 1
            ).first()
            
            if not round1_task:
                print(f"Skipping {email} - No Round 1 task found")
                continue
            
            # Find the template used in round 1
            template_id = base_task.split('-')[0]
            template = next(
                (t for t in TASK_TEMPLATES if t['id'] == template_id),
                None
            )
            
            if not template or not template.get('round2'):
                print(f"Skipping {email} - No round 2 template")
                continue
            
            # Pick a random round 2 variation
            round2_variation = random.choice(template['round2'])
            
            # Generate seed
            seed = get_seed(email)
            
            # Parametrize
            parametrized_brief = round2_variation['brief'].replace("{seed}", seed)
            parametrized_checks = [
                check.replace("{seed}", seed)
                for check in round2_variation['checks']
            ]
            
            # Generate attachments if any
            attachments = generate_attachments(
                round2_variation.get('attachments', []),
                seed
            )
            
            # Generate nonce
            nonce = str(uuid.uuid4())
            
            # Create task request
            task_request = {
                "email": email,
                "secret": round1_task.secret,
                "task": base_task,
                "round": 2,
                "nonce": nonce,
                "brief": parametrized_brief,
                "checks": parametrized_checks,
                "evaluation_url": round1_task.evaluation_url,
                "attachments": attachments
            }
            
            # Send request
            try:
                print(f"Sending Round 2 task to {email} at {round1_task.endpoint}")
                response = requests.post(
                    round1_task.endpoint,
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
                task=base_task,
                round=2,
                nonce=nonce,
                brief=parametrized_brief,
                attachments=json.dumps(attachments),
                checks=json.dumps(parametrized_checks),
                evaluation_url=round1_task.evaluation_url,
                endpoint=round1_task.endpoint,
                statuscode=status_code,
                secret=round1_task.secret
            )
            db.add(task)
            db.commit()
        
        print("Round 2 tasks sent successfully")
        
    finally:
        db.close()


if __name__ == "__main__":
    send_round2_tasks()
