import asyncio
import json
import os
import random
import re
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# -------------------------------------------------------------
# CONFIGURATION & ENVIRONMENT
# -------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-flash-latest"

MEMES_DIR = os.path.join(os.path.dirname(__file__), "memes")
MEMES_JSON = os.path.join(os.path.dirname(__file__), "memes.json")
os.makedirs(MEMES_DIR, exist_ok=True)

FALLBACK_MEMES = {
    "50%": [
        "https://i.imgflip.com/1g8my4.jpg",
        "https://i.imgflip.com/261o3j.jpg",
        "https://i.imgflip.com/30b1gx.jpg",
        "https://i.imgflip.com/2wifvo.jpg",
        "https://i.imgflip.com/265j.jpg",
        "https://i.imgflip.com/345v97.jpg"
    ],
    "25%": [
        "https://i.imgflip.com/1ot29m.jpg",
        "https://i.imgflip.com/28j0te.jpg",
        "https://i.imgflip.com/434f5s.jpg",
        "https://i.imgflip.com/1e7ql7.jpg",
        "https://i.imgflip.com/1h7in3.jpg",
        "https://i.imgflip.com/26am98.jpg"
    ],
    "10%": [
        "https://i.imgflip.com/1jwhww.jpg",
        "https://i.imgflip.com/1bhk.jpg",
        "https://i.imgflip.com/26am98.jpg",
        "https://i.imgflip.com/2fm6x0.jpg",
        "https://i.imgflip.com/382dtb.jpg",
        "https://i.imgflip.com/1ur9b0.jpg"
    ],
    "0%": [
        "https://i.imgflip.com/1c1uej.jpg",
        "https://i.imgflip.com/9ehk.jpg",
        "https://i.imgflip.com/392xvo.jpg",
        "https://i.imgflip.com/2ybua0.jpg",
        "https://i.imgflip.com/2cp1.jpg",
        "https://i.imgflip.com/4t0m5.jpg"
    ],
    "custom": []
}

# -------------------------------------------------------------
# DYNAMIC AI ROAST SYSTEM (VARIED SPEECH & PROACTIVE GRIND)
# -------------------------------------------------------------
class AIRoastEngine:
    SLACKER_KEYWORDS = [
        "lazy", "to lazy", "too lazy", "sleep", "lseep", "lets sleep", "lets lseep", "sleepy", 
        "tired", "shit", "shitt", "fuck", "bored", "procrastinat", "nah", "later", "give up", 
        "dont want", "cant", "quit", "gaming", "play game", "dota", "val", "valorant", "roblox", 
        "genshin", "netflix", "youtube", "relax", "resting", "afk", "idc", "nevermind", "chill",
        "ขี้เกียจ", "นอนดีกว่า", "นอนดีกว่าเว้ย", "นอนเหอะ", "นอนละ", "ไปนอน", "ขอนอน", "นอนแป๊บ",
        "ง่วง", "เหนื่อย", "ไม่ไหว", "ไม่ไหวแล้ว", "ท้อ", "ยอมแพ้", "เทงาน", "ดอง", "พักแป๊บ", 
        "พักก่อน", "ขอพัก", "พักยาว", "ไม่ทำ", "ไม่อยากทำ", "ไม่เอาละ", "ช่างมัน", "ชิลล์", 
        "เล่นเกม", "หิว", "กินข้าวก่อน", "ไถฟีด", "ดูคลิป", "ดูหนัง", "ดู youtube", "เล่นเฟซ", 
        "เล่นตต", "เล่นไอจี", "สู่ขิต", "ไม่เสร็จหรอก", "ขี้เกียจทำ", "ขี้เกียจโว้ย", "บาย", 
        "ขอบาย", "สลีป", "ไม่ทันแน่", "พักผ่อน", "เมื่อย", "ปวดหลัง", "ขอตัว", "ตี้", "ลงแรงค์"
    ]

    WORKING_KEYWORDS = [
        "working", "work", "coding", "code", "starting", "on it", "grind", "doing it", 
        "let's go", "lets go", "fixed", "commit", "push", "pr", "figma", "slide", "debug", 
        "running", "done", "typing", "build", "deploy", "testing", "grinding", "progress",
        "ทำแล้ว", "กำลังทำ", "เริ่มทำ", "เริ่มเลย", "ปั่นแป๊บ", "กำลังปั่น", "เปิดคอม", 
        "ลุย", "เปิดโค้ด", "เขียนโค้ด", "ทำสไลด์", "กำลังแก้", "ok ทำ", "จัดไป", "แก้บั๊ก",
        "ไปทำละ", "ไปทำแล้ว", "ทำต่อ", "ปั่นต่อ", "เปิด figma", "แก้โค้ด", "push code", "commit",
        "ทำเสร็จ", "แก้เสร็จ", "เทสอยู่", "กำลังเทส", "กำลังทำสไลด์", "ลุยงาน", "เริ่มลุย"
    ]

    VARIED_ROASTS = [
        "รีบไปปั่นงานได้แล้ว มัวแต่นั่งคุยเล่นในดิสคอร์ดอยู่ได้! เดดไลน์จะสู้กลับแล้วนะ ⏳💀",
        "พิมพ์แชทคล่องขนาดนี้ ถ้าเอาความเร็วนี้ไปเขียนโค้ด/อ่านหนังสือ ป่านนี้เสร็จไปสามรอบแล้วคุณพรี่! 🤡🔥",
        "คุยเก่งเหมือนงานเสร็จแล้ว! เพื่อนร่วมทีมเค้าปั่นกันหลังขดหลังแข็ง รีบไปช่วยเค้าเดี๋ยวนี้! 👀🚨",
        "พักแป๊บพ่องงง! เหลือเวลาอีกนิดเดียวจะเอาอะไรไปส่งครู/เดโม่กรรมการวะ ปิดดิสแล้วไปเปิดงานซะ! ⚰️💥",
        "เห็นแชทเด้งรัวๆ นึกว่าส่งงาน ที่แท้มานั่งเม้าท์มอย! ลุกไปทำ **{task_name}** ด่วน! 🍿🤡",
        "นอนตอนนี้ได้นอนยาวแน่! ลุกขึ้นมาแก้บั๊ก/ทำการบ้านก่อนที่เดดไลน์จะกลายเป็นความฉิบหายยกตี้! 🥊🔥",
        "บ่นเหนื่อยแต่เห็นส่องดิสทั้งวัน! งานยังไม่แตะแต่ข้ออ้างระดับซีเนียร์ ปั่นงานเดี๋ยวนี้! 🥱🦥",
        "แหมมม ข้ออ้างเยอะเหมือนฟีเจอร์ที่ยังไม่ได้เขียนเลยนะ! รีบไปปั่นให้เสร็จก่อนสู่ขิต! 💀⚡",
        "เตือนด้วยความหวังดีนะจ๊ะ! ดิสคอร์ดไม่ได้ช่วยให้งาน **{task_name}** เสร็จโว้ยยย ลุยงานดิ! 💻🔥",
        "เช็คชื่อหน่อย! ตอนนี้กำลังปั่น **{task_name}** อยู่จริงหรือเปล่า หรือแอบเปิด YouTube/เกม ดูอยู่? 🧐🍿",
        "ถามจริงนะคุณพี่! วันนี้เปิดเอกสาร/โค้ดงาน **{task_name}** ไปกี่บรรทัดแล้ว? อย่าให้รู้นะว่ายัง 0! 🚨🤡",
        "เดดไลน์กำลังคลืบคลานเข้ามาเรื่อยๆ แต่ความเร็วในการทำงานยังคงติดลบ! ลุกไปทำ **{task_name}** เดี๋ยวนี้! ⏳💀"
    ]

    VARIED_PRAISES = [
        "ปาฏิหาริย์เกิดขึ้นจริง! ในที่สุดก็ยอมเปิดคอมทำงานแล้ว ลุยให้เสร็จนะเพื่อน 🚀🔥",
        "ไฟลุกแล้วโว้ยยย! โหมดบีสต์ทำงาน ปั่นให้สุดแล้วกวาดคะแนนเต็ม/รางวัลที่ 1 ไปเลย! ⚡💻",
        "จัดไปอย่าให้แผ่ว! ร่างทองจุติแล้ว คอมมิตเดือดๆ รันเทสผ่านฉลุย ลุยต่อเลย! 🟢🔥",
        "แบบนี้แหละคนจะรวย! ปั่นให้สุดแล้วไปหยุดที่เวทีพรีเซนต์ ลุยยยย! 🏆💪",
        "สปิริตนักสู้ระดับแชมป์เปี้ยน! ลุยโค้ด/การบ้านไม่หยุดแบบนี้ ชนะชัวร์ 100%! 🚀🎉"
    ]


