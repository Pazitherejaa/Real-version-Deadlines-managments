#!/usr/bin/env python3
"""
List available Gemini models to see what's actually available.
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def list_models():
    """List available models with this API key."""
    print("=" * 70)
    print("🔍 LISTING AVAILABLE GEMINI MODELS")
    print("=" * 70)
    
    print(f"\n📋 API Key: {GEMINI_API_KEY[:20]}...")
    print(f"   Type: {'AIza... (Standard)' if GEMINI_API_KEY.startswith('AIza') else 'AQ... (Non-standard/OAuth?)' if GEMINI_API_KEY.startswith('AQ') else 'Unknown'}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    
    print(f"\nFetching from: {url[:80]}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5.0) as resp:
                print(f"\n📡 Status: {resp.status}")
                data = await resp.json()
                
                if resp.status == 200:
                    models = data.get("models", [])
                    print(f"\n✅ Found {len(models)} models:")
                    for i, model in enumerate(models[:10], 1):
                        name = model.get("name", "?").replace("models/", "")
                        display_name = model.get("displayName", "N/A")
                        print(f"   {i}. {name}")
                        print(f"      {display_name}")
                    if len(models) > 10:
                        print(f"   ... and {len(models) - 10} more")
                else:
                    print(f"\n❌ Error: {resp.status}")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
