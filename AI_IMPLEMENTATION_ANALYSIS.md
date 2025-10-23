# LS (Learnify Student) Project - AI Implementation Analysis
## Comprehensive Token Usage & Cost Breakdown Report

**Analysis Date:** October 21, 2025  
**Project:** Learnify Student - AI Assessment Platform  
**Backend Location:** `/home/hub_ai/ls/backend/`

---

## SECTION 1: PROJECT OVERVIEW

### What is LS (Learnify Student)?

LS is a **production-ready AI-powered assessment platform** designed for Indian educational institutions (CBSE and State Boards). It enables teachers to create automated exams with AI-generated questions and students to take assessments with automatic grading.

**Core Purpose:**
- Teachers create assessments (quizzes/exams) for specific chapters
- System automatically generates 10 multiple-choice questions (MCQs) per assessment using AI
- Questions are based on REAL curriculum syllabus content
- Students take exams with time-based access windows
- Automatic scoring and results tracking

**Key Features:**
1. CBSE & State Board syllabus integration (Classes 1-12)
2. Multi-language support (English, Telugu, Hindi)
3. Real-time syllabus discovery and PDF extraction
4. AI-powered question generation from official curricula
5. Hierarchical topic/chapter management
6. Teacher dashboard for assessment creation
7. Student dashboard for exam taking
8. Results analytics and performance tracking

---

## SECTION 2: AI SERVICE FILES & ARCHITECTURE

### 2.1 AI-Powered Question Generation
**File:** `/home/hub_ai/ls/backend/app/ai_question_gen.py`

**Function:** `generate_questions()`
- **Purpose:** Generate 10 MCQs for teacher-created assessments
- **AI Provider:** OpenRouter API (via GPT-4o Mini)
- **API Key:** `OPENROUTER_API_KEY` from `.env`
- **Model Used:** `openai/gpt-4o-mini` (cheap, fast, good quality)

**Prompt Structure:**
```
Input: Board, Class, Subject, Chapter, Optional Syllabus Content
Output: JSON array of 10 MCQs with options, correct answer, difficulty level
```

**Capabilities:**
- Generates questions with REAL syllabus content when available
- Falls back to generic questions if syllabus not found
- Returns questions in JSON format for database storage
- Supports 3 difficulty levels: easy (30%), medium (50%), hard (20%)

---

### 2.2 Syllabus Service (AI-Powered Parsing)
**File:** `/home/hub_ai/ls/backend/app/syllabus_service_v2.py`

**Main Class:** `EnhancedSyllabusService`

**Key Methods Using AI:**

#### 1. `_parse_with_ai()` - Syllabus Structure Parsing
- **Purpose:** Parse unstructured PDF syllabus into structured JSON (units→chapters→topics)
- **AI Provider:** OpenRouter GPT-4o Mini
- **Input:** Raw syllabus text (up to 15,000 characters)
- **Output:** Structured JSON with:
  - Units (numbered structure)
  - Chapters (with chapter numbers)
  - Topics & subtopics
  - Learning outcomes
  - Key concepts
  - Marks weightage
  - Difficulty levels

**Prompt:**
```
"Parse this CBSE Class X Subject syllabus into JSON format.
Extract: Units, Chapters, Topics, Subtopics, Learning outcomes, Weightage, Key concepts"
```

**Call Frequency:**
- Called whenever a new syllabus PDF is fetched
- Cached result stored in database
- Re-triggered only if SHA256 hash changes (content updated)

---

### 2.3 Syllabus Discovery & Extraction
**File:** `/home/hub_ai/ls/backend/app/syllabus_scraper.py`

**Purpose:** Automatically discover CBSE syllabus PDFs from official websites

**Workflow:**
1. Scrapes CBSE website for syllabus PDF URLs
2. Stores in `curriculum_catalog` table
3. Downloads and extracts text via PyMuPDF
4. Falls back to PyPDF2 if PyMuPDF fails
5. Computes SHA256 for version control

**NOT AI-powered** (uses web scraping + PDF extraction)

---

## SECTION 3: AI WORKFLOWS & TOKEN USAGE

### Workflow 1: Teacher Creates Assessment

**Trigger:** Teacher calls `/teacher/create-assessment` endpoint

