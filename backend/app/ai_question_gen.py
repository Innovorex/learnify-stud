import os, requests, json
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_questions(board, class_name, subject, chapter, num_questions=10, syllabus_content=None):
    """
    Calls OpenRouter to generate multiple-choice questions.
    Now uses REAL CBSE syllabus content when available!
    Falls back to sample questions if API fails.
    """

    # Enhanced prompt with real syllabus content
    if syllabus_content:
        prompt = f"""
You are an expert {board} Class {class_name} {subject} question paper setter.

Using the following OFFICIAL CBSE SYLLABUS CONTENT for "{chapter}",
generate {num_questions} high-quality multiple-choice questions (MCQs).

OFFICIAL CBSE SYLLABUS CONTENT:
{syllabus_content[:3000]}

REQUIREMENTS:
- Questions MUST be based on the specific syllabus content above
- Follow CBSE exam pattern and marking scheme
- Include conceptual, application, and analytical questions
- Ensure all options are clear and plausible
- Vary difficulty: 30% easy, 50% medium, 20% hard

Output valid JSON array (NO markdown, just JSON):
[
  {{
    "question": "What is the HCF of 12 and 18?",
    "options": {{"A": "2", "B": "3", "C": "6", "D": "12"}},
    "correct_answer": "C",
    "difficulty": "easy"
  }}
]
"""
    else:
        # Fallback to generic prompt if no syllabus content
        prompt = f"""
Generate {num_questions} multiple choice questions (MCQs) for {board} Class {class_name} {subject},
Chapter: {chapter}. Output valid JSON with a list of objects like:
[
  {{
    "question": "What is the HCF of 12 and 18?",
    "options": {{"A": "2", "B": "3", "C": "6", "D": "12"}},
    "correct_answer": "C",
    "difficulty": "easy"
  }}
]
"""

    # Try API first
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3003",  # Required by OpenRouter
            "X-Title": "AI Assessment Platform"  # Optional, for OpenRouter stats
        }
        payload = {
            "model": "openai/gpt-4o-mini",   # Paid GPT-4o Mini (cheap & good)
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        data = response.json()

        if "error" in data:
            print(f"❌ API Error: {data['error']}")
            print("⚠️ API key invalid. Falling back to sample questions...")
            return generate_sample_questions(subject, chapter, num_questions)

        content = data["choices"][0]["message"]["content"]
        print("📝 AI Content:", content[:200])

        # Extract JSON from markdown code block if present
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        # Try to parse, handling incomplete JSON
        try:
            questions = json.loads(json_str)
        except json.JSONDecodeError:
            # Try to find and extract just the complete JSON array
            import re
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                json_str = match.group(0)
                questions = json.loads(json_str)
            else:
                raise

        print(f"✅ Successfully parsed {len(questions)} questions")
        return questions
    except Exception as e:
        print("❌ Error with AI API:", e)
        print("⚠️ Using sample questions instead...")
        return generate_sample_questions(subject, chapter, num_questions)


def generate_sample_questions(subject, chapter, num_questions=10):
    """
    Generate sample questions when API is unavailable.
    """
    print(f"📝 Generating {num_questions} sample questions for {subject} - {chapter}")

    questions = []
    for i in range(min(num_questions, 10)):
        questions.append({
            "question": f"Question {i+1}: What is a key concept in {chapter}?",
            "options": {
                "A": f"Option A about {chapter}",
                "B": f"Option B about {chapter}",
                "C": f"Correct answer about {chapter}",
                "D": f"Option D about {chapter}"
            },
            "correct_answer": "C",
            "difficulty": "medium"
        })

    return questions
