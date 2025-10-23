# Timezone Issue Fix - Assessment Scheduling

## Problem

When teachers scheduled exams, the times were showing incorrectly for students due to timezone conversion issues.

### Root Cause

1. **Frontend** (`CreateAssessment.tsx`):
   - Used `datetime-local` input which gives local browser time
   - Converted to ISO string using `new Date().toISOString()` which converts to UTC
   - This caused a timezone shift (e.g., IST 2:00 PM → UTC 8:30 AM)

2. **Backend** (`student.py`, `models.py`):
   - Used `datetime.utcnow()` for timestamps
   - Tried to compare IST times with UTC times
   - Inconsistent timezone handling between creation and comparison

## Solution

### Frontend Changes ([CreateAssessment.tsx](frontend/src/components/teacher/CreateAssessment.tsx))

Changed datetime handling to preserve IST timezone:

```typescript
// OLD (incorrect):
start_time: new Date(startTime).toISOString()  // Converts to UTC

// NEW (correct):
const formatToIST = (dateTimeLocal: string) => {
  return dateTimeLocal + ':00+05:30';  // Preserve as IST
};
start_time: formatToIST(startTime)
```

### Backend Changes

#### 1. Models ([app/models.py](backend/app/models.py))

- Added `ist_now()` helper function
- Changed `default=datetime.datetime.utcnow` to `default=ist_now`
- Now all timestamps use IST consistently

#### 2. Teacher API ([app/teacher.py](backend/app/teacher.py))

- Strip timezone info from incoming datetime (convert to naive datetime)
- Store times as naive datetimes (no timezone info)
- This prevents timezone conversion issues

#### 3. Student API ([app/student.py](backend/app/student.py))

- Created `get_ist_now()` helper function
- All time comparisons now use naive IST datetimes
- Consistent timezone handling throughout

## How It Works Now

1. **Teacher schedules exam**:
   - Selects time in datetime-local input (e.g., "2025-10-11 14:30")
   - Frontend appends IST offset: "2025-10-11T14:30:00+05:30"
   - Backend strips timezone and stores as naive datetime: "2025-10-11 14:30:00"

2. **Student views exam**:
   - Backend gets current IST time as naive datetime
   - Compares naive datetimes directly (no timezone conversion)
   - Shows correct availability status

3. **All timestamps**:
   - created_at, submitted_at use `ist_now()` function
   - Consistent IST timing across the entire application

## Testing

To test the fix:

1. **Create an assessment** as a teacher:
   - Select a time 5 minutes from now
   - Note the time displayed

2. **View as a student**:
   - Check the "All Assessments" page
   - Verify the time matches what the teacher set
   - Verify the assessment becomes "Available" at the correct time

3. **Check logs**:
   ```bash
   tail -f /home/learnify/learnify-stud/backend/backend.log
   ```
   Look for debug output showing time comparisons

## Files Modified

- `frontend/src/components/teacher/CreateAssessment.tsx`
- `backend/app/models.py`
- `backend/app/teacher.py`
- `backend/app/student.py`

## Services Restarted

Backend service has been restarted to apply changes. Frontend (Vite) automatically reloads with HMR.

---

**Fix applied on**: 2025-10-11
**Status**: ✅ Fixed and deployed
