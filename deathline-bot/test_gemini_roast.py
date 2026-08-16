#!/usr/bin/env python3
"""
Quick test to check if Gemini API roast system works.
Shows what Gemini does and why it might fail.
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"
ROAST_SYSTEM_PROMPT = os.getenv("ROAST_SYSTEM_PROMPT") or "You are Deathline, a roast bot."

async def test_gemini_roast():
    """
    Test the Gemini roast API call directly.
    """
    print("=" * 70)
    print("🧪 TESTING GEMINI ROAST SYSTEM")
    print("=" * 70)
    
    # Show configuration
    print(f"\n📋 Configuration:")
    print(f"  • Gemini API Key: {'✅ SET' if GEMINI_API_KEY else '❌ NOT SET'}")
    print(f"  • Model: {GEMINI_MODEL}")
    print(f"  • Prompt: {ROAST_SYSTEM_PROMPT[:60]}...")
    
    if not GEMINI_API_KEY:
        print("\n❌ ERROR: GEMINI_API_KEY is not set in .env file!")
        print("   Go to https://aistudio.google.com/app/apikey and get a free key.")
        return
    
    # Explain what Gemini does
    print("\n" + "=" * 70)
    print("🤖 WHAT GEMINI DOES IN YOUR ROAST SYSTEM:")
    print("=" * 70)
    print("""
1. Analyzes the user's message (e.g., "ง่วงเหมือนตายแล้ว")
2. Classifies intent into 3 categories:
   - WORKING: "กำลังทำแล้ว" → Praise them with emojis 🔥💪
   - SLACKING: "ง่วง, ขี้เกียจ" → Roast them with funny Thai sarcasm
   - NEUTRAL: Just casual chat → Say nothing funny
3. Returns a JSON with:
   - intent: WORKING | SLACKING | NEUTRAL
   - response: Custom funny roast/praise in Thai

Without Gemini: Falls back to keyword matching (WORKING_KEYWORDS, SLACKING_KEYWORDS)
With Gemini: AI understands context and generates custom responses
    """)
    
    # Test API call
    print("\n" + "=" * 70)
    print("🧪 TESTING ACTUAL API CALL:")
    print("=" * 70)
    
    test_message = "ง่วงแล้ว พักแป๊บก่อน"
    task_name = "ปั่นโค้ด API"
    time_left_str = "30 minutes"
    
    system_prompt = ROAST_SYSTEM_PROMPT.format(task_name=task_name, time_left_str=time_left_str)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_prompt}\n\nUser Message: \"{test_message}\""}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    }
    
    print(f"\nTest message: '{test_message}'")
    print(f"Task: {task_name}")
    print(f"Time left: {time_left_str}")
    print(f"\nSending to: {GEMINI_MODEL}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5.0) as resp:
                print(f"\n📡 API Status: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content)
                    
                    print(f"\n✅ SUCCESS! Gemini responded:")
                    print(f"   Intent: {parsed.get('intent')}")
                    print(f"   Response: {parsed.get('response')}")
                    return True
                else:
                    data = await resp.json()
                    print(f"\n❌ ERROR {resp.status}:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Try to extract error message
                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown error")
                        print(f"\n💡 Error: {error_msg}")
                        if "API key" in error_msg.lower():
                            print("   → Your GEMINI_API_KEY might be invalid or expired")
                        elif "quota" in error_msg.lower():
                            print("   → You've hit the free tier quota limit")
                        elif "model" in error_msg.lower():
                            print(f"   → Model '{GEMINI_MODEL}' might not exist")
                    return False
    
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT: API took too long (>5s)")
        print("   → Check your internet connection or try a different model")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_roast())
    print("\n" + "=" * 70)
    if result:
        print("✅ Gemini roast system is WORKING!")
    else:
        print("❌ Gemini roast system has issues - see above")
    print("=" * 70)
