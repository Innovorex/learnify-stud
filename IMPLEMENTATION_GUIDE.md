# 🚀 CBSE Syllabus System - Implementation Guide

## Production-Ready Enhancements Implementation

This guide walks you through implementing the enhanced, production-ready CBSE syllabus system with dynamic discovery, version control, and intelligent caching.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Backend Implementation](#backend-implementation)
4. [API Integration](#api-integration)
5. [Frontend Updates](#frontend-updates)
6. [Initial Data Load](#initial-data-load)
7. [Testing](#testing)
8. [Maintenance](#maintenance)

---

## 1. Prerequisites

### Install Required Python Packages

```bash
cd /home/hub_ai/ls/backend

# Add to requirements.txt
echo "PyMuPDF>=1.23.0" >> requirements.txt
echo "beautifulsoup4>=4.12.0" >> requirements.txt
echo "lxml>=4.9.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

**Packages Added:**
- `PyMuPDF` (fitz) - Superior PDF text extraction
- `beautifulsoup4` - HTML parsing for catalog discovery
- `lxml` - Fast XML/HTML parser

---

## 2. Database Setup

### Step 1: Run the Migration Script

```bash
cd /home/hub_ai/ls/backend

# Connect to PostgreSQL
psql -U innovorex -d ai_assessment -f migrations/001_enhanced_syllabus_schema.sql
```

### Step 2: Verify Tables Created

```bash
psql -U innovorex -d ai_assessment -c "\dt"
```

You should see:
- `curriculum_catalog`
- `syllabus_master`
- `syllabus_topics`
- `syllabus_fetch_log`
- `cbse_subject_codes`

### Step 3: Verify Initial Data

```bash
psql -U innovorex -d ai_assessment -c "SELECT * FROM cbse_subject_codes;"
```

Should show standard CBSE subject codes (041, 086, etc.)

---

## 3. Backend Implementation

### Step 1: Update main.py

Add syllabus routes to your FastAPI app:

```python
# In /home/hub_ai/ls/backend/main.py

from app import syllabus_routes  # Add this import

# Add this line after existing routers
app.include_router(syllabus_routes.router, prefix="/api", tags=["Syllabus"])
```

### Step 2: Update Database Models Import

Ensure your models are imported correctly:

```python
# In /home/hub_ai/ls/backend/main.py or wherever Base.metadata.create_all is called

from app.models import (
    User, Assessment, Question, Result,
    CurriculumCatalog, SyllabusMaster, SyllabusTopics,
    SyllabusFetchLog, CBSESubjectCode  # New models
)

# This will create all tables
Base.metadata.create_all(bind=engine)
```

### Step 3: Test Backend Server

```bash
cd /home/hub_ai/ls/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit: `http://localhost:8000/docs`

You should see new endpoints under "Syllabus" section.

---

## 4. API Integration

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/syllabus/subjects/{class_name}` | GET | Get available subjects for a class |
| `/api/syllabus/topics/{class_name}/{subject}` | GET | Get chapters/topics for a subject |
| `/api/syllabus/topic/{topic_id}` | GET | Get detailed topic content |
| `/api/syllabus/fetch/{class_name}/{subject}` | POST | Force refresh syllabus |
| `/api/syllabus/status/{class_name}/{subject}` | GET | Check syllabus cache status |
| `/api/syllabus/hierarchy/{class_name}/{subject}` | GET | Get complete unit→chapter hierarchy |
| `/api/syllabus/discover-catalog/{academic_year}` | POST | Discover all PDFs for a year |
| `/api/syllabus/health` | GET | System health check |

### Test Key Endpoints

```bash
# 1. Get subjects for Class 10
curl http://localhost:8000/api/syllabus/subjects/10

# 2. Get topics for Class 10 Mathematics
curl http://localhost:8000/api/syllabus/topics/10/Mathematics

# 3. Check system health
curl http://localhost:8000/api/syllabus/health
```

---

## 5. Frontend Updates

### Step 1: Update API Service

Create/update `/home/hub_ai/ls/frontend/src/services/api.ts`:

```typescript
// Add syllabus endpoints
export const syllabusAPI = {
  // Get subjects for a class
  getSubjects: (className: string) =>
    api.get(`/api/syllabus/subjects/${className}`),

  // Get topics/chapters for a subject
  getTopics: (className: string, subject: string) =>
    api.get(`/api/syllabus/topics/${className}/${subject}`),

  // Get detailed topic content
  getTopicContent: (topicId: number) =>
    api.get(`/api/syllabus/topic/${topicId}`),

  // Get syllabus status
  getSyllabusStatus: (className: string, subject: string) =>
    api.get(`/api/syllabus/status/${className}/${subject}`),
};
```

### Step 2: Update CreateAssessment Component

Replace the static chapter input with dynamic dropdowns:

```typescript
// In CreateAssessment.tsx

import { useState, useEffect } from 'react';
import { syllabusAPI } from '../../services/api';

// Add state
const [availableSubjects, setAvailableSubjects] = useState<any[]>([]);
const [availableTopics, setAvailableTopics] = useState<any[]>([]);
const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
const [syllabusStatus, setSyllabusStatus] = useState<any>(null);

// Fetch subjects when class changes
useEffect(() => {
  if (className) {
    fetchSubjects();
  }
}, [className]);

// Fetch topics when subject changes
useEffect(() => {
  if (className && subject) {
    fetchTopics();
  }
}, [className, subject]);

const fetchSubjects = async () => {
  try {
    const response = await syllabusAPI.getSubjects(className);
    setAvailableSubjects(response.data.subjects);
  } catch (error) {
    toast.error('Failed to load subjects');
  }
};

const fetchTopics = async () => {
  try {
    // Show loading state
    toast.info('Loading syllabus...');

    const response = await syllabusAPI.getTopics(className, subject);
    setAvailableTopics(response.data);

    // Check cache status
    const statusRes = await syllabusAPI.getSyllabusStatus(className, subject);
    setSyllabusStatus(statusRes.data);

    toast.success('Syllabus loaded!');
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to load topics');
  }
};
```

### Step 3: Update Form UI

Replace the chapter input with a dropdown:

```tsx
{/* Subject Dropdown (with codes) */}
<div className="space-y-2">
  <Label htmlFor="subject">Subject</Label>
  <Select value={subject} onValueChange={setSubject}>
    <SelectTrigger>
      <SelectValue placeholder="Select subject" />
    </SelectTrigger>
    <SelectContent>
      {availableSubjects.map((subj) => (
        <SelectItem key={subj.subject_name} value={subj.subject_name}>
          {subj.subject_name} {subj.subject_code ? `(${subj.subject_code})` : ''}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
</div>

{/* Chapter/Topic Dropdown */}
<div className="space-y-2">
  <Label htmlFor="chapter">Chapter/Topic</Label>
  <Select
    value={selectedTopicId?.toString()}
    onValueChange={(val) => {
      setSelectedTopicId(parseInt(val));
      const topic = availableTopics.find(t => t.id === parseInt(val));
      setChapter(topic?.chapter_name || '');
    }}
  >
    <SelectTrigger>
      <SelectValue placeholder="Select chapter" />
    </SelectTrigger>
    <SelectContent>
      {availableTopics.map((topic) => (
        <SelectItem key={topic.id} value={topic.id.toString()}>
          {topic.chapter_number ? `Ch ${topic.chapter_number}: ` : ''}
          {topic.chapter_name}
          {topic.weightage ? ` (${topic.weightage} marks)` : ''}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>

  {/* Optional: Show PDF link */}
  {syllabusStatus?.pdf_url && (
    <a
      href={syllabusStatus.pdf_url}
      target="_blank"
      rel="noopener noreferrer"
      className="text-sm text-blue-600 hover:underline"
    >
      📄 View Official Syllabus PDF
    </a>
  )}
</div>
```

---

## 6. Initial Data Load

### Step 1: Discover Catalog

Run the catalog discovery for current academic year:

```bash
# Method 1: Using API
curl -X POST http://localhost:8000/api/syllabus/discover-catalog/2024-25

# Method 2: Using Python script
cd /home/hub_ai/ls/backend
python -c "
from app.db import SessionLocal
from app.syllabus_scraper import discover_syllabus_catalog

db = SessionLocal()
count = discover_syllabus_catalog(db, '2024-25')
print(f'Discovered {count} syllabus PDFs')
db.close()
"
```

### Step 2: Pre-load Key Syllabi

Create a script to pre-load frequently used syllabi:

```python
# /home/hub_ai/ls/backend/scripts/preload_syllabi.py

from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService

def preload_syllabi():
    """
    Pre-load common syllabi into cache
    """
    db = SessionLocal()
    service = EnhancedSyllabusService(db)

    # Common subjects to pre-load
    syllabi_to_load = [
        ("9", "Mathematics"),
        ("9", "Science"),
        ("10", "Mathematics"),
        ("10", "Science"),
        ("10", "Social Science"),
        ("11", "Mathematics"),
        ("11", "Physics"),
        ("11", "Chemistry"),
        ("12", "Mathematics"),
        ("12", "Physics"),
        ("12", "Chemistry"),
    ]

    for class_name, subject in syllabi_to_load:
        print(f"\n{'='*60}")
        print(f"Loading: Class {class_name} - {subject}")
        print('='*60)

        try:
            syllabus = service.get_syllabus(class_name, subject)
            if syllabus:
                topics_count = len(service.get_topics(class_name, subject))
                print(f"✅ Loaded {topics_count} topics")
            else:
                print(f"❌ Failed to load")
        except Exception as e:
            print(f"❌ Error: {e}")

    db.close()
    print("\n✅ Pre-loading completed!")

if __name__ == "__main__":
    preload_syllabi()
```

Run it:

```bash
cd /home/hub_ai/ls/backend
python scripts/preload_syllabi.py
```

---

## 7. Testing

### Test Checklist

- [ ] **Database tables created** - All 5 new tables exist
- [ ] **Subject codes populated** - `cbse_subject_codes` has data
- [ ] **Catalog discovery works** - Can discover PDFs from CBSE website
- [ ] **PDF fetching works** - Can download and extract text
- [ ] **SHA256 checksumming** - Content hash is computed and stored
- [ ] **AI parsing works** - Syllabus is parsed into chapters
- [ ] **Topics stored** - `syllabus_topics` has structured data
- [ ] **API endpoints respond** - All syllabus endpoints work
- [ ] **Frontend dropdowns** - Subject and chapter dropdowns populate
- [ ] **Caching works** - Second request uses cached data
- [ ] **Version detection** - System detects when syllabus changes

### Manual Test Flow

1. **Test Subject Listing:**
   ```bash
   curl http://localhost:8000/api/syllabus/subjects/10
   ```
   Should return: Mathematics, Science, Social Science with codes

2. **Test Topic Retrieval (triggers auto-fetch):**
   ```bash
   curl http://localhost:8000/api/syllabus/topics/10/Mathematics
   ```
   First call: Fetches from CBSE, parses, stores (slow ~30-60s)
   Second call: Returns from cache (fast <1s)

3. **Test Cache Status:**
   ```bash
   curl http://localhost:8000/api/syllabus/status/10/Mathematics
   ```
   Should show: cached, SHA256, last_updated, topics_count

4. **Test Frontend:**
   - Select Class 10
   - Subject dropdown should populate with Mathematics (041), Science (086), etc.
   - Select Mathematics
   - Chapter dropdown should show: Real Numbers, Polynomials, etc.

---

## 8. Maintenance

### Automatic Yearly Updates

Set up a cron job to discover new academic year syllabi:

```bash
# Add to crontab
crontab -e

# Add this line (runs April 1st every year at 2 AM)
0 2 1 4 * cd /home/hub_ai/ls/backend && python scripts/refresh_syllabi.py
```

Create `/home/hub_ai/ls/backend/scripts/refresh_syllabi.py`:

```python
from app.db import SessionLocal
from app.syllabus_scraper import CBSESyllabusDiscovery

db = SessionLocal()
scraper = CBSESyllabusDiscovery(db)
results = scraper.refresh_all_catalogs()
print(f"Refreshed: {results}")
db.close()
```

### Monitoring Cache Age

Query to find stale syllabi:

```sql
SELECT
    class_name,
    subject,
    academic_year,
    last_updated,
    EXTRACT(DAY FROM NOW() - last_updated) as age_days
FROM syllabus_master
WHERE is_active = TRUE
AND EXTRACT(DAY FROM NOW() - last_updated) > 180
ORDER BY last_updated ASC;
```

### Force Refresh Stale Syllabi

```bash
# Refresh all syllabi older than 6 months
curl -X POST http://localhost:8000/api/syllabus/refresh-all
```

---

## 🎯 **Implementation Checklist**

### Phase 1: Database (Day 1)
- [ ] Install PyMuPDF, BeautifulSoup4
- [ ] Run migration SQL script
- [ ] Verify tables created
- [ ] Verify CBSE subject codes inserted

### Phase 2: Backend Core (Day 1-2)
- [ ] Models updated (done)
- [ ] Syllabus scraper created (done)
- [ ] Enhanced service created (done)
- [ ] API routes added
- [ ] Routes registered in main.py
- [ ] Server starts without errors

### Phase 3: Initial Load (Day 2)
- [ ] Discover catalog for 2024-25
- [ ] Pre-load Class 9-12 common subjects
- [ ] Verify data in database

### Phase 4: API Testing (Day 2)
- [ ] Test all syllabus endpoints
- [ ] Verify caching works
- [ ] Check SHA256 versioning
- [ ] Test error handling

### Phase 5: Frontend (Day 3)
- [ ] Update API service
- [ ] Add subject dropdown
- [ ] Add chapter/topic dropdown
- [ ] Add PDF link display
- [ ] Test user flow

### Phase 6: Integration (Day 3)
- [ ] Update teacher.py to use syllabus_topic_id
- [ ] Pass syllabus content to AI question generation
- [ ] Test end-to-end flow
- [ ] Verify questions use real syllabus

### Phase 7: Documentation & Deployment (Day 4)
- [ ] Document API endpoints
- [ ] Create admin guide
- [ ] Set up monitoring
- [ ] Deploy to production

---

## 🔧 **Troubleshooting**

### Issue: "Table already exists" error
**Solution:** Tables may have been created by SQLAlchemy auto-create. Drop and recreate:
```sql
DROP TABLE IF EXISTS curriculum_catalog CASCADE;
-- Then run migration again
```

### Issue: PyMuPDF installation fails
**Solution:** Install system dependencies:
```bash
sudo apt-get install python3-dev libmupdf-dev
pip install --upgrade PyMuPDF
```

### Issue: PDF extraction returns empty text
**Solution:** Check PDF URL accessibility:
```bash
curl -I https://cbseacademic.nic.in/web_material/CurriculumMain25/Secondary/Mathematics_IX-X.pdf
```

### Issue: AI parsing returns no chapters
**Solution:** Check syllabus_text length and API response:
- Verify `content_extracted` is not empty in database
- Check OpenRouter API key is valid
- Review logs for AI API errors

---

## 📊 **Performance Expectations**

| Operation | First Time | Cached |
|-----------|-----------|--------|
| Catalog Discovery | 20-30s | N/A |
| Fetch Single Syllabus | 30-60s | <1s |
| Parse with AI | 10-20s | N/A |
| Get Topics | N/A | <100ms |
| Get Subject List | 5-10s (if discovering) | <50ms |

---

## 📞 **Support**

If you encounter issues:

1. Check logs: `/home/hub_ai/ls/backend/logs/`
2. Query `syllabus_fetch_log` for errors
3. Verify database connections
4. Check API keys in `.env`

---

## ✅ **Success Criteria**

You'll know the system is working when:

1. ✅ Teachers see **real CBSE subjects** in dropdown (with codes)
2. ✅ Teachers see **actual chapter names** from official syllabus
3. ✅ AI generates questions using **real syllabus content**
4. ✅ System **auto-updates** when new academic year starts
5. ✅ **PDF links** are displayed for reference
6. ✅ **Cache** reduces API calls and improves speed
7. ✅ **SHA256** detects syllabus changes automatically

---

**Implementation Time:** ~3-4 days for complete setup and testing

**Maintenance:** ~1 hour per year (automatic catalog refresh)
