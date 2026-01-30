import requests
import os
from dotenv import load_dotenv

load_dotenv()

def gemini_response(prompt):
    """Get response from Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "API key not configured"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"API Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"