# 🚀 Quick Start - Fix Your Setup

## ❌ Problem: "ModuleNotFoundError: No module named 'shared'"

This happens because you're running from the wrong directory.

## ✅ Solution: Run from Project Root

### Option 1: Use the Startup Script (Easiest)

```bash
# Go to project root
cd /Users/arvinsamuela/Desktop/IITM/TDS-P1

# Run the script
./start_student_api.sh
```

### Option 2: Manual Commands

```bash
# 1. Go to project root
cd /Users/arvinsamuela/Desktop/IITM/TDS-P1

# 2. Activate venv
source venv/bin/activate

# 3. Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# 4. Run API
python -m student.api
```

### Option 3: Using uvicorn

```bash
cd /Users/arvinsamuela/Desktop/IITM/TDS-P1
source venv/bin/activate
uvicorn student.api:app --host 0.0.0.0 --port 8000
```

## 🎯 Test It Works

Open a new terminal:

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## 📝 Summary

**DON'T** run from `student/` directory
**DO** run from project root: `/Users/arvinsamuela/Desktop/IITM/TDS-P1`

That's it! 🎉