async def generate_ai_roast(user_message: str, author_name: str, task_name: str = "โปรเจกต์ Hackathon", user_id: int = None) -> str:
    """ฟังก์ชันส่งข้อความไปให้ AI ช่วยคิดคำแซวกวนๆ พร้อม Fallback ที่วาจาหลากหลาย
    พิจารณาคะแนนของผู้ใช้เพื่อกำหนดระดับการแซว"""
    clean_msg = user_message.strip().lower()

    # ตรวจสอบว่าเป็นคำชมเชย (Working) หรือไม่
    if any(kw in clean_msg for kw in AIRoastEngine.WORKING_KEYWORDS):
        return random.choice(AIRoastEngine.VARIED_PRAISES)

    # ดึงคะแนนผู้ใช้
    user_score = 0
    tier_name = "😐 Neutral"
    if user_id:
        user_score = UserScoreManager.get_score(user_id)
        tier_name, _ = UserScoreManager.get_tier(user_id)

    # ลองเรียก Gemini AI ถ้ามี API Key
    if GEMINI_API_KEY and GEMINI_API_KEY != "API KEYS":
        tone = "เข้มข้นและโหดสุดแสบ" if user_score < 0 else "ปานกลาง" if user_score < 10 else "เป็นกำลังใจและตลกขบขัน"
        prompt = f"""คุณคือบอท 'Deathline' ประชดประชันแบบเจาะลึกรายบุคคล (Hyper-Personalized Roast)
ผู้ใช้ชื่อ "{author_name}" มีประจำตัว {tier_name} (คะแนน: {user_score})
กำลังมีเดดไลน์ "{task_name}" แต่พิมพ์ข้อความในแชทว่า: "{user_message}"

คำสั่ง:
1. แซว/ด่าเจาะลึกชื่อ "{author_name}" และการอู้งาน/คุยเล่นแบบ{tone} สั้นๆ 1-2 ประโยค
2. ภาษาไทยสแลงเกมเมอร์/เดฟ พร้อมอีโมจิประกอบ"""
        for model in [GEMINI_MODEL, "gemini-flash-latest", "gemini-pro-latest"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.95, "maxOutputTokens": 120}
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=2.5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            if text:
                                return text
            except Exception:
                pass

    # Fallback: เลือกตามคะแนน
    if user_score < -5:
        # หากติดลบมาก → พูดหนักมาก
        templates = [
            "กรรม กรรม กรรมนำ! งานยังไม่ทำ แต่มาแชทเล่นตั้งนั้นเนี่ย! {task_name} รอหนาว! 💀",
            "ผลประวัติของคุณพูดได้แล้ว! ลุกไปทำ {task_name} เดี๋ยวนี้ก่อนยัง 0%! ⚰️",
            "เมตตาชิวเลย! ถ้ายังไม่เสร็จ บอทจะกวนไปตลอดนะคุณพรี่! ลุยงานด่วน! 🔥",
        ]
    elif user_score < 0:
        # คะแนนติดลบ → พูดเข้มข้น
        template = random.choice(AIRoastEngine.VARIED_ROASTS)
        return template.format(task_name=task_name)
    elif user_score < 10:
        # คะแนนน้อย → พูดปกติ
        template = random.choice(AIRoastEngine.VARIED_ROASTS)
        return template.format(task_name=task_name)
    else:
        # คะแนนสูง → พูดดี/ตลกเบา
        templates = [
            "เห็นแบบนี้ก็รู้ว่า {task_name} ของคุณกำลังจะเก่งขึ้นแล้ว ลุยต่อเลย! 🔥",
            "คนเก่งแบบคุณ {task_name} ก็ต้องจบสะดวก ปั่นให้สุดแล้วกวาดเข้ากระเป๋า! 🚀",
            "เห็นเด้งเเชทแบบนี้ ยังไม่ทำ {task_name} เสร็จเหรอ ยอดคนนี้มี! 💪",
        ]
    
    if user_score < -5:
        return random.choice(templates)
    template = random.choice(AIRoastEngine.VARIED_ROASTS)
    return template.format(task_name=task_name)


# -------------------------------------------------------------
# USER SCORE MANAGER (REPUTATION SYSTEM)
# -------------------------------------------------------------
SCORES_JSON = os.path.join(os.path.dirname(__file__), "user_scores.json")

