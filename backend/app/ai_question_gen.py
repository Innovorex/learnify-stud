import os, requests, json
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_questions(board, class_name, subject, chapter, num_questions=10):
    """
    Calls OpenRouter to generate multiple-choice questions.
    """
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

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",   # 100% FREE model!
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    data = response.json()

    print("🔍 API Response:", data)

    try:
        content = data["choices"][0]["message"]["content"]
        print("📝 AI Content:", content[:200])  # Print first 200 chars

        # Extract JSON from markdown code block if present
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        questions = json.loads(json_str)
        print(f"✅ Successfully parsed {len(questions)} questions")
        return questions
    except Exception as e:
        print("❌ Error parsing AI output:", e)
        print("📋 Full response:", data)
        return []
