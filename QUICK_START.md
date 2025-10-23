# 🚀 Quick Start Guide - CBSE Syllabus System

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd /home/hub_ai/ls/backend
pip install PyMuPDF beautifulsoup4 lxml
```

### Step 2: Run Database Migration
```bash
psql -U innovorex -d ai_assessment -f migrations/001_enhanced_syllabus_schema.sql
```

### Step 3: Update main.py
Add this line to `/home/hub_ai/ls/backend/main.py`:
```python
from app import syllabus_routes
app.include_router(syllabus_routes.router, prefix="/api", tags=["Syllabus"])
```

### Step 4: Start Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Discover Catalog
```bash
# In another terminal
curl -X POST http://localhost:8000/api/syllabus/discover-catalog/2024-25
```

Wait ~30 seconds for discovery to complete.

### Step 6: Test It
```bash
# Get subjects for Class 10
curl http://localhost:8000/api/syllabus/subjects/10

# Get topics for Mathematics
curl http://localhost:8000/api/syllabus/topics/10/Mathematics
```

## ✅ Success Indicators

You should see:
- Subjects with codes: `"Mathematics (041)"`
- Real chapter names: `"Real Numbers", "Polynomials"`
- PDF URLs in responses

## 📚 Files Overview

```
ls/
├── backend/
│   ├── migrations/
│   │   └── 001_enhanced_syllabus_schema.sql  ← Run this first
│   ├── app/
│   │   ├── models.py                         ← Updated with new models
│   │   ├── syllabus_scraper.py              ← NEW: Catalog discovery
│   │   ├── syllabus_service_v2.py           ← NEW: Enhanced service
│   │   └── syllabus_routes.py               ← NEW: API endpoints
│   └── main.py                               ← Update to add routes
│
├── IMPLEMENTATION_GUIDE.md                   ← Complete guide
├── IMPLEMENTATION_SUMMARY.md                 ← What was built
└── QUICK_START.md                            ← This file
```

## 🔍 Test Endpoints

Open http://localhost:8000/docs and look for "Syllabus" section.

Try these:
- `GET /api/syllabus/subjects/10`
- `GET /api/syllabus/topics/10/Mathematics`
- `GET /api/syllabus/health`

## 📖 Full Documentation

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for complete setup.

## ⚠️ Troubleshooting

**Can't install PyMuPDF?**
```bash
sudo apt-get install python3-dev libmupdf-dev
pip install --upgrade PyMuPDF
```

**No subjects returned?**
- Run catalog discovery first
- Check `curriculum_catalog` table has data

**Database errors?**
- Ensure PostgreSQL is running
- Check connection string in .env

## 🎯 Next Steps

After this works:
1. Update frontend with dropdowns (see implementation guide)
2. Integrate with question generation
3. Test complete teacher flow

**Estimated setup time:** 15-20 minutes
