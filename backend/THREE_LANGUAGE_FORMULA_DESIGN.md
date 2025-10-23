# Three Language Formula - Implementation Design
## State Boards (Classes 6-10) - English Medium

---

## 1. The Three Language Formula

### Background
Indian schools follow the **Three Language Formula** established by the National Education Policy:
- **First Language (L1/FL)**: Primary language of instruction (English for English medium)
- **Second Language (L2/SL)**: Regional language (Telugu in Telangana/AP)
- **Third Language (L3/TL)**: Additional language (Hindi, Sanskrit, etc.)

### School Configurations

#### **Configuration A: Regional Focus** (Most Common in Telangana/AP)
```
1️⃣ English (FL)   - First Language textbook
2️⃣ Telugu (SL)    - Second Language textbook
3️⃣ Hindi (TL)     - Third Language textbook
```

#### **Configuration B: National Focus**
```
1️⃣ English (FL)   - First Language textbook
2️⃣ Hindi (SL)     - Second Language textbook
3️⃣ Telugu (TL)    - Third Language textbook
```

#### **Configuration C: Sanskrit Option**
```
1️⃣ English (FL)   - First Language textbook
2️⃣ Telugu (SL)    - Second Language textbook
3️⃣ Sanskrit (TL)  - Third Language textbook
```

---

## 2. Database Schema Design (RECOMMENDED)

### Add Three Language Columns

```sql
-- Migration: Add three language support
ALTER TABLE syllabus_master
ADD COLUMN language_position VARCHAR(20);  -- 'FL', 'SL', 'TL', or NULL for non-language subjects

CREATE INDEX idx_syllabus_language_position ON syllabus_master(language_position);

-- Optional: Track which languages a school offers
CREATE TABLE school_language_config (
    id SERIAL PRIMARY KEY,
    school_id INT,  -- If you have schools table
    class_name VARCHAR(10) NOT NULL,
    first_language VARCHAR(50) NOT NULL,   -- 'English'
    second_language VARCHAR(50) NOT NULL,  -- 'Telugu' or 'Hindi'
    third_language VARCHAR(50),            -- 'Hindi', 'Telugu', 'Sanskrit', etc.
    medium VARCHAR(20) NOT NULL,           -- 'English'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Example Data Records

```sql
-- English as FL (same for all configurations)
INSERT INTO syllabus_master (
    board, class_name, subject, language_position, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'English', 'FL', 'English', 'English - Class 6 (Part I)'
);

-- Telugu as SL (Configuration A & C)
INSERT INTO syllabus_master (
    board, class_name, subject, language_position, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'Telugu', 'SL', 'English', 'Telugu - Class 6 (Part II)'
);

-- Telugu as TL (Configuration B)
INSERT INTO syllabus_master (
    board, class_name, subject, language_position, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'Telugu', 'TL', 'English', 'Telugu - Class 6 (Part III)'
);

-- Hindi as SL (Configuration B)
INSERT INTO syllabus_master (
    board, class_name, subject, language_position, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'Hindi', 'SL', 'English', 'Hindi - Class 6 (Part II)'
);

-- Hindi as TL (Configuration A)
INSERT INTO syllabus_master (
    board, class_name, subject, language_position, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'Hindi', 'TL', 'English', 'Hindi - Class 6 (Part III)'
);

