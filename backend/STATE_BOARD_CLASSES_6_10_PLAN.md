# State Board Classes 6-10 Implementation Plan
## Telangana & Andhra Pradesh | English Medium

---

## 1. Subject Structure Analysis

### Current (Classes 1-5) - Simple Structure
```
Class 1-5:
- English
- Mathematics
- Environmental Studies (EVS)
```

### Classes 6-10 - Complex Structure with Language Choices

#### **Core Subjects (Compulsory for all)**
- Mathematics
- Science (Physics, Chemistry, Biology integrated)
- Social Studies (History, Geography, Civics, Economics)

#### **Language Subjects (1st & 2nd Language)**

**First Language (FL):**
- Telugu (most common)
- Hindi
- Urdu
- English

**Second Language (SL):**
- English (most common for Telugu/Hindi/Urdu FL students)
- Telugu (for English FL students)
- Hindi
- Sanskrit

#### **Typical Combinations:**
1. **Most Common (Telugu Medium):**
   - 1st Language: Telugu
   - 2nd Language: English

2. **English Medium (Our Focus):**
   - 1st Language: English
   - 2nd Language: Telugu/Hindi

3. **Other Combinations:**
   - 1st Language: Hindi, 2nd Language: English
   - 1st Language: Urdu, 2nd Language: English

---

## 2. Database Schema Design

### Option A: Separate Language Columns (Recommended)
```sql
ALTER TABLE syllabus_master
ADD COLUMN first_language VARCHAR(50);

ALTER TABLE syllabus_master
ADD COLUMN second_language VARCHAR(50);

ALTER TABLE syllabus_master
ADD COLUMN language_category VARCHAR(20); -- 'FL' or 'SL' or NULL for non-language subjects
```

**Example Records:**
```sql
-- Telugu as First Language (FL)
INSERT INTO syllabus_master (
    board, class_name, subject, language_category,
    first_language, medium
) VALUES (
    'TSBSE', '6', 'Telugu', 'FL', 'Telugu', 'Telugu'
);

-- English as Second Language (SL) for Telugu medium students
INSERT INTO syllabus_master (
    board, class_name, subject, language_category,
    second_language, medium
) VALUES (
    'TSBSE', '6', 'English', 'SL', 'English', 'Telugu'
);

-- English as First Language (FL) for English medium students
INSERT INTO syllabus_master (
    board, class_name, subject, language_category,
    first_language, medium
) VALUES (
    'TSBSE', '6', 'English', 'FL', 'English', 'English'
);

-- Mathematics (no language category - core subject)
INSERT INTO syllabus_master (
    board, class_name, subject, medium
) VALUES (
    'TSBSE', '6', 'Mathematics', 'English'
);
```

### Option B: Subject Code System (More Scalable)
```sql
-- Use subject codes like NCERT/CBSE
-- Example codes:
--   101 = Telugu (FL)
--   102 = Hindi (FL)
--   103 = English (FL)
--   201 = English (SL)
--   202 = Telugu (SL)
--   203 = Hindi (SL)
--   204 = Sanskrit (SL)
--   041 = Mathematics
--   086 = Science
--   087 = Social Studies

ALTER TABLE syllabus_master
ADD COLUMN subject_code VARCHAR(10);

ALTER TABLE syllabus_master
ADD COLUMN language_type VARCHAR(20); -- 'first_language', 'second_language', or NULL
```

---

## 3. Implementation Strategy

### Phase 1: English Medium Only (Simplified Start)

**For English Medium Students (Classes 6-10):**

```
Required Subjects:
├── English (First Language) ← FL textbook
├── Telugu/Hindi (Second Language) ← SL textbook
├── Mathematics
├── Science
└── Social Studies
```