**Steps:**
```
1. Teacher submits: Class, Section, Subject, Chapter, Duration
   
2. Backend creates Assessment record in database
   
3. Background task: generate_and_store_questions()
   
4. Fetch real syllabus content:
   - Query syllabus_master for cached content
   - IF not cached → Fetch PDF → Extract → Parse with AI
   - Retrieve chapter-specific content (3000 chars max)
   
5. AI CALL #1: Generate questions
   - Model: openai/gpt-4o-mini
   - Input: Prompt + syllabus content
   - Output: 10 MCQs in JSON format
   
6. Store 10 questions in question_bank table
   
7. Async background job - no blocking
```

**Tokens per Assessment Creation:**

| Component | Tokens (Approx) | Notes |
|-----------|-----------------|-------|
| **Input Prompt** | 200-400 | System instructions + requirements |
| **Syllabus Context** | 3000 chars ≈ 750-1000 tokens | ~0.25 tokens per character |
| **Question Output** | 1500-2000 tokens | 10 MCQs with options |
| **Total Input Tokens** | 950-1400 | Per assessment |
| **Total Output Tokens** | 1500-2000 | Per assessment |
| **TOTAL TOKENS/ASSESSMENT** | **2450-3400 tokens** | Average: 2900 tokens |

---

### Workflow 2: First Syllabus Fetch (Classes 9-10 CBSE)

**Trigger:** Teacher selects subject not yet in cache OR `/syllabus/topics/{class}/{subject}` endpoint

**Steps:**
```
1. Backend checks syllabus_master for cached content
   
2. IF not found:
   
   3. Fetch PDF from curriculum_catalog
   
   4. Extract text (PyMuPDF or PyPDF2)
   
   5. AI CALL #2: Parse syllabus structure
      - Model: openai/gpt-4o-mini
      - Input: Truncated PDF text (up to 15,000 chars)
      - Output: JSON structure with units, chapters, topics
   
   6. Store in syllabus_master and syllabus_topics tables
   
   7. Cache valid for 6 months
```

**Tokens per Syllabus Parse:**

| Component | Tokens | Notes |
|-----------|--------|-------|
| **Parsing Prompt** | 400-600 | Instructions for structure extraction |
| **Syllabus Text** | 15,000 chars ≈ 3750-5000 tokens | Capped at 15,000 chars |
| **Structured Output** | 2000-3500 tokens | JSON with units, chapters, topics |
| **Total Input Tokens** | 4150-5600 | Per new syllabus |
| **Total Output Tokens** | 2000-3500 | Per new syllabus |
| **TOTAL TOKENS/SYLLABUS** | **6150-9100 tokens** | Average: 7500 tokens |

**Frequency:** ~1-2 times per new subject (then cached for 6 months)

---

### Workflow 3: Classes 1-8 NCERT/State Board (Pre-loaded)

**Architecture:**
- Syllabi are pre-loaded via migration scripts
- No dynamic fetching
- Content stored directly in database
- No AI parsing needed

**Token Usage:** **ZERO** (fully cached)

---

### Workflow 4: Question Submission & Grading

**Process:**
```
1. Student submits answers via /student/submit-exam
2. Backend retrieves question_bank records
3. Compares student answers with correct_answer field
4. Calculates score
5. Stores result in exam_results table
```

**Token Usage:** **ZERO** (no AI calls - fully deterministic)

---

## SECTION 4: CURRENT AI PROVIDERS & MODELS

### Active AI Provider: OpenRouter

**API Details:**
- **Service:** OpenRouter (API aggregator)
- **Primary Model:** `openai/gpt-4o-mini`
- **API Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Auth:** Bearer token from `.env` - `OPENROUTER_API_KEY`

**Why GPT-4o Mini?**
- Cost-effective
- Fast generation (perfect for web applications)
- Good quality for education domain
- Handles JSON output well
- Sufficient context window (128K tokens)

**Other Available Models (Unused):**
- `GEMINI_API_KEY` in `.env` - not actively used
- System has capability to switch models but default is GPT-4o Mini

---

## SECTION 5: DETAILED COST BREAKDOWN

### 5.1 OpenRouter Pricing (GPT-4o Mini)

**Current Rates via OpenRouter:**
- Input: $0.000150 per 1K tokens
- Output: $0.000600 per 1K tokens

**Formula:**
```
Cost = (Input_tokens / 1000 × $0.00015) + (Output_tokens / 1000 × $0.0006)
```

---

### 5.2 Token Usage Scenarios

#### Scenario A: Simple Question Generation (No Syllabus Cache Hit)

**Happens when:**
- Teacher creates first assessment for a class/subject

**Process:**
1. Syllabus is cached (assume hit) - 0 tokens
2. Question generation - 2900 tokens avg