-- Mathematics (no language position)
INSERT INTO syllabus_master (
    board, class_name, subject, medium, textbook_name
) VALUES (
    'TSBSE', '6', 'Mathematics', 'English', 'Mathematics - Class 6'
);
```

---

## 3. Data Structure (Python)

### Complete Structure for Classes 6-10

```python
TELANGANA_6_10_ENGLISH_MEDIUM = {
    "6": {
        # First Language (FL) - Always English for English medium
        "English_FL": {
            "textbook_name": "English - Class 6 (Part I)",
            "language_position": "FL",
            "chapters": [
                "A Tale of Two Birds",
                "The Friendly Mongoose",
                "The Shepherd's Treasure",
                # ... more chapters
            ]
        },

        # Second Language (SL) - Telugu OR Hindi
        "Telugu_SL": {
            "textbook_name": "Telugu - Class 6 (Part II)",
            "language_position": "SL",
            "chapters": [
                "వనం", "పక్షులు", "నీటి చుక్క",
                # ... more Telugu chapters
            ]
        },
        "Hindi_SL": {
            "textbook_name": "Hindi - Class 6 (Part II)",
            "language_position": "SL",
            "chapters": [
                "वह चिड़िया जो", "बचपन", "नादान दोस्त",
                # ... more Hindi chapters
            ]
        },

        # Third Language (TL) - Hindi, Telugu, or Sanskrit
        "Hindi_TL": {
            "textbook_name": "Hindi - Class 6 (Part III)",
            "language_position": "TL",
            "chapters": [
                "वह चिड़िया जो", "बचपन", "नादान दोस्त",
                # ... simplified/basic Hindi chapters
            ]
        },
        "Telugu_TL": {
            "textbook_name": "Telugu - Class 6 (Part III)",
            "language_position": "TL",
            "chapters": [
                "వనం", "పక్షులు", "నీటి చుక్క",
                # ... simplified/basic Telugu chapters
            ]
        },
        "Sanskrit_TL": {
            "textbook_name": "Sanskrit - Class 6 (Part III)",
            "language_position": "TL",
            "chapters": [
                "शब्द परिचयः", "सुभाषितानि", "पठनीयाः",
                # ... Sanskrit chapters
            ]
        },

        # Core Subjects (same for all students)
        "Mathematics": {
            "textbook_name": "Mathematics - Class 6",
            "chapters": [
                "Knowing Our Numbers",
                "Whole Numbers",
                "Playing with Numbers",
                # ... more chapters
            ]
        },
        "Science": {
            "textbook_name": "Science - Class 6",
            "chapters": [
                "Food: Where Does it Come From?",
                "Components of Food",
                "Fibre to Fabric",
                # ... more chapters
            ]
        },
        "Social Studies": {
            "textbook_name": "Social Studies - Class 6",
            "chapters": [
                "Reading and Making Maps",
                "Globe: Model of the Earth",
                "Land Forms",
                # ... more chapters
            ]
        }
    },
    # Classes 7-10 follow similar pattern
}
```

---

## 4. API Design

### Enhanced API with Language Position

```python
def generate_and_store_questions(
    assessment_id: int,
    class_name: str,
    subject: str,
    chapter: str,
    board_code: str = 'CBSE',
    medium: str = 'English',
    language_position: str = None  # 'FL', 'SL', 'TL', or None
):
    """
    Generate questions with language position support

    Args:
        language_position:
            - 'FL' for First Language
            - 'SL' for Second Language
            - 'TL' for Third Language
            - None for non-language subjects (Math, Science, etc.)
    """
    pass
```

### Example Usage

```python
# Configuration A: Regional Focus (English, Telugu, Hindi)

# First Language - English
generate_and_store_questions(
    class_name='6',
    subject='English',
    chapter='A Tale of Two Birds',
    board_code='TSBSE',
    medium='English',
    language_position='FL'
)

# Second Language - Telugu
generate_and_store_questions(
    class_name='6',
    subject='Telugu',
    chapter='వనం',
    board_code='TSBSE',
    medium='English',
    language_position='SL'
)

# Third Language - Hindi
generate_and_store_questions(
    class_name='6',
    subject='Hindi',
    chapter='वह चिड़िया जो',
    board_code='TSBSE',
    medium='English',
    language_position='TL'
)

# Core Subject - Mathematics (no language position)
generate_and_store_questions(
    class_name='6',
    subject='Mathematics',
    chapter='Knowing Our Numbers',
    board_code='TSBSE',
    medium='English',
    language_position=None
)
```

---

## 5. Syllabus Query Logic

### Smart Language Position Inference

```python
def infer_language_position(subject: str, medium: str,
                           school_config: dict = None) -> str:
    """
    Infer language position based on school configuration

    Default for English Medium:
    - English → FL
    - Telugu → SL (default for Telangana/AP)
    - Hindi → TL (default)
    """
    if not school_config:
        # Default configuration (Regional Focus)
        school_config = {
            'first_language': 'English',
            'second_language': 'Telugu',
            'third_language': 'Hindi'
        }

    subject_lower = subject.lower()

    # Check each position
    if subject_lower == school_config['first_language'].lower():
        return 'FL'
    elif subject_lower == school_config['second_language'].lower():
        return 'SL'
    elif subject_lower == school_config['third_language'].lower():
        return 'TL'

    return None  # Not a language subject
```

### Database Query

```python
def get_syllabus(self, class_name, subject, board_code, medium,
                language_position=None):
    """
    Get syllabus with language position support
    """
    query = self.db.query(SyllabusMaster).filter(
        SyllabusMaster.class_name == class_name,
        SyllabusMaster.subject.ilike(subject),
        SyllabusMaster.board == board_code,
        SyllabusMaster.medium.ilike(medium)
    )

    # For language subjects, filter by position
    if language_position:
        query = query.filter(
            SyllabusMaster.language_position == language_position
        )
    else:
        # For non-language subjects, ensure no language position
        query = query.filter(
            SyllabusMaster.language_position.is_(None)
        )

    return query.first()
