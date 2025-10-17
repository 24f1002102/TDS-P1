#!/usr/bin/env python3
"""
Export results from database to CSV.
"""
import csv
from shared.database import SessionLocal, Result, Repo, Task
from datetime import datetime

def export_results(output_file: str = "results_export.csv"):
    """Export all results to CSV."""
    db = SessionLocal()
    
    try:
        results = db.query(Result).order_by(Result.email, Result.task, Result.round).all()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Email', 'Task', 'Round', 'Repo URL', 'Commit SHA',
                'Pages URL', 'Check', 'Score', 'Reason', 'Timestamp'
            ])
            
            for r in results:
                writer.writerow([
                    r.email, r.task, r.round, r.repo_url, r.commit_sha,
                    r.pages_url, r.check, r.score, r.reason, r.timestamp
                ])
        
        print(f"✅ Exported {len(results)} results to {output_file}")
        
    finally:
        db.close()

def export_summary(output_file: str = "summary.csv"):
    """Export summary with average scores."""
    db = SessionLocal()
    
    try:
        # Get average scores per student per round
        query = """
            SELECT 
                r.email,
                r.task,
                r.round,
                AVG(res.score) as avg_score,
                COUNT(res.id) as num_checks,
                r.repo_url,
                r.pages_url
            FROM repos r
            LEFT JOIN results res ON 
                r.email = res.email AND 
                r.task = res.task AND 
                r.round = res.round
            GROUP BY r.email, r.task, r.round
            ORDER BY r.email, r.round
        """
        
        results = db.execute(query).fetchall()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Email', 'Task', 'Round', 'Average Score', 'Num Checks',
                'Repo URL', 'Pages URL'
            ])
            
            for r in results:
                writer.writerow([
                    r.email, r.task, r.round, 
                    f"{r.avg_score:.2f}" if r.avg_score else "N/A",
                    r.num_checks or 0,
                    r.repo_url, r.pages_url
                ])
        
        print(f"✅ Exported summary to {output_file}")
        
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    export_type = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if export_type in ["results", "both"]:
        export_results()
    
    if export_type in ["summary", "both"]:
        export_summary()