**Cost:** 
```
(950 input × $0.00015/1000) + (2000 output × $0.0006/1000)
= $0.000142 + $0.0012
= $0.001342 per assessment
```

---

#### Scenario B: Cold Start (First-Ever Subject)

**Happens when:**
- Brand new subject/class combination
- Syllabus not in database

**Process:**
1. Fetch & parse syllabus - 7500 tokens
2. Question generation - 2900 tokens
3. Total: 10400 tokens

**Cost:**
```
Syllabus Parse: (5000 input × $0.00015/1000) + (2500 output × $0.0006/1000)
              = $0.00075 + $0.0015 = $0.00225

Question Gen:   (950 input × $0.00015/1000) + (2000 output × $0.0006/1000)
              = $0.000142 + $0.0012 = $0.001342

Total: $0.003592 per assessment
```

**BUT:** This only happens once per subject, then cached for 6 months.

---

#### Scenario C: State Board / Multi-Language

**Classes 6-10 with Three Language Formula:**
- English Medium with English (FL), Telugu (SL), Hindi (TL)
- Same process as above but potentially 3x cost for language variants

**Cost per language:** $0.001342 (similar to Scenario A)
**For 3 languages:** ~$0.004 per chapter

---

### 5.3 Monthly Cost Estimates

#### Assumption: Active Usage Scenario
- **Teacher Base:** 50 teachers
- **Avg Assessments/Teacher/Month:** 10
- **Total Assessments/Month:** 500
- **New Syllabus Fetches/Month:** 15 (Classes 9-12, ~15 subjects × ~1 refresh)

**Monthly Calculation:**

```
Question Generation:
  500 assessments × $0.001342 = $0.671

New Syllabus Parsing:
  15 syllabi × $0.00225 = $0.0338

TOTAL MONTHLY: $0.705
TOTAL ANNUAL: $8.46
```

**Per Student Perspective** (5000 students):
- Annual: $8.46 ÷ 5000 = $0.0017 per student
- Monthly: $0.71 ÷ 5000 = $0.00014 per student

---

#### Assumption: Heavy Usage Scenario
- **Teachers:** 200
- **Avg Assessments/Teacher/Month:** 20
- **Total Assessments/Month:** 4000
- **New Syllabi/Month:** 30

**Monthly Calculation:**

```
Question Generation:
  4000 assessments × $0.001342 = $5.368

New Syllabus Parsing:
  30 syllabi × $0.00225 = $0.0675

TOTAL MONTHLY: $5.436
TOTAL ANNUAL: $65.23
```

**Per Student** (20,000 students):
- Annual: $65.23 ÷ 20,000 = $0.00326 per student
- Monthly: $5.44 ÷ 20,000 = $0.00027 per student

---

#### Assumption: Enterprise Scale
- **Teachers:** 500
- **Students:** 50,000
- **Avg Assessments/Teacher/Month:** 25
- **Total Assessments/Month:** 12,500
- **New Syllabi/Month:** 50

**Monthly Calculation:**

```
Question Generation:
  12,500 assessments × $0.001342 = $16.775

New Syllabus Parsing:
  50 syllabi × $0.00225 = $0.1125

TOTAL MONTHLY: $16.888
TOTAL ANNUAL: $202.65
```

**Per Student** (50,000 students):
- Annual: $202.65 ÷ 50,000 = $0.00405 per student
- Monthly: $16.89 ÷ 50,000 = $0.00034 per student

---

## SECTION 6: DATABASE SCHEMA (AI-Generated Content Storage)

### Tables Storing AI Content:

#### 1. **question_bank** (Questions Generated by AI)
```sql
Columns:
  - id (PK)
  - assessment_id (FK)
  - question (TEXT) ← AI GENERATED
  - options (JSON) ← AI GENERATED
  - correct_answer (CHAR) ← AI PROVIDED
  - difficulty (VARCHAR) ← AI PROVIDED
  
Growth Rate:
  10 questions × 500 assessments/month = 5,000 rows/month
  = 60,000 rows/year
  ≈ 20-30 MB/year (compressed with indices)
```

#### 2. **syllabus_topics** (Parsed by AI)
```sql
Columns:
  - id (PK)
  - syllabus_id (FK)
  - unit_number, unit_name
  - chapter_number, chapter_name
  - subtopics (JSON) ← AI PARSED
  - learning_outcomes (JSON) ← AI PARSED
  - key_concepts (JSON) ← AI PARSED
  - content_details (TEXT)
  - weightage (INT) ← AI PROVIDED
  - difficulty_level (VARCHAR) ← AI PROVIDED
  
Growth Rate:
  ~100-200 topics per syllabus
  ~15-20 new syllabi per year = 1500-4000 topics/year
  ≈ 5-10 MB/year
```

