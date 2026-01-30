import json
import re
from gemini_fallback import gemini_response

def test_quiz_generation():
    """Test quiz generation with proper JSON parsing"""
    
    topic = "Python Programming"
    
    prompt = f"""Generate exactly 5 multiple-choice questions about {topic}. 
    Format as a JSON array where each question has:
    - "question": the question text
    - "options": array of 4 answer choices
    - "answer": the exact correct answer text (not just A/B/C/D)
    
    Example format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris"
      }}
    ]
    
    Make sure answers are educational and accurate. Return only valid JSON."""
    
    try:
        print("Testing quiz generation...")
        response = gemini_response(prompt)
        print(f"Raw response length: {len(response)} characters")
        
        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            print("Found JSON array in response")
            
            try:
                quiz_data = json.loads(json_str)
                print(f"Successfully parsed {len(quiz_data)} questions")
                
                # Validate structure
                valid_count = 0
                for i, q in enumerate(quiz_data):
                    if (isinstance(q, dict) and 
                        'question' in q and 
                        'options' in q and 
                        'answer' in q and
                        isinstance(q['options'], list) and 
                        len(q['options']) >= 4):
                        
                        print(f"Question {i+1}: Valid")
                        print(f"  Q: {q['question'][:50]}...")
                        print(f"  Options: {len(q['options'])}")
                        print(f"  Answer: {q['answer']}")
                        print(f"  Answer in options: {q['answer'] in q['options']}")
                        valid_count += 1
                    else:
                        print(f"Question {i+1}: Invalid structure")
                
                print(f"\nSUCCESS: {valid_count}/{len(quiz_data)} questions are valid")
                return True
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return False
        else:
            print("No JSON array found in response")
            print("Response preview:", response[:200])
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_quiz_generation()