#!/usr/bin/env python3
"""
Test: Generate AI questions using REAL CBSE syllabus content
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal
from app.syllabus_service_v2 import EnhancedSyllabusService
from app.ai_question_gen import generate_questions
import json

print("="*70)
print("🧪 AI Question Generation Test - Using Real CBSE Content")
print("="*70)

db = SessionLocal()

try:
    service = EnhancedSyllabusService(db)

    # Get syllabus and topics
    print("\n📚 Loading Class 10 Mathematics syllabus...")
    syllabus = service.get_syllabus('10', 'Mathematics')
    topics = service.get_topics('10', 'Mathematics')

    if not topics:
        print("❌ No topics found")
        exit(1)

    # Get first topic (Real Numbers)
    first_topic = topics[0]
    print(f"\n✅ Selected Chapter: {first_topic.chapter_name}")
    print(f"   Unit: {first_topic.unit_name}")

    # Get detailed content
    topic_content = service.get_topic_content(first_topic.id)

    # Extract relevant syllabus section for this chapter
    full_content = topic_content['full_syllabus_content']
    chapter_name = topic_content['chapter_name']

    # Take a relevant chunk (first 3000 chars that mention the chapter)
    if chapter_name.lower() in full_content.lower():
        start_idx = full_content.lower().find(chapter_name.lower())
        syllabus_chunk = full_content[max(0, start_idx-500):start_idx+2500]
    else:
        syllabus_chunk = full_content[:3000]

    print(f"\n📄 Syllabus Content Sample (for {chapter_name}):")
    print(f"   {syllabus_chunk[:400]}...")

    print(f"\n🤖 Generating 5 questions using REAL CBSE content...")
    print(f"   Chapter: {chapter_name}")
    print(f"   This may take 10-20 seconds...\n")

    # Now let's create an enhanced version that uses real content
    from dotenv import load_dotenv
    import requests

    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    prompt = f"""
You are an expert CBSE Class 10 Mathematics question paper setter.

Using the following OFFICIAL CBSE syllabus content for "{chapter_name}",
generate 5 high-quality multiple-choice questions.

OFFICIAL CBSE SYLLABUS CONTENT:
{syllabus_chunk}

REQUIREMENTS:
- Questions MUST be based on the specific content above
- Follow CBSE exam pattern
- Include conceptual and application-based questions
- Ensure options are clear and unambiguous
- Mark difficulty appropriately

Output valid JSON array:
[
  {{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct_answer": "C",
    "difficulty": "medium",
    "topic": "{chapter_name}"
  }}
]
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3003",
        "X-Title": "AI Assessment Platform"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    data = response.json()

    if "error" in data:
        print(f"❌ API Error: {data['error']}")
        exit(1)

    content = data["choices"][0]["message"]["content"]

    # Extract JSON
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()
    else:
        json_str = content.strip()

    questions = json.loads(json_str)

    print(f"✅ Generated {len(questions)} questions!\n")
    print("="*70)

    for i, q in enumerate(questions, 1):
        print(f"\n📝 Question {i} ({q.get('difficulty', 'medium')})")
        print(f"   {q['question']}")
        print(f"\n   Options:")
        for key, value in q['options'].items():
            marker = "✓" if key == q['correct_answer'] else " "
            print(f"     {marker} {key}) {value}")
        print()

    print("="*70)
    print("✅ SUCCESS!")
    print("   Questions are based on REAL CBSE syllabus content")
    print("   NOT generic/placeholder questions!")
    print("="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