#### 3. **syllabus_master** (Full Syllabus Content)
```sql
Columns:
  - id (PK)
  - content_extracted (TEXT) ← FULL SYLLABUS TEXT
  - content_sha256 (VARCHAR) ← For version control
  - last_updated (TIMESTAMP)
  
Growth Rate:
  ~50-100 KB per syllabus (PDF-derived text)
  ~15-20 syllabi/year = 750 KB - 2 MB/year
```

#### 4. **syllabus_fetch_log** (Audit Trail)
```sql
Tracks every AI operation:
  - fetch_status
  - duration_ms
  - error_message
  - attempt (retry count)
  
1 log entry per syllabus fetch/parse attempt
```

---

## SECTION 7: API CALL PATTERNS

### Per User Action Call Frequency:

| User Action | AI Calls | Timing | Frequency |
|-------------|----------|--------|-----------|
| **Teacher Creates Assessment** | 1 (Question Gen) | Background | Per assessment |
| **Student Views Subjects** | 0 | Synchronous | Per class selection |
| **Student Views Chapters** | 0* | Synchronous | Per subject selection |
| **Student Takes Exam** | 0 | Synchronous | During exam |
| **Teacher Views Results** | 0 | Synchronous | On demand |

**Note:** *Subjects/Chapters are fetched from cached database, no AI calls

### Backend API Endpoints Summary:

**Question Generation:**
- `POST /teacher/create-assessment` → Triggers AI question generation

**Syllabus Management:**
- `GET /syllabus/subjects/{class}` → Returns cached subjects
- `GET /syllabus/topics/{class}/{subject}` → Returns cached topics (or triggers AI parse on first call)
- `POST /syllabus/fetch/{class}/{subject}` → Force refresh (triggers AI parse)

**Student Assessment:**
- `GET /student/assessments/{class}/{section}` → Read from DB
- `GET /student/assessment/{id}/questions` → Read from question_bank
- `POST /student/submit-exam` → Auto-grade (no AI)

---

## SECTION 8: TOKEN USAGE PATTERNS ANALYSIS

### Pattern 1: Monthly Lifecycle

```
Week 1: 
  - Teachers start creating assessments
  - High question generation calls
  - Low syllabus parsing (most cached)
  
Weeks 2-4:
  - Continued assessments
  - Occasional new syllabi
  - Mostly cache hits

Pattern: Front-loaded costs in first week, then plateau
```

### Pattern 2: Seasonal Patterns

```
Academic Year Cycle (India):
  April-June: School starts
    - Peak syllabus discovery (all subjects needed)
    - Peak assessment creation
    - HIGHEST TOKEN USAGE
    
  July-September: Mid-term
    - Normal assessment creation
    - Minimal new syllabus (cached)
    - NORMAL USAGE
    
  October-November: Mid-year
    - Revisions begin
    - NORMAL USAGE
    
  December-March: Final exams
    - Peak assessments again
    - HIGHEST TOKEN USAGE

Recommendation: Budget 3-4x normal usage for April-June and Dec-March
```

### Pattern 3: Per-Student Impact

**Hidden Question:** How much do students indirectly trigger AI?

**Answer:** Not directly. Questions are pre-generated by teacher.

**Exception:** If teacher creates assessment during class:
- Teacher: 1 AI call
- Students: 0 AI calls (questions already generated)
- Cost: Amortized across all students in class

**Example:**
- 40 students take 10-question exam
- 1 teacher triggered 1 AI call (10 questions, ~2900 tokens)
- Cost: $0.001342 ÷ 40 = $0.000034 per student

---

## SECTION 9: POTENTIAL OPTIMIZATION OPPORTUNITIES

### 1. Batch Question Generation
**Current:** Generate 10 questions per assessment
**Opportunity:** Generate 100 questions once, reuse across multiple assessments

**Savings:** 90% reduction in question generation calls
**Risk:** Less variation, higher cost per question batch

### 2. Cached Syllabus Reuse
**Current:** Parse syllabus when first teacher requests
**Opportunity:** Pre-parse all CBSE syllabi on server startup

**Savings:** Eliminate all syllabus parsing calls after initialization
**Impact:** 7500 tokens × 15-20 syllabi = 112,500 - 150,000 tokens saved/month
**Annual Savings:** $1.35 - $1.80