class UserScoreManager:
    @staticmethod
    def _load_scores() -> dict:
        if os.path.exists(SCORES_JSON):
            try:
                with open(SCORES_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @staticmethod
    def _save_scores(data: dict):
        try:
            with open(SCORES_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def get_score(cls, user_id: int) -> int:
        scores = cls._load_scores()
        return scores.get(str(user_id), 0)

    @classmethod
    def add_score(cls, user_id: int, points: int, reason: str = ""):
        scores = cls._load_scores()
        user_key = str(user_id)
        current = scores.get(user_key, 0)
        scores[user_key] = current + points
        cls._save_scores(scores)
        return scores[user_key]

    @classmethod
    def get_leaderboard(cls, limit: int = 10) -> List[Tuple[int, int]]:
        scores = cls._load_scores()
        sorted_scores = sorted(
            [(int(uid), score) for uid, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_scores[:limit]

    @classmethod
    def get_tier(cls, user_id: int) -> Tuple[str, str]:
        """ส่งคืน (tier_name, emoji) ตามคะแนน"""
        score = cls.get_score(user_id)
        if score >= 50:
            return "🏆 Legendary Grinder", "🏆"
        elif score >= 30:
            return "🥇 Pro Worker", "🥇"
        elif score >= 15:
            return "🔥 Solid Performer", "🔥"
        elif score >= 5:
            return "✅ Decent Worker", "✅"
        elif score >= 0:
            return "😐 Neutral", "😐"
        elif score >= -10:
            return "⚠️ Slacker", "⚠️"
        else:
            return "💀 Notorious Slacker", "💀"


# -------------------------------------------------------------
# MEME MANAGER (ADD, LIST & DELETE)
# -------------------------------------------------------------
class MemeManager:
    @staticmethod
    def _load_json() -> dict:
        if os.path.exists(MEMES_JSON):
            try:
                with open(MEMES_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return FALLBACK_MEMES.copy()

    @staticmethod
    def _save_json(data: dict):
        try:
            with open(MEMES_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def get_meme(cls, milestone: str) -> Tuple[Optional[str], Optional[discord.File]]:
        if os.path.exists(MEMES_DIR):
            valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")
            local_files = [
                os.path.join(MEMES_DIR, f)
                for f in os.listdir(MEMES_DIR)
                if f.lower().endswith(valid_exts)
            ]
            if local_files:
                chosen_path = random.choice(local_files)
                filename = os.path.basename(chosen_path)
                return f"attachment://{filename}", discord.File(chosen_path, filename=filename)

        memes_db = cls._load_json()
        pool = memes_db.get(milestone, []) + memes_db.get("custom", [])
        if not pool:
            pool = FALLBACK_MEMES.get(milestone, [])

        if pool:
            return random.choice(pool), None
        return None, None

    @classmethod
    def add_custom_meme(cls, url: str, category: str = "custom") -> bool:
        data = cls._load_json()
        if category not in data:
            data[category] = []
        if url not in data[category]:
            data[category].append(url)
            cls._save_json(data)
            return True
        return False

    @classmethod
    def delete_meme(cls, query: str) -> Tuple[bool, str]:
        query = query.strip()
        data = cls._load_json()
        deleted = False

        # 1. ค้นหาและลบใน JSON URLs
        for cat in list(data.keys()):
            if isinstance(data[cat], list):
                original_len = len(data[cat])
                data[cat] = [u for u in data[cat] if query.lower() not in u.lower()]
                if len(data[cat]) < original_len:
                    deleted = True

        if deleted:
            cls._save_json(data)
            return True, f"🗑️ ลบลิงก์รูป Meme ที่ตรงกับ `{query}` ออกจากคลังเรียบร้อยแล้ว!"

        # 2. ค้นหาและลบในโฟลเดอร์ memes ท้องถิ่น
        if os.path.exists(MEMES_DIR):
            for fname in os.listdir(MEMES_DIR):
                if query.lower() in fname.lower():
                    try:
                        os.remove(os.path.join(MEMES_DIR, fname))
                        return True, f"🗑️ ลบไฟล์รูปภาพ `{fname}` ออกจากโฟลเดอร์มีมเรียบร้อยแล้ว!"
                    except Exception as e:
                        return False, f"❌ เกิดข้อผิดพลาดในการลบไฟล์: {e}"

        return False, f"❌ ไม่พบรูปภาพหรือ URL ที่ตรงกับคำค้นหา `{query}`"

    @classmethod
    def get_stats(cls) -> dict:
        data = cls._load_json()
        local_count = 0
        if os.path.exists(MEMES_DIR):
            valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")
            local_count = len([f for f in os.listdir(MEMES_DIR) if f.lower().endswith(valid_exts)])
        counts = {k: len(v) for k, v in data.items()}
        counts["local_folder"] = local_count
        return counts


# -------------------------------------------------------------
# BOT INITIALIZATION
# -------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True

class DeathlineBot(commands.Bot):
    def __init__(self, intents: Optional[discord.Intents] = None):
        bot_intents = intents if intents is not None else discord.Intents.default()
        super().__init__(command_prefix=["!", "."], intents=bot_intents)
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.active_tasks: Dict[str, dict] = {}
        self.active_focus: Dict[int, dict] = {}
        self.user_roast_cooldown: Dict[int, float] = {}
        self.slacker_strikes: Dict[int, int] = {}

    async def setup_hook(self):
        self.scheduler.start()
        print("[SCHEDULER] APScheduler Started Successfully!")
        try:
            synced = await self.tree.sync()
            print(f"[SYNC] Synced {len(synced)} Global Slash Commands (Single Copy)!")
        except Exception as e:
            print(f"[SYNC ERROR]: {e}")

    async def on_ready(self):
        print("=" * 60)
        print(f"💀 Deathline Bot is ONLINE! Logged in as: {self.user}")
        print(f"⏰ Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # เคลียร์ Guild-specific commands ที่อาจค้างอยู่เพื่อแก้ปัญหาคำสั่งซ้ำเบิ้ล 2 ชุด
        for guild in self.guilds:
            try:
                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
            except Exception:
                pass

        print("[CLEANUP] เคลียร์คำสั่งซ้ำซ้อนเรียบร้อยแล้ว มีเพียง 1 ชุดเท่านั้น!")
        print("=" * 60)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="💀 AI Intent Roaster | /deathline_help"
            )
        )
        
        # เปิด Terminal Message Mode
        asyncio.create_task(terminal_message_handler())

bot = DeathlineBot()


# -------------------------------------------------------------
# AUTOMATED PROGRESSIVE MILESTONE ROAST SYSTEM
# -------------------------------------------------------------
MILESTONE_THEMES = {
    "50%": {
        "badge": "🟡 [HALF-TIME | 50% REMAINING]",
        "color": discord.Color.from_rgb(241, 196, 15),
        "intensity": "😏 Sarcasm Level: Mild",
        "roast": "😏 ผ่านไปครึ่งทางแล้วจ้า! สภาพตอนนี้น่าจะยังนั่งไถฟีดหรือเพิ่งเปิดไฟล์โปรเจกต์เปิดแล้วปิดแบบนั้นใช่ไหม? 🤷 เหลือเวลาครึ่งหนึ่งแล้ว! ลุยหนักๆ ไปเถิด! ปั่นไม่หยุด ล้วงไม่ลืม ทำให้เสร็จต่อนะ! 💪🔥"
    },
    "25%": {
        "badge": "🟠 [SWEAT PHASE | 25% REMAINING]",
        "color": discord.Color.from_rgb(230, 126, 34),
        "intensity": "😰 Sarcasm Level: High Panic",
        "roast": "😰 เหลือ 25% สุดท้ายแล้ว! เริ่มได้กลิ่นความฉิบหายโชยมาตามลมหรือยัง? 🌪️ ปั่นมือเป็นระวิงได้แล้ว! โลดแล่นกันซิ! ความดันเด้ง ความเร็วลาดเหวอ ทำงานเต็มพิกัดนะครับ! 🚀💨 สุดท้ายแล้ว ต้องรักษาสติให้ติดต่อกัน!"
    },
    "10%": {
        "badge": "🔴 [PANIC MODE | 10% REMAINING]",
        "color": discord.Color.from_rgb(231, 76, 60),
        "intensity": "🔥 Sarcasm Level: Maximum Brutal",
        "roast": "🚨 10% โค้งสุดท้าย! สภาพตอนนี้คือเอานิ้วโป้งเท้าพิมพ์โค้ด/ตัวอักษรก็ต้องยอมแล้ว! 🦶💻 วิกฤตระดับ 10 ริกเตอร์! เจ็บตัว เหนื่อย อ่อนไหว ทั้งหมดนี้ยอมรับได้แล้ว ถ้าจะเสร็จ! 😫 ลุยทำให้สุดฝ่าย ตายแต่ให้เสร็จ! 💀⚡ อยากให้สำเร็จแตกว่า อยากให้สาร!"
    },
    "75%": {
        "badge": "🟡 [CHECK-IN | 75% REMAINING]",
        "color": discord.Color.from_rgb(241, 196, 15),
        "intensity": "🤔 Sarcasm Level: Curious Interrogation",
        "roast": "🤔 ปี่เอ้ยยยย! เหลือ 75% เวลาอยู่ ลองตรวจสอบตัวเองหน่อย 🧐 กำลังทำงาน **{task_name}** อยู่จริงๆ ป่าว? 📚💻 หรือแอบเปิดเฟซบุ๊ก/ยูทูป/เกมอยู่ไหม? 🎮 ส่อบตัวหน่อย! 👀 เหลือเวลาเยอะๆ อยู่ แล้วยังไม่เริ่ม? ลุยงานเดี๋ยวนี้ซิ! ⏰💪"
    },
    "0%": {
        "badge": "💀🚨 [DEATHLINE HIT | TIME OVER]",
        "color": discord.Color.from_rgb(153, 45, 34),
        "intensity": "⚰️ Status: R.I.P.",
        "roast": "⚰️🚨 DEATHLINE HIT! สู่ขิตอย่างเป็นทางการแล้ว! เวลาหมด ความพยายามไม่ทันตามเวลา ขอแสดงความเสียใจและสมควรตัวจริงกับทีมของคุณล่วงหน้าครับ! 💀 การต่อสู้สิ้นสุด ศึกจบลง หมดแรง หมดเวลา หมดทุกอย่าง! 🪦 เตรียมตัวสำหรับรอบต่อไป ถ้าหากมีอีก!"
    }
}

async def auto_dispatch_roast(task_id: str, milestone: str):
    if task_id not in bot.active_tasks:
        return

    task_info = bot.active_tasks[task_id]
    channel_id = task_info.get("channel_id")
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    user_ids = task_info.get("user_ids", [task_info.get("creator_id")])
    task_name = task_info["task_name"]
    theme = MILESTONE_THEMES.get(milestone, MILESTONE_THEMES["0%"])
    meme_url_or_attachment, file_to_upload = MemeManager.get_meme(milestone)

    mentions_str = " ".join([f"<@{uid}>" for uid in user_ids])

    embed = discord.Embed(
        title=f"{theme['badge']} {task_name}",
        description=f"📢 {mentions_str}\n\n> **{theme['roast']}**",
        color=theme["color"],
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="📋 ชื่องาน", value=f"`{task_name}`", inline=True)
    embed.add_field(name="⚡ ระดับความลน", value=f"`{theme['intensity']}`", inline=True)
    embed.add_field(name="🆔 Task ID", value=f"`{task_id}`", inline=True)
    embed.add_field(name="👥 ทีมผู้รับผิดชอบร่วมกัน", value=mentions_str, inline=False)

    if meme_url_or_attachment:
        embed.set_image(url=meme_url_or_attachment)

    embed.set_footer(text=f"Deathline Automated AI Roast • Milestone {milestone}")

    send_kwargs = {
        "content": f"# 🚨 **DEATHLINE MILESTONE ALERT!**\n## 📢 {mentions_str} งาน: `{task_name}` ({milestone})\n>>> 💀 **{theme['roast']}**",
        "embed": embed
    }
    if file_to_upload:
        send_kwargs["file"] = file_to_upload

    try:
        await channel.send(**send_kwargs)
    except Exception as e:
        print(f"[AUTO ROAST ERROR]: {e}")

    # ถ้าถึงเวลาสิ้นสุด (0%) ให้เพิ่มความเสียหาย -3 score
    if milestone == "0%":
        for uid in user_ids:
            new_score = UserScoreManager.add_score(uid, -3, "missed_deadline")
            tier_name, tier_emoji = UserScoreManager.get_tier(uid)
        
        # ส่งข้อความแจ้งว่าถูกลบ Score
        penalty_embed = discord.Embed(
            title="💀 โศกนาฏกรรม! หมดเวลาโดยไม่เสร็จ!",
            description=f"{mentions_str} ถูกลบ **-3 Score** เพราะไม่ทำงาน **{task_name}** เสร็จทันเวลา 😭",
            color=discord.Color.from_rgb(231, 76, 60)
        )
        for uid in user_ids:
            score = UserScoreManager.get_score(uid)
            tier_name, _ = UserScoreManager.get_tier(uid)
            penalty_embed.add_field(name=f"<@{uid}>", value=f"Score: {score} ({tier_name})", inline=True)
        
        penalty_embed.set_footer(text="⏰ เดดไลน์มิสชิบหาย! เตรียมตัวสำหรับรอบถัดไป!")
        
        try:
            await channel.send(embed=penalty_embed)
        except Exception:
            pass
        
        bot.active_tasks.pop(task_id, None)


async def dispatch_focus_alert(user_id: int, channel_id: int, session_name: str, minutes: int):
    channel = bot.get_channel(channel_id)
    if channel:
        embed = discord.Embed(
            title="🎉☕ [FOCUS COMPLETE] ครบเวลาโฟกัสแล้ว!",
            description=f"<@{user_id}> ยอดเยี่ยมมาก! คุณโฟกัสกับ **{session_name}** ครบ **{minutes} นาที** แล้ว",
            color=discord.Color.from_rgb(46, 204, 113),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="💡 ข้อแนะนำ", value="พักสายตา ลุกขึ้นยืดเส้นยืดสาย ดื่มน้ำสักแก้วก่อนเริ่มรอบถัดไปนะครับ!", inline=False)
        embed.set_footer(text="Deathline Co-working Pomodoro")
        try:
            await channel.send(content=f"# 🔔 <@{user_id}> หมดเวลาโฟกัสแล้วครับ!\n### ☕ ได้เวลาพักสายตายืดเส้นยืดสายสักครู่", embed=embed)
        except Exception as e:
            print(f"[FOCUS ERROR]: {e}")

    bot.active_focus.pop(user_id, None)


# -------------------------------------------------------------
# EVENT LISTENER: REAL-TIME AUTONOMOUS DETECTION & PROACTIVE ROAST
# -------------------------------------------------------------
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # ให้คำสั่ง prefix (เช่น !sync, !roast) ทำงานได้ปกติ
    await bot.process_commands(message)

    content = message.content or ""
    clean_content = re.sub(r"<@!?[0-9]+>", "", content).strip()
    is_mentioned = bot.user.mentioned_in(message) if bot.user else False

    user_id = message.author.id
    current_time = time.time()

    # ตรวจสอบว่าผู้ใช้มีเดดไลน์ที่ยังไม่เสร็จอยู่หรือไม่
    user_tasks = [info for tid, info in bot.active_tasks.items() if user_id in info.get("user_ids", []) or info.get("creator_id") == user_id]
    task_name = user_tasks[0]["task_name"] if user_tasks else "โปรเจกต์ / การบ้าน"

    # ตรวจสอบคำอู้งาน / คำทำงาน
    is_slacking = any(kw in clean_content.lower() for kw in AIRoastEngine.SLACKER_KEYWORDS)
    is_working = any(kw in clean_content.lower() for kw in AIRoastEngine.WORKING_KEYWORDS)

    # บันทึกคะแนนคนอู้งานสำหรับ Leaderboard
    if is_slacking:
        bot.slacker_strikes[user_id] = bot.slacker_strikes.get(user_id, 0) + 1

    # ตอบกลับอัตโนมัติเมื่อ:
    # 1. มีคนแท็กหาบอท (@บอท)
    # 2. ตรวจพบคำอู้งาน / คำทำงาน
    # 3. ผู้ใช้มีเดดไลน์ค้างอยู่และพิมพ์ในแชท (Targeted & Random Check-in 40%)
    # 4. หรือสุ่มตอบกลับ 30% เมื่อมีคนคุยเล่นทั่วไปในห้องแชท
    has_active_task = len(user_tasks) > 0
    should_respond = (
        is_mentioned 
        or is_slacking 
        or is_working 
        or (has_active_task and random.random() < 0.40 and len(clean_content) > 0)
        or (random.random() < 0.30 and len(clean_content) > 1)
    )

    if should_respond and (clean_content or is_mentioned):
        # แปะ Reaction กวนๆ หรือไฟลุกตามสถานการณ์
        try:
            if is_working:
                for r in ["🟢", "🔥", "🚀", "💻"][:2]:
                    await message.add_reaction(r)
            elif is_slacking:
                for r in ["🥱", "🦥", "🤡", "🚨", "⚰️"][:2]:
                    await message.add_reaction(r)
            else:
                for r in ["👀", "💀", "🤡", "⏳"][:1]:
                    await message.add_reaction(r)
        except Exception:
            pass

        # Cooldown เล็กน้อย 2.5 วินาทีเพื่อความลื่นไหล
        last_roast = bot.user_roast_cooldown.get(user_id, 0)
        if current_time - last_roast > 2.5:
            bot.user_roast_cooldown[user_id] = current_time
            try:
                async with message.channel.typing():
                    eval_text = clean_content if clean_content else "ขี้เกียจ"
                    roast_text = await generate_ai_roast(eval_text, message.author.display_name, task_name, user_id)
                    
                    if is_working:
                        formatted_response = f"# 🔥 <@{user_id}> โหมดลุยงาน!\n### 🚀 กำลังปั่น: **{task_name}**\n>>> 🟢 **{roast_text}**"
                    else:
                        formatted_response = f"# 🚨 <@{user_id}>\n### 📚 สถานะงาน/การบ้าน: **{task_name}**\n>>> 💀 **{roast_text}**"
                    
                    await message.reply(formatted_response)
            except Exception as e:
                print(f"[REPLY ERROR]: {e}")


# -------------------------------------------------------------
# SLASH COMMANDS: TEAM DEADLINES, MEME DELETE & SCOREBOARD
# -------------------------------------------------------------
def setup_deadline_jobs(task_id: str, task_name: str, deadline_minutes: int, channel_id: int, creator_id: int, user_ids: List[int]):
    now = datetime.now(timezone.utc)
    total_seconds = deadline_minutes * 60
    target_time = now + timedelta(seconds=total_seconds)

    scheduled_job_ids = []
    for label, ratio in [("75%", 0.25), ("50%", 0.50), ("25%", 0.75), ("10%", 0.90), ("0%", 1.00)]:
        delay = total_seconds * ratio
        if delay >= 5 or label == "0%":
            run_time = now + timedelta(seconds=delay)
            job_id = f"roast_{task_id}_{label}"
            bot.scheduler.add_job(
                auto_dispatch_roast, trigger="date", run_date=run_time, args=[task_id, label], id=job_id, replace_existing=True
            )
            scheduled_job_ids.append(job_id)

    bot.active_tasks[task_id] = {
        "creator_id": creator_id,
        "user_ids": user_ids,
        "channel_id": channel_id,
        "task_name": task_name,
        "target_time": target_time,
        "job_ids": scheduled_job_ids
    }
    return target_time


@bot.tree.command(name="deathline_add", description="เพิ่มเดดไลน์งานใหม่")
@app_commands.describe(
    task_name="ชื่องาน",
    deadline_days="วัน (0-365)",
    deadline_hours="ชั่วโมง (0-23)",
    deadline_minutes="นาที (0-59)",
    teammate1="เพื่อนร่วมทีม 1",
    teammate2="เพื่อนร่วมทีม 2"
)
async def deathline_add(
    interaction: discord.Interaction, 
    task_name: str, 
    deadline_days: int = 0,
    deadline_hours: int = 0,
    deadline_minutes: int = 0,
    teammate1: Optional[discord.Member] = None,
    teammate2: Optional[discord.Member] = None
):
    total_minutes = (deadline_days * 24 * 60) + (deadline_hours * 60) + deadline_minutes
    
    if total_minutes <= 0:
        await interaction.response.send_message("❌ กรุณาระบุจำนวนวันหรือนาทีที่มากกว่า 0 ครับ (เช่น deadline_days=1 หรือ deadline_minutes=60)", ephemeral=True)
        return

    task_id = str(uuid.uuid4())[:6]
    user_ids = [interaction.user.id]
    if teammate1 and teammate1.id not in user_ids:
        user_ids.append(teammate1.id)
    if teammate2 and teammate2.id not in user_ids:
        user_ids.append(teammate2.id)

    target_time = setup_deadline_jobs(
        task_id=task_id,
        task_name=task_name,
        deadline_minutes=total_minutes,
        channel_id=interaction.channel_id,
        creator_id=interaction.user.id,
        user_ids=user_ids
    )
    unix_timestamp = int(target_time.timestamp())
    mentions_str = " ".join([f"<@{uid}>" for uid in user_ids])

    embed = discord.Embed(
        title="💀 ตั้งเดดไลน์และระบบ AI Roast อัตโนมัติแล้ว!",
        description=f"บอทจะคอยจับตาดูคุณ และยิงคำแซว (Roast) + มีมประจานอัตโนมัติเมื่อถึง 50%, 25%, 10% และ 0%!",
        color=discord.Color.from_rgb(230, 126, 34),
        timestamp=target_time
    )
    embed.add_field(name="📋 ชื่องาน", value=f"**{task_name}**", inline=False)
    embed.add_field(name="⏳ กำหนดส่ง", value=f"<t:{unix_timestamp}:F>\n(<t:{unix_timestamp}:R>)", inline=True)
    embed.add_field(name="🆔 Task ID", value=f"`{task_id}`", inline=True)
    embed.add_field(name="👤 ผู้สร้างเดดไลน์ (Creator)", value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name="👥 ผู้รับผิดชอบทั้งหมด", value=mentions_str, inline=False)
    embed.add_field(name="🔥 AI Roast", value="75% ➔ 50% ➔ 25% ➔ 10% ➔ 0%", inline=False)
    deadline_text = f"**{deadline_days}** วัน " if deadline_days else ""
    deadline_text += f"**{deadline_hours}** ชั่วโมง " if deadline_hours else ""
    deadline_text += f"**{deadline_minutes}** นาที" if deadline_minutes else ""
    if deadline_text.strip():
        embed.add_field(name="📅 เวลา", value=deadline_text, inline=False)
    embed.set_footer(text="หากทำเสร็จก่อนใช้คำสั่ง /deathline_done [task_id] เพื่อรอดพ้นจากการโดนแซว!")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="team_deadline", description="เดดไลน์ทีม")
@app_commands.describe(
    task_name="ชื่องาน",
    member1="สมาชิก 1",
    deadline_days="วัน",
    deadline_hours="ชั่วโมง",
    deadline_minutes="นาที",
    member2="สมาชิก 2",
    member3="สมาชิก 3",
    member4="สมาชิก 4"
)
async def team_deadline(
    interaction: discord.Interaction,
    task_name: str,
    member1: discord.Member,
    deadline_days: int = 0,
    deadline_hours: int = 0,
    deadline_minutes: int = 0,
    member2: Optional[discord.Member] = None,
    member3: Optional[discord.Member] = None,
    member4: Optional[discord.Member] = None
):
    total_minutes = (deadline_days * 24 * 60) + (deadline_hours * 60) + deadline_minutes
    if total_minutes <= 0:
        await interaction.response.send_message("❌ ต้องระบุเวลา", ephemeral=True)
        return

    task_id = str(uuid.uuid4())[:6]
    user_ids = [interaction.user.id]
    for m in [member1, member2, member3, member4]:
        if m and m.id not in user_ids:
            user_ids.append(m.id)

    target_time = setup_deadline_jobs(
        task_id=task_id,
        task_name=task_name,
        deadline_minutes=total_minutes,
        channel_id=interaction.channel_id,
        creator_id=interaction.user.id,
        user_ids=user_ids
    )
    unix_timestamp = int(target_time.timestamp())
    mentions_str = " ".join([f"<@{uid}>" for uid in user_ids])

    embed = discord.Embed(
        title="👥💀 ตั้งเดดไลน์ระดับทีม (Shared Team Pressure)!",
        description=f"เพิ่มงานสำหรับทีมเรียบร้อย! ทุกคนจะได้รับแรงกดดันและคำแซวร่วมกันอย่างเท่าเทียม!",
        color=discord.Color.from_rgb(231, 76, 60),
        timestamp=target_time
    )
    embed.add_field(name="📋 ชื่องานทีม", value=f"**{task_name}**", inline=False)
    embed.add_field(name="⏳ กำหนดส่ง", value=f"<t:{unix_timestamp}:F>\n(<t:{unix_timestamp}:R>)", inline=True)
    embed.add_field(name="🆔 Task ID", value=f"`{task_id}`", inline=True)
    embed.add_field(name="👤 ผู้สร้างงาน (Creator)", value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name="👥 ทีม", value=mentions_str, inline=False)
    deadline_text = f"**{deadline_days}** วัน " if deadline_days else ""
    deadline_text += f"**{deadline_hours}** ชั่วโมง " if deadline_hours else ""
    deadline_text += f"**{deadline_minutes}** นาที" if deadline_minutes else ""
    if deadline_text.strip():
        embed.add_field(name="📅 เวลา", value=deadline_text, inline=False)
    embed.set_footer(text="หากทำเสร็จก่อนใช้คำสั่ง /deathline_done [task_id] เพื่อรอดตายยกทีม!")

    await interaction.response.send_message(content=f"📢 {mentions_str} คุณได้รับมอบหมายงานทีมใหม่!", embed=embed)


@bot.tree.command(name="deathline_list", description="ดูรายการเดดไลน์ทั้งหมดที่กำลังนับถอยหลังอยู่")
async def deathline_list(interaction: discord.Interaction):
    if not bot.active_tasks:
        embed = discord.Embed(
            title="✨ ไม่มีเดดไลน์ที่ค้างอยู่",
            description="ตอนนี้ไม่มีงานที่กำลังนับถอยหลัง สบายใจได้ หรือใช้ `/deathline_add` หรือ `/team_deadline` เพื่อเพิ่มงานใหม่",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="📋 รายการเดดไลน์ที่กำลังจับเวลา (Active Deadlines)",
        description=f"มีงานที่กำลังนับถอยหลังทั้งหมด **{len(bot.active_tasks)}** งาน",
        color=discord.Color.from_rgb(241, 196, 15),
        timestamp=datetime.now(timezone.utc)
    )

    for tid, info in bot.active_tasks.items():
        unix_time = int(info["target_time"].timestamp())
        members = " ".join([f"<@{uid}>" for uid in info.get("user_ids", [info.get("creator_id")])])
        embed.add_field(
            name=f"🆔 `{tid}` : {info['task_name']}",
            value=f"👤 ผู้สร้าง: <@{info.get('creator_id')}>\n👥 ผู้รับผิดชอบ: {members}\n📺 ห้อง: <#{info['channel_id']}>\n⏰ ครบกำหนด: <t:{unix_time}:R> (<t:{unix_time}:T>)",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="deathline_done", description="เคลียร์งานที่เสร็จแล้วก่อนเวลา เพื่อยกเลิก AI Roast ทั้งหมด และได้รับ Score +5!")
@app_commands.describe(task_id="รหัส Task ID 6 หลัก (ดูได้จาก /deathline_list)")
async def deathline_done(interaction: discord.Interaction, task_id: str):
    task_id = task_id.strip()
    if task_id not in bot.active_tasks:
        await interaction.response.send_message(f"❌ ไม่พบ Task ID `{task_id}` ในระบบ หรืออาจหมดเวลาไปแล้ว", ephemeral=True)
        return

    info = bot.active_tasks[task_id]
    for jid in info.get("job_ids", []):
        try:
            bot.scheduler.remove_job(jid)
        except Exception:
            pass

    task_name = info["task_name"]
    user_ids = info.get("user_ids", [interaction.user.id])
    mentions_str = " ".join([f"<@{uid}>" for uid in user_ids])
    bot.active_tasks.pop(task_id, None)

    for uid in user_ids:
        bot.user_roast_cooldown[uid] = 0
        # เพิ่มคะแนน +5 สำหรับผู้ที่ทำเสร็จก่อนเวลา
        new_score = UserScoreManager.add_score(uid, 5, "completed_task")

    embed = discord.Embed(
        title="🎉 ปิดงานสำเร็จ (Task Completed)!",
        description=f"ยินดีด้วยครับ! {mentions_str} ทำงาน **{task_name}** เสร็จก่อนเวลา!\nบอทยกเลิกคิวส่ง AI Roast ประจานทั้งหมดให้แล้ว รอดตายยกทีม! 🛡️",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="🆔 Task ID", value=f"`{task_id}`", inline=True)
    
    # แสดงคะแนนที่ได้รับ
    score_field = "\n".join([f"<@{uid}> → +5 pts (ทั้งหมด: {UserScoreManager.get_score(uid)})" for uid in user_ids])
    embed.add_field(name="🏆 Score Earned", value=score_field, inline=False)
    
    embed.set_footer(text="Deathline • ปั่นงานเสร็จทันเวลา ยอดเยี่ยมมาก!")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="meme_add", description="เพิ่มลิงก์รูป Meme ของคุณเข้าสู่คลังของบอท")
@app_commands.describe(
    url="ลิงก์รูปภาพมีม (เช่น https://example.com/meme.jpg หรือ gif)",
    category="หมวดหมู่ความลนของมีม"
)
@app_commands.choices(category=[
    app_commands.Choice(name="50% Remaining (เริ่มเตือน)", value="50%"),
    app_commands.Choice(name="25% Remaining (เริ่มลน)", value="25%"),
    app_commands.Choice(name="10% Remaining (สปีดสุดขีด)", value="10%"),
    app_commands.Choice(name="0% Remaining (หมดเวลา/สู่ขิต)", value="0%"),
    app_commands.Choice(name="Custom / General (ทั่วไป)", value="custom")
])
async def meme_add(interaction: discord.Interaction, url: str, category: app_commands.Choice[str]):
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await interaction.response.send_message("❌ กรุณาระบุ URL ของรูปภาพที่ถูกต้อง (ขึ้นต้นด้วย http:// หรือ https://)", ephemeral=True)
        return

    success = MemeManager.add_custom_meme(url, category.value)
    if success:
        embed = discord.Embed(
            title="✅ เพิ่มรูป Meme เข้าสู่คลังเรียบร้อย!",
            description=f"รูปภาพถูกบันทึกในหมวดหมู่ **{category.name}** แล้ว",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("ℹ️ มีมนี้มีอยู่ในระบบแล้วครับ", ephemeral=True)


@bot.tree.command(name="meme_delete", description="ลบรูป Meme หรือ URL ออกจากคลัง")
@app_commands.describe(query="URL หรือชื่อไฟล์รูปภาพที่ต้องการลบ")
async def meme_delete(interaction: discord.Interaction, query: str):
    success, msg = MemeManager.delete_meme(query)
    if success:
        await interaction.response.send_message(f"✅ {msg}")
    else:
        await interaction.response.send_message(f"❌ {msg}", ephemeral=True)


@bot.tree.command(name="meme_list", description="ดูจำนวนมีมในคลังและหมวดหมู่ต่างๆ")
async def meme_list(interaction: discord.Interaction):
    stats = MemeManager.get_stats()
    embed = discord.Embed(
        title="🎭 คลังมีมเตือนเดดไลน์ (Meme Repository)",
        description="สถิติภาพมีมทั้งหมดที่พร้อมสุ่มส่งในแต่ละช่วงเวลา:",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    embed.add_field(name="📂 Local /memes folder", value=f"`{stats.get('local_folder', 0)}` ไฟล์", inline=True)
    embed.add_field(name="🟡 50% Milestone", value=f"`{stats.get('50%', 0)}` รูป", inline=True)
    embed.add_field(name="🟠 25% Milestone", value=f"`{stats.get('25%', 0)}` รูป", inline=True)
    embed.add_field(name="🔴 10% Milestone", value=f"`{stats.get('10%', 0)}` รูป", inline=True)
    embed.add_field(name="💀 0% Milestone", value=f"`{stats.get('0%', 0)}` รูป", inline=True)
    embed.add_field(name="🎨 Custom Memes", value=f"`{stats.get('custom', 0)}` รูป", inline=True)
    embed.set_footer(text="ใช้คำสั่ง /meme_add เพื่อเพิ่ม หรือ /meme_delete เพื่อลบมีม")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="scoreboard", description="ดูลีดเดอร์บอร์ดรวม Hall of Fame + Slacker Leaderboard")
async def scoreboard(interaction: discord.Interaction):
    """แสดงลีดเดอร์บอร์ดคะแนนรวม Hall of Fame (Top) + Slacker (Bottom)"""
    leaderboard = UserScoreManager.get_leaderboard(limit=100)
    
    if not leaderboard:
        await interaction.response.send_message("📊 ยังไม่มีข้อมูลคะแนนในระบบ ให้ทำงานและเสร็จก่อนเวลาสักงานก่อน!", ephemeral=True)
        return

    # แยก Top (Hall of Fame) และ Bottom (Slacker)
    hall_of_fame = [item for item in leaderboard if item[1] >= 5][:10]
    slacker_list = [item for item in leaderboard if item[1] < 0][:10]

    embed = discord.Embed(
        title="🏆💀 ลีดเดอร์บอร์ดรวม: Hall of Fame + Slacker",
        description="🟩 ผู้ที่ทำงานเสร็จเร็วได้ Score +5 💚 | 🟥 ผู้ที่ไม่ทำเสร็จถูกลด -3 💔",
        color=discord.Color.from_rgb(52, 152, 219),
        timestamp=datetime.now(timezone.utc)
    )

    # ===== HALL OF FAME (TOP PERFORMERS) =====
    if hall_of_fame:
        fame_text = ""
        for rank, (uid, score) in enumerate(hall_of_fame, start=1):
            tier_name, tier_emoji = UserScoreManager.get_tier(uid)
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "⭐"
            
            # ทำแถบคะแนน
            score_bar = "🟩 " * min(10, score // 10)
            
            fame_text += f"{medal} `#{rank}` • {tier_emoji} <@{uid}> → **{score}** pts {score_bar}\n"
        
        embed.add_field(
            name="🏆 HALL OF FAME (Top Performers)",
            value=fame_text.strip(),
            inline=False
        )
    
    # ===== SLACKER LEADERBOARD (WORST PERFORMERS) =====
    if slacker_list:
        slacker_text = ""
        for rank, (uid, score) in enumerate(slacker_list, start=1):
            tier_name, tier_emoji = UserScoreManager.get_tier(uid)
            medal = "💀" if rank == 1 else "👻" if rank == 2 else "🔥" if rank == 3 else "⚠️"
            
            # ทำแถบคะแนน (ติดลบ)
            score_bar = "🟥 " * (abs(score) // 5)
            
            slacker_text += f"{medal} `#{rank}` • {tier_emoji} <@{uid}> → **{score}** pts {score_bar}\n"
        
        embed.add_field(
            name="💀 SLACKER LEADERBOARD (Worst Performers)",
            value=slacker_text.strip(),
            inline=False
        )
    
    # ===== STATISTICS =====
    total_users = len(leaderboard)
    positive_scores = len([item for item in leaderboard if item[1] > 0])
    negative_scores = len([item for item in leaderboard if item[1] < 0])
    
    stats_text = f"📊 ทั้งหมด: **{total_users}** คน | 🟩 Positive: **{positive_scores}** | 🟥 Negative: **{negative_scores}**"
    embed.add_field(name="📈 สถิติ", value=stats_text, inline=False)

    embed.set_footer(text="Deathline Score System • ลุยงานให้เสร็จเพื่อปีนขึ้น Hall of Fame! 🚀")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="my_score", description="ดูคะแนนและเทียร์ของคุณเอง")
async def my_score(interaction: discord.Interaction):
    """แสดงคะแนนและเทียร์ส่วนตัวของผู้ใช้"""
    uid = interaction.user.id
    score = UserScoreManager.get_score(uid)
    tier_name, tier_emoji = UserScoreManager.get_tier(uid)
    
    embed = discord.Embed(
        title=f"📊 สถิติคะแนนของ {interaction.user.display_name}",
        color=discord.Color.from_rgb(52, 152, 219)
    )
    
    embed.add_field(name=f"{tier_emoji} เทียร์ของคุณ", value=tier_name, inline=True)
    embed.add_field(name="💯 คะแนนรวม", value=f"`{score}` pts", inline=True)
    
    # ทำแถบคะแนน
    if score >= 50:
        score_bar = "🟩" * min(10, score // 10)
    elif score >= 10:
        score_bar = "🟩" * (score // 10) + "🟨"
    elif score >= 0:
        score_bar = "🟨" * (score // 5)
    elif score >= -10:
        score_bar = "🟥" * (abs(score) // 5)
    else:
        score_bar = "⬛" * min(10, abs(score) // 10)
    
    embed.add_field(name="📈 กราฟคะแนน", value=score_bar if score_bar else "😐", inline=False)
    
    # ข้อเสนอแนะ
    if score < -10:
        advice = "💀 คุณกำลังอยู่ในสถานการณ์ที่ร้ายแรง! รีบทำงานให้เสร็จและเพิ่มคะแนน!"
    elif score < 0:
        advice = "⚠️ คะแนนติดลบ ลุยงานให้เสร็จเพื่อเพิ่มคะแนนกันเถอะ!"
    elif score < 5:
        advice = "😐 คะแนนยังน้อย ลุยงานให้เสร็จเพื่อเพิ่มสถานะ!"
    elif score < 15:
        advice = "✅ ดีเลยค่อนข้างสม่ำเสมอ ให้มีความพยายามเพิ่มขึ้นหน่อย!"
    elif score < 30:
        advice = "🔥 ยอดเยี่ยม! กำลังขึ้นทางที่ถูกต้องแล้ว!"
    else:
        advice = "🏆 ตำนานอย่างแท้จริง! ยังคงรักษาความเก่งนี้ไว้ล่วงหน้า!"
    
    embed.add_field(name="💡 ข้อแนะนำ", value=advice, inline=False)
    embed.set_footer(text="Deathline Score System • ทำงานต่อไปสู่ความสำเร็จ!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="team_status", description="ดูภาพรวมสถานะทีม ทั้งเดดไลน์และช่วงโฟกัสในเซิร์ฟเวอร์")
async def team_status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 สรุปสถานะการทำงานของทีม (Team War Room)",
        color=discord.Color.from_rgb(52, 152, 219),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="⏳ เดดไลน์ที่กำลังนับถอยหลัง", value=f"`{len(bot.active_tasks)}` งาน", inline=True)
    embed.add_field(name="🎯 สมาชิกที่กำลัง Focus Pomodoro", value=f"`{len(bot.active_focus)}` คน", inline=True)
    embed.add_field(name="🎭 มีมในคลังระบบ", value=f"`{sum(MemeManager.get_stats().values())}` รูป", inline=True)
    
    if bot.active_tasks:
        tasks_preview = "\n".join([f"• `{tid}`: **{info['task_name']}** (<t:{int(info['target_time'].timestamp())}:R>)" for tid, info in list(bot.active_tasks.items())[:5]])
        embed.add_field(name="📋 งานที่ใกล้ครบกำหนดที่สุด", value=tasks_preview, inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="focus_start", description="เริ่มโหมด Co-working / Pomodoro จับเวลาโฟกัสทำงาน")
@app_commands.describe(
    minutes="เวลาที่ต้องการโฟกัส (ค่าเริ่มต้น 25 นาที)",
    session_name="หัวข้อที่กำลังโฟกัส (เช่น ปั่นโค้ด API, วาด Mockup)"
)
async def focus_start(interaction: discord.Interaction, minutes: int = 25, session_name: str = "Focus Session"):
    user_id = interaction.user.id
    if minutes <= 0:
        await interaction.response.send_message("❌ กรุณาระบุจำนวนนาทีที่มากกว่า 0 ครับ", ephemeral=True)
        return

    if user_id in bot.active_focus:
        old_job_id = bot.active_focus[user_id].get("job_id")
        if old_job_id:
            try:
                bot.scheduler.remove_job(old_job_id)
            except Exception:
                pass
        bot.active_focus.pop(user_id, None)

    now = datetime.now(timezone.utc)
    target_time = now + timedelta(minutes=minutes)
    unix_timestamp = int(target_time.timestamp())
    job_id = f"focus_{user_id}_{int(now.timestamp())}"

    bot.scheduler.add_job(
        dispatch_focus_alert,
        trigger="date",
        run_date=target_time,
        args=[user_id, interaction.channel_id, session_name, minutes],
        id=job_id,
        replace_existing=True
    )

    bot.active_focus[user_id] = {
        "channel_id": interaction.channel_id,
        "session_name": session_name,
        "end_time": target_time,
        "job_id": job_id
    }

    embed = discord.Embed(
        title="🎯 เริ่มต้นช่วง Focus / Co-working!",
        description=f"เปิดโหมดมีสมาธิสำหรับ <@{user_id}>",
        color=discord.Color.from_rgb(52, 152, 219)
    )
    embed.add_field(name="📌 เซสชัน", value=f"**{session_name}**", inline=False)
    embed.add_field(name="⏱️ ระยะเวลา", value=f"`{minutes}` นาที", inline=True)
    embed.add_field(name="🔔 แจ้งเตือนเมื่อถึง", value=f"<t:{unix_timestamp}:T> (<t:{unix_timestamp}:R>)", inline=True)
    embed.set_footer(text="สู้ๆ ครับ! ปิดการแจ้งเตือนที่ไม่จำเป็นแล้วลุยกันเลย 🚀")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="focus_stop", description="หยุดเวลา Focus / Pomodoro ปัจจุบันของคุณ")
async def focus_stop(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in bot.active_focus:
        await interaction.response.send_message("ℹ️ คุณไม่ได้อยู่ในช่วง Focus Session ในขณะนี้", ephemeral=True)
        return

    info = bot.active_focus[user_id]
    job_id = info.get("job_id")
    if job_id:
        try:
            bot.scheduler.remove_job(job_id)
        except Exception:
            pass

    session_name = info["session_name"]
    bot.active_focus.pop(user_id, None)

    embed = discord.Embed(
        title="🛑 หยุดช่วง Focus เรียบร้อยแล้ว",
        description=f"ยกเลิกการจับเวลาสำหรับ **{session_name}** เรียบร้อยแล้วครับ",
        color=discord.Color.from_rgb(149, 165, 166)
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="sync", description="เคลียร์คำสั่งซ้ำซ้อนและซิงค์ Slash Commands ให้แสดงเพียง 1 ชุด")
async def sync_slash(interaction: discord.Interaction):
    if interaction.guild:
        bot.tree.clear_commands(guild=interaction.guild)
        await bot.tree.sync(guild=interaction.guild)
    synced = await bot.tree.sync()
    await interaction.response.send_message(f"✅ เคลียร์คำสั่งซ้ำเรียบร้อย! มีคำสั่ง Slash Commands ทั้งหมด {len(synced)} คำสั่ง (ชุดเดียว สะอาดตา)", ephemeral=True)


@bot.command(name="sync")
async def sync_prefix(ctx: commands.Context):
    if ctx.guild:
        bot.tree.clear_commands(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
    synced = await bot.tree.sync()
    await ctx.send(f"✅ เคลียร์คำสั่งซ้ำเรียบร้อย! ซิงค์ {len(synced)} Slash Commands เรียบร้อยแล้ว!")


@bot.command(name="roast")
async def roast_prefix(ctx: commands.Context, *, task: str = "โปรเจกต์ Hackathon"):
    msg = random.choice(AIRoastEngine.VARIED_ROASTS).format(task_name=task)
    await ctx.reply(f"{ctx.author.mention} {msg}")


@bot.tree.command(name="deathline_help", description="ดูคำสั่งทั้งหมดและวิธีใช้งานบอท Deathline")
async def deathline_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💀 คู่มือการใช้งาน Discord Bot 'Deathline'",
        description="บอทช่วยเตือนเดดไลน์อัตโนมัติพร้อมระบบ **AI Smart Roast & Team Deadlines** สำหรับ Hackathon!",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    embed.add_field(
        name="📌 คำสั่งเดดไลน์เดี่ยวและทีม (Solo & Team Commands)",
        value=(
            "• `/deathline_add [task_name] [deadline_minutes]` : เพิ่มงานเดี่ยว พร้อมระบุเพื่อนร่วมทีม\n"
            "• `/team_deadline [task_name] [deadline_minutes] [member1]...` : ตั้งเดดไลน์ระดับทีม แท็กทุกคนเพื่อรับแรงกดดันร่วมกัน\n"
            "• `/deathline_list` : ดูรายการเดดไลน์ที่กำลังนับถอยหลัง พร้อมชื่อผู้สร้างและทีม\n"
            "• `/deathline_done [task_id]` : ปิดงานเมื่อเสร็จก่อนเวลา เพื่อยกเลิก AI Roast ทั้งหมด"
        ),
        inline=False
    )
    embed.add_field(
        name="� ระบบคะแนนและลีดเดอร์บอร์ด (Score System)",
        value=(
            "• `/scoreboard` : ดูลีดเดอร์บอร์ดคะแนนทั้งทีม\n"
            "• `/my_score` : ดูคะแนนและเทียร์ส่วนตัวของคุณ\n"
            "• ✅ ทำงานเสร็จก่อนเวลา → +5 Score\n"
            "• ❌ ไม่ทำเสร็จทันเวลา → -3 Score"
        ),
        inline=False
    )
    embed.add_field(
        name="�🎭 ระบบมีมและสถิติทีม (Meme & Team Features)",
        value=(
            "• `/meme_add [url] [category]` : เพิ่มรูปมีมของคุณเข้าสู่คลัง\n"
            "• `/meme_delete [query]` : ลบรูปมีมหรือ URL ที่ไม่ต้องการออกจากคลัง\n"
            "• `/meme_list` : ดูจำนวนรูปมีมทั้งหมดในระบบ\n"
            "• `/team_status` : ดูภาพรวมสงครามเดดไลน์ของทีม"
        ),
        inline=False
    )
    embed.add_field(
        name="🎯 Co-working Pomodoro & Tools",
        value=(
            "• `/focus_start [minutes] [session_name]` : เริ่มจับเวลาโฟกัสทำงาน\n"
            "• `/focus_stop` : หยุดช่วง Focus ปัจจุบัน\n"
            "• `!roast` / `!sync` : คำสั่งพิมพ์ด่วน"
        ),
        inline=False
    )
    embed.set_footer(text="Deathline Bot • Built for Hackathon Teams")
    await interaction.response.send_message(embed=embed)


# -------------------------------------------------------------
# TERMINAL INPUT HANDLER - Send messages from terminal through bot
# -------------------------------------------------------------
async def terminal_message_handler():
    """อ่านอินพุตจากเทอร์มิแนลและส่งข้อความไปยัง Discord"""
    loop = asyncio.get_event_loop()
    
    def read_terminal_input():
        """ฟังก์ชันอ่านข้อความจากเทอร์มิแนล"""
        return input()
    
    # ⚡ Secret Mode - No visible output
    
    while True:
        try:
            # อ่านอินพุตจากเทอร์มิแนลโดยไม่หยุด bot
            user_input = await loop.run_in_executor(None, read_terminal_input)
            user_input = user_input.strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                break
            
            elif user_input.lower() == "help":
                print("• msg <id> <text>  • list  • exit")
            
            elif user_input.lower() == "list":
                for guild in bot.guilds:
                    print(f"\n{guild.name}:")
                    for channel in guild.text_channels:
                        print(f"  #{channel.name} ({channel.id})")
                print()
            
            elif user_input.lower().startswith("msg"):
                parts = user_input.split(" ", 2)
                if len(parts) < 3:
                    print("❌ ใช้วิธี: msg <channel_id> <message>")
                    continue
                
                try:
                    channel_id = int(parts[1])
                    message = parts[2]
                    
                    channel = bot.get_channel(channel_id)
                    if not channel:
                        print(f"✗ Channel {channel_id} not found")
                        continue
                    
                    await channel.send(message)
                    print(f"✓ Sent")
                    
                except ValueError:
                    print("✗ Invalid ID")
                except Exception as e:
                    print(f"✗ Error: {e}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            pass


# ตัวแปรเก็บสถานะ Terminal Mode
terminal_mode_enabled = False

def setup_terminal_mode():
    """ตั้งค่า Terminal Input Handler"""
    global terminal_mode_enabled
    if not terminal_mode_enabled:
        terminal_mode_enabled = True
        # สร้าง task สำหรับรัน terminal handler
        asyncio.create_task(terminal_message_handler())


# -------------------------------------------------------------
# MAIN ENTRYPOINT
# -------------------------------------------------------------
def run_bot():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "!" * 60)
        print("❌ ข้อผิดพลาด: ยังไม่ได้ตั้งค่า DISCORD_BOT_TOKEN ในไฟล์ .env")
        print("👉 โปรดเปิดไฟล์ .env แล้วใส่ Bot Token ของคุณ จากนั้นรันใหม่อีกครั้ง")
        print("!" * 60 + "\n")
        sys.exit(1)

    print("🚀 Connecting to Discord Gateway...")
    try:
        bot.run(TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        print("⚠️ Message Content Intent not enabled in Developer Portal. Launching with default intents...")
        safe_bot = DeathlineBot(intents=discord.Intents.default())
        safe_bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()