```

---

## 6. Frontend Implications

### Assessment Creation Form

```
Select Board: [CBSE ▼] [TSBSE ▼] [BSEAP ▼]
Select Class: [6 ▼]
Select Medium: [English ▼]
Select Subject: [English ▼] [Telugu ▼] [Hindi ▼] [Mathematics ▼] [Science ▼] [Social Studies ▼]

⚠️ For Language Subjects:
Select Language Level:
  ○ First Language (Part I)
  ○ Second Language (Part II)  ← Default for Telugu in English medium
  ○ Third Language (Part III)

Select Chapter: [Chapter list based on selection ▼]
```

---

## 7. Implementation Steps

### Step 1: Add language_position Column ✅
```sql
ALTER TABLE syllabus_master ADD COLUMN language_position VARCHAR(20);
CREATE INDEX idx_syllabus_language_position ON syllabus_master(language_position);
```

### Step 2: Update Models 🔧
```python
class SyllabusMaster(Base):
    # ... existing columns ...
    language_position = Column(String(20))  # 'FL', 'SL', 'TL', or NULL
```

### Step 3: Research & Create Data Structure 📝
For **each board** (TSBSE, BSEAP), **each class** (6-10), collect:

**Language Subjects (3 versions each):**
- English (FL) - Part I textbook
- Telugu (SL) - Part II textbook
- Telugu (TL) - Part III textbook
- Hindi (SL) - Part II textbook
- Hindi (TL) - Part III textbook
- Sanskrit (TL) - Part III textbook (optional)

**Core Subjects (1 version each):**
- Mathematics
- Science
- Social Studies

### Step 4: Load Data 📊
```python
python load_state_board_classes_6_10.py
```

### Step 5: Update Question Generation 🔧
Add `language_position` parameter to `generate_and_store_questions()`

### Step 6: Test All Configurations ✅
Test with:
- Configuration A: English (FL), Telugu (SL), Hindi (TL)
- Configuration B: English (FL), Hindi (SL), Telugu (TL)
- Configuration C: English (FL), Telugu (SL), Sanskrit (TL)

---

## 8. Data Volume Estimate

### For English Medium (Classes 6-10)

**Per Board (TSBSE or BSEAP):**
- 5 classes × 8 subjects* = 40 syllabi
- Estimated 15-20 chapters per subject
- Total: ~600-800 chapters per board

*8 subjects:
1. English (FL)
2. Telugu (SL)
3. Telugu (TL)
4. Hindi (SL)
5. Hindi (TL)
6. Mathematics
7. Science
8. Social Studies

**Total for Both Boards:**
- 80 syllabi (2 boards × 40 syllabi)
- ~1200-1600 chapters

---

## 9. Simplified Start (RECOMMENDED)

### Phase 1A: Support Most Common Configuration Only

For **English Medium with Regional Focus** (85% of schools in Telangana/AP):
```
1️⃣ English (FL)
2️⃣ Telugu (SL)
3️⃣ Hindi (TL)
+ Mathematics, Science, Social Studies
```

**Syllabi to load:**
- 2 boards × 5 classes × 6 subjects = **60 syllabi**
- Estimated **~900 chapters**

### Phase 1B: Add Alternative Configurations Later

Add support for:
- Configuration B (Hindi as SL)
- Configuration C (Sanskrit as TL)

---

## 10. Final Recommendation

### ✅ RECOMMENDED APPROACH:

**Step 1:** Add `language_position` column to database
**Step 2:** Start with **Configuration A only** (Regional Focus)
- English (FL)
- Telugu (SL)
- Hindi (TL)
- Mathematics, Science, Social Studies

**Step 3:** Load data for 2 boards × 5 classes × 6 subjects = **60 syllabi**

**Step 4:** Test question generation with language positions

**Step 5 (Later):** Add alternative configurations (Hindi SL, Sanskrit TL, etc.)

---

## Summary

✅ **Three Language Formula Support:**
- First Language (FL) - Part I textbook
- Second Language (SL) - Part II textbook
- Third Language (TL) - Part III textbook

✅ **Database Design:**
- Add `language_position` column ('FL', 'SL', 'TL', NULL)
- Store each language-level combination separately

✅ **Start Simple:**
- English Medium only
- Configuration A (English-Telugu-Hindi) first
- 60 syllabi, ~900 chapters
- Add other configurations later

Would you like me to:
1. Add the `language_position` column now?
2. Start researching textbook chapters for Classes 6-10?
3. Implement the simplified Configuration A first?
