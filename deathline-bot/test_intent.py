import asyncio
from bot import LLMIntentAnalyzer

test_phrases = [
    'to lazy to do this shitt',
    'lets lseep',
    'นอนดีกว่าเว้ย',
    'ขี้เกียจ',
    'กำลังทำสไลด์',
    'เปิดคอมลุยงานแล้ว',
    'i am coding now'
]

async def run_tests():
    for p in test_phrases:
        res = await LLMIntentAnalyzer.analyze_message(p, 12345, 'Demo Task', '10 นาที')
        print(f'Test: "{p}" -> Intent: {res["intent"]} | Response: {res["response"][:40]}...')

asyncio.run(run_tests())