### 3. Lighter-Weight Models for Parsing
**Current:** GPT-4o Mini for all tasks
**Opportunity:** Use cheaper models like Claude 3.5 Haiku for parsing

**Potential Savings:** 30-50% on parsing costs
**Risk:** Lower quality parsing

### 4. Local LLM for Question Generation
**Current:** Cloud-based GPT-4o Mini
**Opportunity:** Run local Llama 2 or Mistral for question generation

**Savings:** $0 marginal cost
**Risk:** Quality issues, infrastructure costs

---

## SECTION 10: COST PROJECTION TABLE

| Metric | Base Case | Growth 2x | Growth 5x | Enterprise |
|--------|-----------|-----------|-----------|------------|
| Monthly Assessments | 500 | 1,000 | 2,500 | 12,500 |
| Monthly Cost (AI) | $0.71 | $1.42 | $3.55 | $16.89 |
| Annual Cost (AI) | $8.46 | $16.92 | $42.30 | $202.65 |
| Cost/Student/Year | $0.0017 | $0.00085 | $0.00085 | $0.004 |
| Cost/Assessment | $0.001342 | $0.001342 | $0.001342 | $0.001342 |

**Observation:** Costs scale linearly with usage. Per-student cost decreases as user base grows.

---

## SECTION 11: IMPLEMENTATION TIMELINE

### Phase 1: Current State (Delivered)
- Question generation working
- Syllabus service working
- Database schema in place
- Classes 1-8 pre-loaded

### Phase 2: Production Ready
- Pre-load all CBSE syllabi (save on AI parsing)
- Implement caching at API layer
- Add monitoring for token usage

### Phase 3: Optimization
- Batch processing for peak times
- Consider local models for parsing
- Implement token budgeting system

---

## SECTION 12: KEY FILES REFERENCE

| File | Purpose | AI Usage |
|------|---------|----------|
| `/home/hub_ai/ls/backend/app/ai_question_gen.py` | Question generation | **HIGH** - 1 call per assessment |
| `/home/hub_ai/ls/backend/app/syllabus_service_v2.py` | Syllabus parsing & caching | **MEDIUM** - 1 call per new subject |
| `/home/hub_ai/ls/backend/app/teacher.py` | Routes teacher requests | **INDIRECT** - triggers AI calls |
| `/home/hub_ai/ls/backend/app/models.py` | Database schema | Stores AI content |
| `/home/hub_ai/ls/backend/app/syllabus_routes.py` | API endpoints | Manages cached content |

---

## SECTION 13: SUMMARY & RECOMMENDATIONS

### Current AI Architecture
- **Provider:** OpenRouter (GPT-4o Mini)
- **Primary Use:** Question generation (per assessment)
- **Secondary Use:** Syllabus structure parsing (once per subject)
- **Questions Generated:** 10 per assessment
- **Cost:** ~$0.0013 per assessment

### Monthly Cost Breakdown (500 assessments scenario)
- Question Generation: $0.67/month
- Syllabus Parsing: $0.03/month (with 6-month caching)
- **Total:** ~$0.70/month (~$8.46/year)

### Recommendations
1. **Maintain Current Setup** - Costs are minimal and quality is good
2. **Monitor Peak Seasons** - Budget 3-4x normal for April-June and Dec-March
3. **Implement Cost Tracking** - Add API call logging for budget monitoring
4. **Consider Pre-loading** - Load all syllabi on startup to eliminate parsing calls
5. **Plan for Scale** - Linear scaling expected up to 50,000 students

### Break-Even Analysis
At $0.001342 per assessment, **100 assessments = $0.134 cost**
- Typical school subscription: $10-50/month
- Pure AI costs: <1% of revenue

---

## APPENDIX: TOKEN CALCULATION METHODOLOGY

### How Tokens are Calculated

**OpenRouter uses OpenAI's tokenizer:**
- 1 token ≈ 4 characters (average)
- 1 token ≈ 0.75 words (average)

**For 3000 characters of syllabus content:**
```
3000 chars ÷ 4 chars/token = 750 tokens
```

**For 15,000 characters of syllabus content:**
```
15,000 chars ÷ 4 chars/token = 3,750 tokens
```

**For 10-question JSON output:**
```
Approximately 1,500-2,000 tokens
(Each MCQ with question, 4 options, answer, difficulty)
```

---

**Report Generated:** October 21, 2025  
**Data Source:** Code analysis of `/home/hub_ai/ls/backend/`  
**Accuracy:** High confidence for current implementation  
**Last Updated:** Real-time from codebase