**Data Structure:**
```python
TELANGANA_6_10_ENGLISH_MEDIUM = {
    "6": {
        "English_FL": {  # First Language
            "textbook_name": "English - Class 6 (First Language)",
            "language_category": "FL",
            "chapters": [...]
        },
        "Telugu_SL": {  # Second Language
            "textbook_name": "Telugu - Class 6 (Second Language)",
            "language_category": "SL",
            "chapters": [...]
        },
        "Hindi_SL": {  # Alternative Second Language
            "textbook_name": "Hindi - Class 6 (Second Language)",
            "language_category": "SL",
            "chapters": [...]
        },
        "Mathematics": {
            "textbook_name": "Mathematics - Class 6",
            "chapters": [...]
        },
        "Science": {
            "textbook_name": "Science - Class 6",
            "chapters": [...]
        },
        "Social Studies": {
            "textbook_name": "Social Studies - Class 6",
            "chapters": [...]
        }
    },
    # Classes 7-10 follow same pattern
}
```

### Phase 2: Multi-Medium Support (Future)

Add support for Telugu medium, Hindi medium, etc.

---

## 4. Frontend/API Changes

### Current API:
```python
generate_and_store_questions(
    class_name='5',
    subject='Mathematics',
    chapter='The Fish Tale',
    board_code='TSBSE',
    medium='English'
)
```

### Enhanced API for Classes 6-10:
```python
generate_and_store_questions(
    class_name='6',
    subject='English',
    chapter='Chapter 1',
    board_code='TSBSE',
    medium='English',
    language_category='FL',  # NEW: 'FL' or 'SL' for language subjects
    first_language='English',  # NEW: Optional
    second_language='Telugu'  # NEW: Optional
)
```

### Alternative Simplified API:
```python
# Let system infer language category based on medium
generate_and_store_questions(
    class_name='6',
    subject='English',  # System knows: English medium → English is FL
    chapter='Chapter 1',
    board_code='TSBSE',
    medium='English'
)

generate_and_store_questions(
    class_name='6',
    subject='Telugu',  # System knows: English medium → Telugu is SL
    chapter='Chapter 1',
    board_code='TSBSE',
    medium='English'
)
```

---

## 5. Subject Mapping Logic

### Inference Rules for English Medium:

```python
def get_language_category(subject: str, medium: str) -> str:
    """
    Determine if a language subject is FL or SL based on medium
    """
    if medium == 'English':
        if subject.lower() == 'english':
            return 'FL'  # English is First Language
        elif subject.lower() in ['telugu', 'hindi', 'sanskrit']:
            return 'SL'  # Other languages are Second Language

    elif medium == 'Telugu':
        if subject.lower() == 'telugu':
            return 'FL'  # Telugu is First Language
        elif subject.lower() in ['english', 'hindi', 'sanskrit']:
            return 'SL'  # Other languages are Second Language

    elif medium == 'Hindi':
        if subject.lower() == 'hindi':
            return 'FL'  # Hindi is First Language
        elif subject.lower() in ['english', 'telugu', 'sanskrit']:
            return 'SL'  # Other languages are Second Language

    return None  # Not a language subject (Math, Science, etc.)
```

---

## 6. Database Query Examples

### Get Syllabus for English Medium Student (Class 6):

```sql
-- First Language (English)
SELECT * FROM syllabus_master
WHERE board = 'TSBSE'
AND class_name = '6'
AND subject = 'English'
AND medium = 'English'
AND language_category = 'FL';

-- Second Language (Telugu)
SELECT * FROM syllabus_master
WHERE board = 'TSBSE'
AND class_name = '6'
AND subject = 'Telugu'
AND medium = 'English'
AND language_category = 'SL';

-- Core subjects (no language category)
SELECT * FROM syllabus_master
WHERE board = 'TSBSE'
AND class_name = '6'
AND subject IN ('Mathematics', 'Science', 'Social Studies')
AND medium = 'English'
AND language_category IS NULL;
```

---

## 7. Implementation Steps

### Step 1: Update Database Schema ✅ READY TO IMPLEMENT
```sql
ALTER TABLE syllabus_master ADD COLUMN language_category VARCHAR(20);
CREATE INDEX idx_syllabus_language_category ON syllabus_master(language_category);
```

### Step 2: Create Data Structure (Classes 6-10) 📝 RESEARCH NEEDED
- Research SCERT Telangana textbooks for Classes 6-10
- Research SCERT AP textbooks for Classes 6-10
- Map all chapter names for:
  - English (FL)
  - Telugu (SL)
  - Hindi (SL) - optional
  - Mathematics
  - Science
  - Social Studies

