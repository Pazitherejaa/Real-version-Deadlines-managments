# 💀 Deathline - Discord Bot สำหรับ Co-working, Deadline & AI Intent Roaster

บอท Discord สไตล์สายลุยสำหรับงาน Hackathon ที่ช่วยจับเวลาเดดไลน์โปรเจกต์ เตือนงานแบบ **AI Intent Analysis & Multi-Message Escalation Protocol** พร้อมระบบจับเวลาโฟกัส Co-working (Pomodoro) ในตัว

---

## 📁 โครงสร้างโปรเจกต์

```text
deathline-bot/
├── bot.py              # โค้ดหลักของบอท (Slash Commands, Event Listener, Intent Analyzer & Multi-Message Escalation)
├── memes.json          # คลังเก็บรูป Meme URLs ตามหมวดหมู่ (50%, 25%, 10%, 0%, custom)
├── memes/              # โฟลเดอร์เก็บไฟล์รูปภาพมีมแบบ Local
├── requirements.txt    # รายการแพ็กเกจ (discord.py, python-dotenv, apscheduler, aiohttp)
├── .env                # เก็บค่า Token ของ Discord Bot และ Gemini API Key
├── .env.example        # ตัวอย่างไฟล์คอนฟิก
└── README.md           # คู่มือการติดตั้งและใช้งาน
```

---

## ⌨️ รายการคำสั่ง Slash Commands ทั้งหมด

| คำสั่ง | คำอธิบาย | ตัวอย่างการใช้งาน |
|---|---|---|
| `/deathline_add` | เพิ่มเดดไลน์งานเดี่ยว/ทีม พร้อมระบบเตือนอัตโนมัติ | `/deathline_add task_name: ปั่นสไลด์ Pitch deadline_minutes: 30` |
| `/team_deadline` | ตั้งเดดไลน์ระดับทีม พร้อมแท็กเพื่อนร่วมทีมทุกคน | `/team_deadline task_name: ประกอบร่าง API deadline_minutes: 45 member1: @A member2: @B` |
| `/deathline_list` | ดูรายการงานทั้งหมดที่กำลังนับถอยหลังอยู่แบบ Real-time พร้อมชื่อทีม | `/deathline_list` |
| `/deathline_done` | ปิดงานเมื่อทำเสร็จก่อนเวลา (รีเซ็ต Strike และยกเลิกการแซวทั้งหมด) | `/deathline_done task_id: 3a1f9c` |
| `/roast_preview` | ทดลองดูตัวอย่างข้อความทั้งโหมดแซว, Slacker และโหมดชมคนตั้งใจทำงาน | `/roast_preview level: Working Encouragement` |
| `/sync` หรือ `!sync` | บังคับซิงค์ Slash Commands ให้ขึ้นทันทีในห้องแชท | `/sync` หรือพิมพ์ `!sync` |
| `/meme_add` | อัปโหลด/บันทึกลิงก์รูปมีมของตัวเองเข้าสู่ระบบ | `/meme_add url: https://... category: 10% Remaining` |
| `/meme_list` | ดูสถิติและจำนวนรูปมีมที่มีในระบบ | `/meme_list` |
| `/focus_start` | เริ่มจับเวลาโฟกัสทำงานสไตล์ Pomodoro / Co-working | `/focus_start minutes: 25 session_name: ปั่นโค้ด API` |
| `/focus_stop` | ยกเลิก/หยุดช่วงเวลา Focus ปัจจุบัน | `/focus_stop` |
| `/deathline_help` | แสดงคู่มือการใช้งานบอทและคำสั่งทั้งหมด | `/deathline_help` |

To active bot use terminal and cd to the location of file then python bot.py to acitve it