### Step 3: Update Models 🔧 CODE CHANGE
```python
class SyllabusMaster(Base):
    # ... existing columns ...
    language_category = Column(String(20))  # 'FL', 'SL', or NULL
```

### Step 4: Update Syllabus Service 🔧 CODE CHANGE
```python
def get_syllabus(self, class_name, subject, board_code, medium,
                language_category=None):
    query = self.db.query(SyllabusMaster).filter(
        SyllabusMaster.class_name == class_name,
        SyllabusMaster.subject.ilike(subject),
        SyllabusMaster.board == board_code,
        SyllabusMaster.medium.ilike(medium)
    )

    # Filter by language category if specified
    if language_category:
        query = query.filter(SyllabusMaster.language_category == language_category)

    return query.first()
```

### Step 5: Load Data 📊 DATA IMPORT
```python
# Run data loader for Classes 6-10
python load_state_board_classes_6_10.py
```

### Step 6: Test Question Generation ✅ TESTING
```python
# Test English (FL)
generate_questions(class_name='6', subject='English',
                  board_code='TSBSE', medium='English')

# Test Telugu (SL)
generate_questions(class_name='6', subject='Telugu',
                  board_code='TSBSE', medium='English')

# Test Mathematics (core)
generate_questions(class_name='6', subject='Mathematics',
                  board_code='TSBSE', medium='English')
```

---

## 8. Recommended Approach (SIMPLE START)

### For English Medium Only (Classes 6-10):

**Store as separate subject entries:**
```python
subjects = [
    "English",        # Implicitly FL for English medium
    "Telugu",         # Implicitly SL for English medium
    "Mathematics",    # Core
    "Science",        # Core
    "Social Studies"  # Core
]
```

**Let the system infer FL/SL based on:**
- If medium = 'English' and subject = 'English' → It's FL textbook
- If medium = 'English' and subject = 'Telugu' → It's SL textbook

**No need for complex language_category initially!**

### When to Add Language Category?

Only add `language_category` column when:
1. Supporting multiple mediums (Telugu medium, Hindi medium)
2. Need to distinguish between FL and SL explicitly
3. Have students choosing different language combinations

---

## 9. Data Collection Plan

### Immediate Actions:

1. **Research SCERT Websites:**
   - Telangana: https://scert.telangana.gov.in/
   - AP: https://cse.ap.gov.in/

2. **Identify Textbooks for Classes 6-10:**
   - English (FL) - List all chapter names
   - Telugu (SL) - List all chapter names
   - Mathematics - List all chapter names
   - Science - List all chapter names
   - Social Studies - List all chapter names

3. **Create Data Structure File:**
   ```
   state_board_structure_6_10_telangana_ap.py
   ```

4. **Estimate Data Volume:**
   - 2 boards × 5 classes × 5 subjects = 50 syllabi
   - Estimated ~20 chapters per subject
   - Total: ~1000 chapters

---

## 10. Final Recommendation

### START SIMPLE:

**Phase 1 (Recommended Now):**
- English Medium only
- Classes 6-10
- 5 subjects per class:
  - English (understood as FL)
  - Telugu (understood as SL)
  - Mathematics
  - Science
  - Social Studies
- **No language_category column needed yet**
- Use existing schema with clear naming convention

**Phase 2 (Future):**
- Add language_category column
- Support Telugu medium
- Support Hindi medium
- Support language choice variations

---

## Summary

✅ **Simplest Approach for English Medium (Classes 6-10):**

1. Add `language_category` column to schema (optional but recommended)
2. Research and map chapter names for 5 subjects × 5 classes × 2 boards
3. Load data with clear subject naming (English, Telugu, Mathematics, Science, Social Studies)
4. System infers FL/SL based on medium
5. No complex API changes needed initially

**Total Data to Add:**
- 50 syllabi (2 boards × 5 classes × 5 subjects)
- ~1000 chapters
- English medium only

Would you like me to:
1. Add the `language_category` column to database?
2. Research the textbook structure for Classes 6-10?
3. Start implementing the data structure?
