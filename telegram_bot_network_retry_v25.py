# -*- coding: utf-8 -*-
import traceback
"""
Telegram Protection / Admin / Fun Bot
نسخة PyDroid - إعادة اتصال مستمرة عند أخطاء الشبكة، بدون مكتبات خارجية.

مهم:
1) شغّل الملف في PyDroid.
2) اجعل البوت Admin في المجموعة مع صلاحيات حذف الرسائل، تقييد الأعضاء، حظرهم، وتثبيت الرسائل حسب الحاجة.
3) لتعطيل وضع الخصوصية للمجموعات: BotFather -> /setprivacy -> Disable، حتى تصل للبوت رسائل الأعضاء العادية.
4) يمكن وضع التوكن في BOT_TOKEN أو متغير البيئة BOT_TOKEN.

هذه النسخة تعالج المشكلة السابقة: أزرار الأقسام ليست رسائل "تم استلام الأمر" فقط، بل تنفذ وظائف فعلية أو تفتح إعداد الوظيفة المطلوبة."""

import os, json, time, re, random, sqlite3, urllib.request, urllib.parse, urllib.error, tempfile, socket

# نترك Android/VPN يختار مسار الشبكة المناسب؛ فرض IPv4 قد يسبب Network is unreachable لبعض الشبكات.
from html import escape
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8626048634:AAFJl3go77Z2VenU6-H5yHK0HYf1LEGgs84")
API = "https://api.telegram.org/bot" + BOT_TOKEN + "/"
DB = "telegram_bot.sqlite3"
DEVELOPER = "n6iiii"


# ---------------- 600 رد جاهز ----------------
# الردود الجاهزة تعمل تلقائياً عند تطابق الرسالة، ويمكن للمشرف تعطيل الردود من إعدادات الردود.
_REPLY_SUFFIXES = [
    "", " والله", " حبيبي", " حبيبتي", " يالغالي", " يالغالية", " يا صديقي", " يا صديقتي", " بالعراقي", " 😂"
]
_REPLY_BASES = [
    ("هلا", "هلا وغلا 🌹 نورت المكان."),
    ("مرحبا", "مرحبتين وألف هلا ❤️"),
    ("اهلا", "أهلاً وسهلاً بيك 🌷"),
    ("السلام عليكم", "وعليكم السلام ورحمة الله وبركاته 🌹"),
    ("صباح الخير", "صباح النور والسرور ☀️"),
    ("مساء الخير", "مساء الورد 🌹"),
    ("شلونك", "تمام والحمد لله، إنت شلونك؟ ❤️"),
    ("شلونج", "بخير وعافية، شلونج؟ 🌷"),
    ("شخبارك", "أخبارنا طيبة دامك بخير 😄"),
    ("شخبارج", "كلشي تمام والحمد لله 🌷"),
    ("وينك", "هنا وياكم، ما غبت 😎"),
    ("وينج", "موجودة وياكم 🌸"),
    ("اشتقتلك", "وأنا هم اشتقتلك ❤️"),
    ("احبك", "وأني أقدّر محبتك 🌹"),
    ("احبج", "الله يسعد قلبج ❤️"),
    ("حبيبي", "عيوني حبيبي 🌹"),
    ("حبيبتي", "عيوني حبيبتي 🌷"),
    ("يا بعد قلبي", "بعد روحي إنت ❤️"),
    ("يا روحي", "تدلل يا روحي 🌹"),
    ("تدلل", "تأمر أمر 😎"),
    ("تأمر", "من عيوني 🌹"),
    ("شكرا", "العفو، بالخدمة دائماً ❤️"),
    ("شكراً", "العفو يا طيب 🌷"),
    ("مشكور", "تدلل، هذا واجبي 🌹"),
    ("مشكورة", "العفو حبيبتي 🌷"),
    ("عاشت ايدك", "تعيش وتسلم 🌹"),
    ("عاشت ايدج", "تسلمين يا وردة 🌷"),
    ("الله يسلمك", "ويسلمك ويحفظك ❤️"),
    ("الله يحفظك", "آمين ويحفظك من كل شر 🤲"),
    ("الله يوفقك", "آمين وياك يا رب 🤲"),
    ("الله يسعدك", "ويسعد قلبك وأيامك ❤️"),
    ("الله يخليك", "ويخليك لأحبابك 🌹"),
    ("امين", "آمين يا رب العالمين 🤲"),
    ("آمين", "آمين وياك يا رب ❤️"),
    ("تصبح على خير", "وأنت من أهله، أحلام سعيدة 🌙"),
    ("تصبحين على خير", "وأنتِ من أهله 🌙❤️"),
    ("تصبحون على خير", "وأنتم من أهله 🌙"),
    ("باي", "باي، نشوفك على خير 👋"),
    ("باي باي", "مع السلامة يا وردة 🌹"),
    ("مع السلامة", "الله وياك ويحفظك 🌷"),
    ("سلام", "سلامات يا غالي 👋"),
    ("ضحكتني", "المهم ضحكتك تبقى حاضرة 😂❤️"),
    ("هههه", "دوم الضحكة 😂"),
    ("ههههه", "ضحكتك حلوة 😂🌹"),
    ("هههههه", "ها شنو هاي الضحكة 😂😂"),
    ("😂", "دوم الضحك يا رب 😂"),
    ("🤣", "واضح اليوم مودك ضحك 🤣"),
    ("زين", "الحمد لله، المهم أنت زين 🌹"),
    ("تمام", "تمام التمام 😎❤️"),
    ("تمام الحمدلله", "دوم الحمد لله على كل حال 🤲"),
    ("الحمدلله", "الحمد لله دائماً وأبداً 🤲"),
    ("الحمد لله", "الحمد لله رب العالمين ❤️"),
    ("شنو تسوي", "أرتب أموري وياكم 😎"),
    ("شنو تسوين", "أتابعكم وأونس وياكم 🌷"),
    ("شنو الاخبار", "كلها طيبة إن شاء الله 🌹"),
    ("شنو الأخبار", "الأخبار حلوة بوجودكم ❤️"),
]
_BUILTIN_REPLIES = {}
for _base, _answer in _REPLY_BASES:
    for _suffix in _REPLY_SUFFIXES:
        _key = (_base + _suffix).strip().lower()
        if _key not in _BUILTIN_REPLIES:
            _BUILTIN_REPLIES[_key] = _answer
# يضمن 600 رد بالضبط مع ردود إضافية طبيعية عند اختلاف الصياغة.
_EXTRA_STARTS = [
    "وين", "ليش", "شلون", "شنو", "منو", "اكو", "اكو احد", "تعال", "تعالي", "اسمع", "اسمعي",
    "جاوب", "جاوبي", "رد", "ردي", "ساعدني", "ساعديني", "اريد", "أريد", "محتاج", "محتاجة",
    "تعرف", "تعرفين", "تدري", "تدرين", "عندك", "عندج", "يصير", "ممكن", "اقدر", "أكدر",
    "شنو رأيك", "شنو رايك", "رأيك", "رايك", "احب", "احبج", "احبك", "اشتاق", "اشتقت",
    "زعلان", "زعلانة", "فرحان", "فرحانة", "تعبان", "تعبانة", "مستانس", "مستانسة", "خوش", "حلو",
]
_EXTRA_ENDS = [" اليوم", " هسه", " بالليل", " بالصباح", " بالعصر", " وياي", " وياكم", " هنا", " بالحياة", "؟"]
for _a in _EXTRA_STARTS:
    for _b in _EXTRA_ENDS:
        _key=(_a+_b).strip().lower()
        if _key not in _BUILTIN_REPLIES:
            _BUILTIN_REPLIES[_key] = "تدلل 🌹 آني وياك، شنو تحتاج؟"
        if len(_BUILTIN_REPLIES) >= 600:
            break
    if len(_BUILTIN_REPLIES) >= 600:
        break
# إذا كان عدد التركيبات أقل من المطلوب، نضيف عبارات قصيرة فريدة.
_i=1
while len(_BUILTIN_REPLIES) < 600:
    _key=f"يا بوت {_i}"
    _BUILTIN_REPLIES[_key]="هلا بيك 🌹 آني حاضر، أمرني."
    _i += 1

BUILTIN_REPLIES = dict(list(_BUILTIN_REPLIES.items())[:600])

# ---------------- Telegram API ----------------
def api(method, data=None):
    if not BOT_TOKEN or BOT_TOKEN == "PUT_TOKEN_HERE":
        raise RuntimeError("ضع توكن البوت في BOT_TOKEN")
    data = data or {}
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(API + method, data=encoded)
    try:
        with urllib.request.urlopen(req, timeout=(35 if method == "getUpdates" else 10)) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        print("Telegram API error:", raw)
        return {"ok": False, "description": raw}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # أخطاء الشبكة مثل: [Errno 101] Network is unreachable
        msg = str(getattr(e, "reason", e))
        print("🌐 انقطاع الشبكة: %s" % msg)
        return {"ok": False, "network_error": True, "description": msg}
    except Exception as e:
        print("Network/API error:", repr(e))
        return {"ok": False, "description": str(e)}

def call(method, **kwargs):
    return api(method, kwargs)

def send(cid, text, keyboard=None, reply_to=None):
    d = {"chat_id": cid, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard: d["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    if reply_to: d["reply_to_message_id"] = reply_to
    return call("sendMessage", **d)

def edit(cid, mid, text, keyboard=None):
    d = {"chat_id": cid, "message_id": mid, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard: d["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    return call("editMessageText", **d)

def answer(cbid, text="تم", alert=False):
    return call("answerCallbackQuery", callback_query_id=cbid, text=text[:190], show_alert=bool(alert))

def delete(cid, mid):
    return call("deleteMessage", chat_id=cid, message_id=mid)


import tempfile

# Cache Telegram file_id so repeated songs are sent instantly without re-downloading.
SONG_FILE_CACHE = {}

def upload_audio_file(cid, path, caption="", reply_to=None, filename=None, content_type="audio/mpeg"):
    """Upload a real local audio file to Telegram using multipart/form-data."""
    boundary = "----PyDroidTelegramBoundary" + str(int(time.time()*1000))
    parts=[]
    def add_field(name, value):
        parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode('utf-8'))
    add_field('chat_id', str(cid))
    if caption:
        add_field('caption', caption)
        add_field('parse_mode', 'HTML')
    if reply_to:
        add_field('reply_to_message_id', str(reply_to))
    fname=filename or os.path.basename(path)
    head=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{fname}\"\r\nContent-Type: {content_type}\r\n\r\n").encode('utf-8')
    with open(path,'rb') as f: data=f.read()
    body=b''.join(parts)+head+data+b"\r\n"+f"--{boundary}--\r\n".encode('utf-8')
    req=urllib.request.Request(API+'sendAudio', data=body, headers={'Content-Type':'multipart/form-data; boundary='+boundary})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print('audio upload error:',repr(e))
        return {'ok':False,'description':str(e)}

# ---------------- SQLite ----------------
def db():
    c = sqlite3.connect(DB, timeout=20)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS settings(chat_id INTEGER PRIMARY KEY, welcome INTEGER DEFAULT 0, rules TEXT DEFAULT '', group_link TEXT DEFAULT '', silent INTEGER DEFAULT 0, welcome_text TEXT DEFAULT '', notifications INTEGER DEFAULT 1, auto_reply INTEGER DEFAULT 1, voice_notifications INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS protection(chat_id INTEGER, key TEXT, action TEXT DEFAULT 'delete', enabled INTEGER DEFAULT 0, PRIMARY KEY(chat_id,key));
    CREATE TABLE IF NOT EXISTS warnings(chat_id INTEGER, user_id INTEGER, count INTEGER DEFAULT 0, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS roles(chat_id INTEGER, user_id INTEGER, role TEXT, PRIMARY KEY(chat_id,user_id,role));
    CREATE TABLE IF NOT EXISTS points(chat_id INTEGER, user_id INTEGER, points INTEGER DEFAULT 0, messages INTEGER DEFAULT 0, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS bank(chat_id INTEGER, user_id INTEGER, money INTEGER DEFAULT 1000, debt INTEGER DEFAULT 0, last_salary INTEGER DEFAULT 0, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS custom_replies(chat_id INTEGER, trigger TEXT, reply TEXT, PRIMARY KEY(chat_id,trigger));
    CREATE TABLE IF NOT EXISTS known_chats(chat_id INTEGER PRIMARY KEY, title TEXT, type TEXT);
    CREATE TABLE IF NOT EXISTS game_state(chat_id INTEGER PRIMARY KEY, game TEXT, answer TEXT, question TEXT);
    CREATE TABLE IF NOT EXISTS messages(chat_id INTEGER, message_id INTEGER, user_id INTEGER, kind TEXT, PRIMARY KEY(chat_id,message_id));
    CREATE TABLE IF NOT EXISTS menu_context(chat_id INTEGER, menu_message_id INTEGER, target_user_id INTEGER, target_message_id INTEGER, target_json TEXT, PRIMARY KEY(chat_id,menu_message_id));
    CREATE TABLE IF NOT EXISTS content_history(chat_id INTEGER, kind TEXT, item_key TEXT, used_at INTEGER, PRIMARY KEY(chat_id,kind,item_key));
    CREATE TABLE IF NOT EXISTS user_meta(chat_id INTEGER, user_id INTEGER, nickname TEXT DEFAULT '', bio TEXT DEFAULT '', title TEXT DEFAULT '', likes INTEGER DEFAULT 0, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS named_bans(chat_id INTEGER, name TEXT PRIMARY KEY);
    CREATE TABLE IF NOT EXISTS content_bans(chat_id INTEGER, kind TEXT, value TEXT, PRIMARY KEY(chat_id,kind,value));
    CREATE TABLE IF NOT EXISTS tags(chat_id INTEGER, tag_name TEXT, user_id INTEGER, PRIMARY KEY(chat_id,tag_name,user_id));
    CREATE TABLE IF NOT EXISTS custom_commands(chat_id INTEGER, command TEXT, reply TEXT, PRIMARY KEY(chat_id,command));
    CREATE TABLE IF NOT EXISTS birthdays(chat_id INTEGER, user_id INTEGER, day TEXT, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS global_bans(user_id INTEGER PRIMARY KEY);
    CREATE TABLE IF NOT EXISTS command_toggles(chat_id INTEGER, command TEXT, enabled INTEGER DEFAULT 1, PRIMARY KEY(chat_id,command));
    CREATE TABLE IF NOT EXISTS admin_permissions(chat_id INTEGER, user_id INTEGER, perm TEXT, enabled INTEGER DEFAULT 1, PRIMARY KEY(chat_id,user_id,perm));
    CREATE TABLE IF NOT EXISTS user_stats(chat_id INTEGER, user_id INTEGER, sakkat INTEGER DEFAULT 1, PRIMARY KEY(chat_id,user_id));
    CREATE TABLE IF NOT EXISTS whisper_sessions(user_id INTEGER PRIMARY KEY, target_id INTEGER NOT NULL, group_id INTEGER NOT NULL, created_at INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS whisper_messages(id INTEGER PRIMARY KEY AUTOINCREMENT, target_id INTEGER NOT NULL, group_id INTEGER NOT NULL, sender_id INTEGER NOT NULL, body TEXT NOT NULL, created_at INTEGER NOT NULL);
    """)
    # migrations for older sqlite files
    for col, ddl in [("welcome_text", "TEXT DEFAULT ''"), ("notifications", "INTEGER DEFAULT 1"), ("auto_reply", "INTEGER DEFAULT 1"), ("voice_notifications", "INTEGER DEFAULT 1")]:
        try: c.execute("ALTER TABLE settings ADD COLUMN %s %s" % (col, ddl))
        except sqlite3.OperationalError: pass
    c.commit(); c.close()

def one(sql, p=()):
    c=db(); r=c.execute(sql,p).fetchone(); c.close(); return r

def all_rows(sql,p=()):
    c=db(); r=c.execute(sql,p).fetchall(); c.close(); return r

def run(sql,p=()):
    c=db(); c.execute(sql,p); c.commit(); c.close()


# ---------------- Core helpers ----------------
PROT = {
    "links":"الروابط", "tag":"التاك والمنشن", "edit":"التعديل", "animated":"المتحركات",
    "photos":"الصور", "videos":"الفيديوهات", "documents":"الملفات", "bots":"البوتات",
    "forward":"التوجيه", "audio":"الصوت والبصمات", "contacts":"الجهات", "location":"الموقع",
    "channels":"القنوات", "spam":"التكرار", "stickers":"الملصقات", "voice":"البصمة",
    "english":"الإنكليزية", "persian":"الفارسية", "pin":"التثبيت", "notifications":"الإشعارات",
    "all":"الكل"
}

BOT_ID_CACHE = None

def kb(rows):
    return {"inline_keyboard": rows}

def btn(text, data):
    return {"text": text, "callback_data": data}

def home_kb():
    return kb([
        [btn("🛡️ الحماية","menu:protect"), btn("👮 الأدمن","menu:admin")],
        [btn("👑 المدير","menu:manager"), btn("🏗️ المنشئ","menu:creator")],
        [btn("💎 المالك","menu:owner"), btn("😂 التحشيش","menu:funny")],
        [btn("🎮 التسلية","menu:fun"), btn("💰 البنك","menu:bank")],
        [btn("🧹 التنظيف","menu:clean"), btn("🎯 الألعاب","menu:games")],
        [btn("🧑‍💻 المطور","menu:developer")]
    ])

ADMIN_PAGES = {
1: """👮 <b>اوامر ادمنية المجموعه</b>
—————————————
⌔︙اسم للبوت + الامر {جميع الاوامر}
⌔︙رفع، تنزيل ← مميز
⌔︙المميزين ← مسح المميزين
⌔︙رفع المالك
⌔︙تاك ، تاك للكل ، المجموعه
⌔︙منع ، الغاء منع
—————————————
⌔︙الاوامر التالية ← {بالرد ، بالمعرف}
⌔︙حظر ، طرد ← الغاء حظر
⌔︙كتم ← الغاء كتم
⌔︙تقييد ← الغاء تقييد
⌔︙كشف ، رفع ← القيود
⌔︙انذار ← {بالرد ، بالمعرف}
—————————————
⌔︙عرض القوائم:
⌔︙المنشئين الاساسيين ، المنشئين
⌔︙المدراء ، الادمنيه ، المميزين
⌔︙المشرفين ، المكتومين ، قائمه المنع
—————————————
⌔︙تثبيت ، الغاء تثبيت
⌔︙الرابط ، الاعدادات ، الحمايه
⌔︙الترحيب ، القوانين
⌔︙ضع رتبه ← {اسم الرتبه}
⌔︙تحكم ← {بالرد ، بالمعرف}""",
2: """👮 <b>اوامر الادمن — الاعضاء والادمنيه</b>
—————————————
⌔︙ايدي ، ايدي بالرد ، رسائلي
⌔︙تفاعلي ، بايو ، زوجني
⌔︙لقبي ، لقبه {بالرد}
⌔︙اسمي ، معرفي ، رابطي
⌔︙جهاتي ، سحكاتي ، نقاطي
⌔︙بيع نقاطي + العدد
⌔︙مسح نقاطي ، التفاعل
⌔︙معلوماتي ، كول + الكلمه
⌔︙انطق + الكلمه ، الانشاء ، انشاء البوت
⌔︙منشن ، نداء ، ترند
⌔︙زواج ، ثنائي اليوم ، نبذه
⌔︙الوقت ، الساعه ، التاريخ
⌔︙زخرفه ، زخرفه + اسم
⌔︙تحويل الصيغ ، غنيلي ، اغنيه
⌔︙همسه ، الابراج ، اسم برجك
⌔︙صورتي ، جمالي ، تيكتوك
⌔︙صلاحياتي ، رتبتي ، نزلني
⌔︙صلاحياته ، الرتبه ، تفاعله ، جهاته
⌔︙كشف ، كشف عام ، رابطه
—————————————
⌔︙رفع ، تنزيل ← ادمن
⌔︙الادمنيه ← مسح الادمنيه
⌔︙رفع الادمنيه
⌔︙كشف ، طرد ، قفل ← البوتات
⌔︙قفل البوتات ← بالطرد
⌔︙فحص ← البوت
⌔︙طرد ← المحذوفين
⌔︙قفل فتح ← القنوات
⌔︙مسح التعديل""",
3: """👮 <b>اوامر الادمن — الردود والتفعيل</b>
—————————————
⌔︙اضف ، مسح تاك
⌔︙قائمه تاك الاسم
⌔︙مسح قائمه تاك الاسم
⌔︙حظر ، طرد اسم + الاسم
⌔︙الغاء حظر اسم + الاسم
⌔︙الاسماء المحظوره
⌔︙مسح الاسماء المحظوره
—————————————
⌔︙تغيير رد ← {اسم الرتبه والنص}
⌔︙وضع الرتب ← {بالرد ، بالمعرف}
⌔︙ضع رتبه ← {اسم الرتبه}
⌔︙مسح رتبه ← {بالرد ، بالمعرف}
—————————————
⌔︙وضع اسم + اسم المجموعه
⌔︙وضع رابط ، صوره ، قوانين ، وصف ، الترحيب
⌔︙مسح الرابط ، انشاء رابط ، انشاء رابط انضمام
⌔︙تفعيل ، تعطيل الرابط العادي
—————————————
⌔︙تفعيل ، تعطيل: الايدي، البايو، الرابط
⌔︙الترحيب، منشن، انطق، صورتي، اسمي، نبذه
⌔︙الردود، الابراج، التفاعل، غنيلي، شعر، قصيده
⌔︙صوره، متحركه، الصيغ، كول
⌔︙الاذكار، الاقتباس (كل ساعة)
—————————————
⌔︙تاك عام ، all ، نداء للكل
⌔︙سجل الاداره
⌔︙الميديا ← امسح
⌔︙اضف رسائل + العدد / اضف نقاط + العدد / اضف سحكات + العدد""",
4: """👮 <b>اوامر الادمن — الاختصارات</b>
—————————————
⌔︙ايدي - ا
⌔︙رفع مميز - م
⌔︙رفع ادمن - اد
⌔︙رفع مدير - مد
⌔︙رفع منشئ - من
⌔︙رفع منشئ الاساسي - اس
⌔︙رفع مطور - مط
⌔︙رفع مطور ثانوي - ثانوي
⌔︙تنزيل الكل بالرد - تك
⌔︙تعطيل الايدي بالصوره - تعط
⌔︙تفعيل الايدي بالصوره - تفع
⌔︙تغيير الايدي - تغ
⌔︙تنزيل جميع الرتب - تنز
⌔︙قفل الاشعارات - قق
⌔︙فتح الاشعارات - فف
⌔︙الرابط - ر
⌔︙الردود - رر
⌔︙تثبيت - ث
⌔︙كشف - ك
⌔︙تاك - تت
⌔︙تاك للكل - تكك
⌔︙رفع القيود - رف
⌔︙الغاء حظر - الغ
⌔︙اضف رد - رد / مسح رد - مر
⌔︙غنيلي - غ / اغنيه - غغ
⌔︙شعر - ش / قصيده - ق
⌔︙نقاطي - ن / اسالني - س / لغز - ل
⌔︙معاني - مع / حزوره - ح / صورتي - ص
⌔︙نداء - ند / ميوزك - مي"""
}

ADMIN_TOGGLES = [
    ("id_photo", "🪪 ايدي بالصورة"), ("id_plain", "🪪 ايدي بدون صورة"),
    ("welcome", "👋 الترحيب"), ("group_link", "🔗 الرابط"),
    ("verify", "✅ التحقق"), ("games", "🎮 الألعاب"),
    ("funny", "😂 التحشيش"), ("kick_me", "🚪 اطردني"),
    ("bio", "📝 البايو"), ("my_link", "🔗 رابطي"),
    ("my_photo", "🖼️ صورتي"), ("my_name", "🏷️ اسمي"),
    ("replies", "💬 الردود"), ("zodiac", "♈ الأبراج"),
    ("interaction", "📊 التفاعل"), ("music", "🎵 غنيلي / أغنية"),
    ("poem", "🎙️ شعر / قصيدة"), ("image", "🖼️ صورة"),
    ("gif", "🎞️ متحركة"), ("formats", "🔄 تحويل الصيغ"),
    ("call", "📢 كول"), ("adhkar", "📿 الأذكار"),
    ("quote", "💭 الاقتباس"), ("auto_tag", "📣 التاك التلقائي"),
    ("auto_call", "📢 النداء التلقائي"), ("auto_clean", "🧹 المسح التلقائي"),
    ("cleaner", "🧼 المنظف التلقائي"), ("points", "⭐ النقاط والرسائل"),
    ("bank", "💰 البنك"), ("birthday", "🎂 عيد الميلاد"), ("whisper", "🤫 الهمسة"),
]

def command_toggle(cid, key):
    r = one("SELECT enabled FROM command_toggles WHERE chat_id=? AND command=?", (cid,key))
    return True if r is None else bool(r[0])

def set_command_toggle(cid, key, enabled):
    run("INSERT INTO command_toggles(chat_id,command,enabled) VALUES(?,?,?) ON CONFLICT(chat_id,command) DO UPDATE SET enabled=excluded.enabled", (cid,key,1 if enabled else 0))

def toggle_label(cid, key, label):
    return ("🟢 " if command_toggle(cid,key) else "🔴 ") + label

def admin_toggle_kb(cid, page=1):
    # 8 toggles per page; every item is an actual on/off setting.
    pages = [ADMIN_TOGGLES[0:8], ADMIN_TOGGLES[8:16], ADMIN_TOGGLES[16:24], ADMIN_TOGGLES[24:]]
    page = max(1, min(4, page))
    rows=[]; row=[]
    for key,label in pages[page-1]:
        row.append(btn(toggle_label(cid,key,label), "toggle:"+key+":"+str(page)))
        if len(row)==2:
            rows.append(row); row=[]
    if row: rows.append(row)
    nav=[]
    for i in range(1,5):
        nav.append(btn(("● " if i==page else "○ ")+str(i), "admin:page:"+str(i)))
    rows.append(nav)
    rows.append([btn("⚡ تفعيل الكل", "admin:all"), btn("⛔ تعطيل الكل", "admin:none")])
    rows.append([btn("👮 إجراءات الإدارة", "admin:actions"), btn("📋 القوائم", "list:menu")])
    rows.append([btn("⬅️ الرئيسية", "home")])
    return kb(rows)

def admin_actions_kb():
    return kb([
        [btn("🚫 حظر بالرد", "act:ban"), btn("👢 طرد بالرد", "act:kick")],
        [btn("🔇 كتم بالرد", "act:mute"), btn("🔊 رفع الكتم", "act:unmute")],
        [btn("📌 تثبيت بالرد", "act:pin"), btn("🗑️ مسح بالرد", "act:delete")],
        [btn("👑 رفع أدمن بالرد", "role:add:admin"), btn("➖ تنزيل أدمن", "role:del:admin")],
        [btn("⭐ رفع مميز", "role:add:special"), btn("➖ تنزيل مميز", "role:del:special")],
        [btn("📣 تاك للكل", "tagall"), btn("⚠️ إنذار بالرد", "warn")],
        [btn("📋 القوائم", "list:menu")],
        [btn("⬅️ رجوع للأدمن", "menu:admin")]
    ])

def admin_kb(page=1):
    return admin_toggle_kb(0, page)

def protect_kb(cid):
    rows=[]
    for key,label in PROT.items():
        rows.append([btn(("🔒 " if prot(cid,key) else "🔓 ")+label, "prot:"+key)])
    rows.append([btn("⚙️ طريقة العقوبة","protmode"), btn("⬅️ الرئيسية","home")])
    return kb(rows)

def settings(cid):
    r=one("SELECT * FROM settings WHERE chat_id=?",(cid,))
    if not r:
        run("INSERT OR IGNORE INTO settings(chat_id) VALUES(?)",(cid,))
        r=one("SELECT * FROM settings WHERE chat_id=?",(cid,))
    return dict(r)

def set_setting(cid,col,value):
    allowed={"welcome","rules","group_link","silent","welcome_text","notifications","auto_reply","voice_notifications"}
    if col not in allowed: return False
    run("UPDATE settings SET %s=? WHERE chat_id=?"%col,(value,cid))
    return True

def prot(cid,key):
    r=one("SELECT enabled FROM protection WHERE chat_id=? AND key=?",(cid,key))
    return bool(r and r[0])

def set_prot(cid,key,on,mode=None):
    if key not in PROT: return
    if mode is None:
        r=one("SELECT action FROM protection WHERE chat_id=? AND key=?",(cid,key))
        mode=r[0] if r else "delete"
    run("INSERT INTO protection(chat_id,key,action,enabled) VALUES(?,?,?,?) ON CONFLICT(chat_id,key) DO UPDATE SET action=excluded.action,enabled=excluded.enabled",(cid,key,mode,int(bool(on))))

def action_for(cid,key):
    r=one("SELECT action FROM protection WHERE chat_id=? AND key=?",(cid,key))
    return r[0] if r else "delete"

def mention(user):
    if not user: return "عضو"
    name=escape((user.get("first_name") or user.get("username") or "عضو"))
    uid=user.get("id")
    return '<a href="tg://user?id=%s">%s</a>'%(uid,name) if uid else name

def target_from_message(m):
    r=m.get("reply_to_message")
    if not r or not r.get("from"): return None
    return dict(r["from"])

def is_admin(cid,uid):
    if not uid: return False
    r=call("getChatMember",chat_id=cid,user_id=uid)
    if not r.get("ok"): return False
    return r.get("result",{}).get("status") in ("creator","administrator")

def is_creator(cid,uid):
    if not uid: return False
    r=call("getChatMember",chat_id=cid,user_id=uid)
    return bool(r.get("ok") and r.get("result",{}).get("status")=="creator")

def bot_id():
    global BOT_ID_CACHE
    if BOT_ID_CACHE is None:
        r=call("getMe")
        BOT_ID_CACHE=r.get("result",{}).get("id") if r.get("ok") else 0
    return BOT_ID_CACHE

def can_target(cid,uid):
    if not uid: return False
    r=call("getChatMember",chat_id=cid,user_id=uid)
    if not r.get("ok"): return True
    return r.get("result",{}).get("status") not in ("creator","administrator")

def ban(cid,uid): return call("banChatMember",chat_id=cid,user_id=uid)
def kick(cid,uid): return call("banChatMember",chat_id=cid,user_id=uid,until_date=int(time.time())+60)
def mute(cid,uid):
    return call("restrictChatMember",chat_id=cid,user_id=uid,permissions=json.dumps({"can_send_messages":False,"can_send_audios":False,"can_send_documents":False,"can_send_photos":False,"can_send_videos":False,"can_send_video_notes":False,"can_send_voice_notes":False,"can_send_polls":False,"can_send_other_messages":False,"can_add_web_page_previews":False},ensure_ascii=False))
def unmute(cid,uid):
    return call("restrictChatMember",chat_id=cid,user_id=uid,permissions=json.dumps({"can_send_messages":True,"can_send_audios":True,"can_send_documents":True,"can_send_photos":True,"can_send_videos":True,"can_send_video_notes":True,"can_send_voice_notes":True,"can_send_polls":True,"can_send_other_messages":True,"can_add_web_page_previews":True},ensure_ascii=False))
def pin(cid,mid): return call("pinChatMessage",chat_id=cid,message_id=mid,disable_notification=True)
def unpin(cid,mid=None):
    d={"chat_id":cid}
    if mid: d["message_id"]=mid
    return call("unpinChatMessage",**d)

def mod_result(r,oktext):
    return oktext if r.get("ok") else "❌ فشل التنفيذ: <code>%s</code>"%escape(str(r.get("description","unknown")))

def save_menu_context(cid,menu_mid,target=None,target_mid=None):
    tj=json.dumps(target or {},ensure_ascii=False)
    run("INSERT OR REPLACE INTO menu_context(chat_id,menu_message_id,target_user_id,target_message_id,target_json) VALUES(?,?,?,?,?)",(cid,menu_mid,(target or {}).get("id"),target_mid,tj))

def menu_context(cid,menu_mid):
    r=one("SELECT target_json,target_message_id FROM menu_context WHERE chat_id=? AND menu_message_id=?",(cid,menu_mid))
    if not r: return None,None
    try: t=json.loads(r[0]) if r[0] else None
    except Exception: t=None
    return (t or None),r[1]

def action_target_from_callback(msg):
    return menu_context(msg["chat"]["id"],msg["message_id"])

def next_content(cid,kind,items):
    if not items: return ""
    unused=[]
    for item in items:
        key=str(item)
        if not one("SELECT 1 FROM content_history WHERE chat_id=? AND kind=? AND item_key=?",(cid,kind,key)):
            unused.append(item)
    if not unused:
        run("DELETE FROM content_history WHERE chat_id=? AND kind=?",(cid,kind))
        unused=list(items)
    item=random.choice(unused)
    run("INSERT OR IGNORE INTO content_history(chat_id,kind,item_key,used_at) VALUES(?,?,?,?)",(cid,kind,str(item),int(time.time())))
    return item


SONG_QUERIES = ['كاظم الساهر زيديني عشقاً', 'كاظم الساهر أنا وليلى', 'كاظم الساهر مدرسة الحب', 'كاظم الساهر هل عندك شك', 'كاظم الساهر قولي أحبك', 'كاظم الساهر إني خيرتك فاختاري', 'كاظم الساهر أحبيني بلا عقد', 'كاظم الساهر كل عام وأنت حبيبتي', 'كاظم الساهر الرسم بالكلمات', 'كاظم الساهر عيد وحب', 'ماجد المهندس تناديك', 'ماجد المهندس واحشني موت', 'ماجد المهندس على مودك', 'ماجد المهندس شهد الحروف', 'ماجد المهندس بين إيديا', 'ماجد المهندس أنجنيت', 'ماجد المهندس أوقع لك', 'ماجد المهندس أنت ملك', 'ماجد المهندس هدوء', 'ماجد المهندس مو بس حبك', 'حسين الجسمي بالبنط العريض', 'حسين الجسمي أحبك', 'حسين الجسمي بشرة خير', 'حسين الجسمي فقدتك', 'حسين الجسمي ستة الصبح', 'حسين الجسمي مهم جدا', 'حسين الجسمي سته الصبح', 'حسين الجسمي رعاك الله', 'حسين الجسمي اجا الليل', 'أصالة نصري عايشة على اللي فات', 'أصالة نصري بنت أكابر', 'أصالة نصري أكثر', 'أصالة نصري قد الحروف', 'أصالة نصري خانات الذكريات', 'أصالة نصري 60 دقيقة حياة', 'أصالة نصري سامحتك كتير', 'أصالة نصري جابوا سيرته', 'أصالة نصري سؤال بسيط', 'أصالة نصري يوم يومين', 'شيرين مشاعر', 'شيرين كده يا قلبي', 'شيرين على بالي', 'شيرين الوتر الحساس', 'شيرين صبري قليل', 'شيرين كل ما أغني', 'شيرين حبه جنة', 'شيرين متحاسبنيش', 'شيرين كلام عينيه', 'شيرين نساي', 'عمرو دياب تملي معاك', 'عمرو دياب نور العين', 'عمرو دياب قمرين', 'عمرو دياب وياه', 'عمرو دياب قصاد عيني', 'عمرو دياب ليلي نهاري', 'عمرو دياب راجع', 'عمرو دياب أنت الحظ', 'عمرو دياب أماكن السهر', 'عمرو دياب يا أنا يا لأ', 'نانسي عجرم آه ونص', 'نانسي عجرم يا طبطب', 'نانسي عجرم بدنا نولع الجو', 'نانسي عجرم معجبة مغرمة', 'نانسي عجرم إحساس جديد', 'نانسي عجرم شخبط شخابيط', 'نانسي عجرم في حاجات', 'نانسي عجرم لون عيونك', 'نانسي عجرم الدنيا حلوة', 'نانسي عجرم مية وخمسين', 'إليسا عيشالك', 'إليسا أجمل إحساس', 'إليسا حالة حب', 'إليسا مكتوبة ليك', 'إليسا سهرنا يا ليل', 'إليسا أسعد واحدة', 'إليسا أنا وبس', 'إليسا عكس اللي شايفينها', 'إليسا من أول دقيقة', 'إليسا صاحبة رأي', 'وائل كفوري عمري كلو', 'وائل كفوري البنت القوية', 'وائل كفوري لو حبنا غلطة', 'وائل كفوري حكم القلب', 'وائل كفوري مين حبيبي أنا', 'وائل كفوري كيفك يا وجعي', 'وائل كفوري شو رأيك', 'وائل كفوري أخدت القرار', 'وائل كفوري قلبي مشتاق', 'وائل كفوري كلنا مننجر', 'ملحم زين ضلي اضحكي', 'ملحم زين علواه', 'ملحم زين أنت مشيتي', 'ملحم زين ما عاد بدي ياك', 'ملحم زين رافقيني', 'ملحم زين غيبي يا شمس', 'ملحم زين يا حبيب القلب', 'ملحم زين على الله تعود', 'ملحم زين بدي حبك', 'ملحم زين عيوني', 'رحمة رياض وعد مني', 'رحمة رياض الكوكب', 'رحمة رياض أصعد للكمر', 'رحمة رياض ماكو مني', 'رحمة رياض أتحداكم', 'رحمة رياض اني أحجي', 'رحمة رياض ماما ماما', 'رحمة رياض عشتار', 'رحمة رياض حلو هالحب', 'رحمة رياض سوبرمان', 'سيف نبيل عشك موت', 'سيف نبيل فدوه', 'سيف نبيل ممكن', 'سيف نبيل لو', 'سيف نبيل إنتي', 'سيف نبيل لا لا', 'سيف نبيل قلب جديد', 'سيف نبيل غصباً', 'سيف نبيل يا ناس', 'سيف نبيل هواي أحبك', 'حاتم العراقي يا طير', 'حاتم العراقي مهاجر', 'حاتم العراقي أشوفك وين يا محبوبي', 'حاتم العراقي دكتوري', 'حاتم العراقي هم أحبه', 'حاتم العراقي خبرني', 'حاتم العراقي حبك', 'حاتم العراقي يا دنيا', 'حاتم العراقي ريت', 'حاتم العراقي يا غالي', 'نور الزين جيناك بهاية', 'نور الزين لا ما جاي', 'نور الزين عشكته', 'نور الزين اضحك', 'نور الزين مليته', 'نور الزين يا روحي', 'نور الزين عصفورة', 'نور الزين خاف من عندك', 'نور الزين أخاف عليك', 'نور الزين مو حرام', 'محمد السالم قلب قلب', 'محمد السالم ميهمني', 'محمد السالم حبيبي عراقي', 'محمد السالم ماخذ قلبي', 'محمد السالم خان الذهب', 'محمد السالم أحنه', 'محمد السالم لا تروح', 'محمد السالم أنتظر', 'محمد السالم يا حب', 'محمد السالم أحبك', 'علي صابر معقولة', 'علي صابر تعال', 'علي صابر شكد حلو', 'علي صابر ما أريدك', 'علي صابر يا دنيا', 'علي صابر غيمة', 'علي صابر بطة', 'علي صابر أنت حبك', 'علي صابر أحلى', 'علي صابر راح', 'أحمد المصلاوي موجوع قلبي', 'أحمد المصلاوي أخيراً قالها', 'أحمد المصلاوي سواها', 'أحمد المصلاوي تعال', 'أحمد المصلاوي ما نسيتك', 'أحمد المصلاوي مليون', 'أحمد المصلاوي مشتاق', 'أحمد المصلاوي يا ناس', 'أحمد المصلاوي تبقى إلي', 'أحمد المصلاوي حنيت', 'بلقيس انتهى', 'بلقيس دبلوماسي', 'بلقيس ممكن', 'بلقيس يا كل الحب', 'بلقيس حالة جديدة', 'بلقيس مزاجنجي', 'بلقيس قدر', 'بلقيس صابرة', 'بلقيس غلط', 'بلقيس يا هوى', 'أحلام تدري ليش', 'أحلام هذا أنا', 'أحلام مستغرب', 'أحلام وش ذكرك', 'أحلام أبرحل', 'أحلام الله يصبرني', 'أحلام فضها سيرة', 'أحلام أنا ما أستاهل', 'أحلام مثير', 'أحلام ليه متضايق', 'عبدالمجيد عبدالله تتنفسك دنياي', 'عبدالمجيد عبدالله رهيب', 'عبدالمجيد عبدالله يا ابن الأوادم', 'عبدالمجيد عبدالله إنسان أكثر', 'عبدالمجيد عبدالله من مثلك', 'عبدالمجيد عبدالله هانت عليك', 'عبدالمجيد عبدالله غلطة', 'عبدالمجيد عبدالله خطاك', 'عبدالمجيد عبدالله أول حكايتنا', 'عبدالمجيد عبدالله يا عيونه', 'كاظم الساهر لا يا صديقي', 'كاظم الساهر يا وفية', 'كاظم الساهر بغداد', 'كاظم الساهر تحبني', 'كاظم الساهر إنتهت الحرب', 'ماجد المهندس اعلنها', 'ماجد المهندس الله عليك', 'حسين الجسمي بالسلامة', 'حسين الجسمي سمرية', 'أصالة نصري طلبتك', 'شيرين بحبك من زمان', 'عمرو دياب حبيبي يا نور العين', 'نانسي عجرم يا سلام', 'إليسا يا مرايتي', 'وائل كفوري حبك عذاب', 'رحمة رياض انتي وبس', 'سيف نبيل كل يوم', 'نور الزين يا ريت', 'علي صابر أنت السند', 'حاتم العراقي يا عيني', 'محمد السالم غالي', 'أحمد المصلاوي يا بعد قلبي', 'بلقيس دقوا خبيتي', 'أحلام أحبك موت', 'عبدالمجيد عبدالله تناقض', 'شيرين حبيت', 'إليسا لو فيي', 'عمرو دياب وهي زكريات', 'نانسي عجرم ما تعتذر', 'ماجد المهندس تناديك لايف', 'كاظم الساهر أغازلك', 'حسين الجسمي يا حبيبي', 'أصالة نصري يا مجنون', 'رحمة رياض خلصني', 'سيف نبيل عاشق موت', 'نور الزين أحبك', 'علي صابر شلونك', 'محمد السالم مشتاقلك', 'أحمد المصلاوي أحبك', 'حاتم العراقي أحبك', 'ملحم زين يا غايب', 'بلقيس لا تعليق', 'أحلام تدري ليش لايف', 'عبدالمجيد عبدالله حن الغريب', 'شيرين أغنية مشاعر لايف', 'إليسا كرمالك', 'وائل كفوري حبك عذاب لايف', 'كاظم الساهر زيديني عشقاً أغنية', 'كاظم الساهر أنا وليلى أغنية', 'كاظم الساهر مدرسة الحب أغنية', 'كاظم الساهر هل عندك شك أغنية']

SECTION={
"manager":[("👑 رفع أدمن","role:add:admin"),("➖ تنزيل أدمن","role:del:admin"),("📋 الأدمنية","list:admins"),("📣 تاك للكل","tagall"),("📜 القوانين","rules"),("🔗 الرابط","link"),("👋 الترحيب","welcome_menu"),("🔔 الإشعارات","notify_menu"),("💬 الردود","replies_menu")],
"creator":[("👑 رفع مدير","role:add:manager"),("➖ تنزيل مدير","role:del:manager"),("📋 المدراء","list:manager"),("🏷️ ضع رتبة","setrank"),("⚙️ الإعدادات","settings"),("🛡️ الحماية","menu:protect"),("🧹 التنظيف","menu:clean"),("🎵 الأغاني","music_menu")],
"owner":[("💎 رفع مالك","role:add:owner"),("➖ تنزيل مالك","role:del:owner"),("📋 المالكين","list:owner"),("🧹 تنزيل جميع الرتب","roles:clear"),("🔐 صلاحيات البوت","botperms"),("🗑️ حذف الردود","replies_clear")],
"funny":[("😂 ملك","fun:ملك"),("👸 ملكة","fun:ملكة"),("🤪 أثول","fun:اثول"),("🐄 بقره","fun:بقره"),("🤡 غبي","fun:غبي"),("❤️ نسبة الحب","fun:حب"),("🎁 هدية","fun:هدية"),("🤣 نكتة","fun:نكات"),("✍️ شعر","fun:شعر")],
"fun":[("🎤 غنيلي","fun:غنيلي"),("📝 شعر","fun:شعر"),("💍 زوجني","fun:زوجني"),("💑 زواج","fun:زواج"),("❤️ ثنائي اليوم","fun:ثنائي"),("😂 نكات","fun:نكات"),("🖼️ صورتي","fun:صورتي"),("🎵 بحث أغنية","music_menu")],
"bank":[("💳 حسابي","bank:account"),("💰 فلوسي","bank:money"),("💵 راتب","bank:salary"),("🎲 حظ","bank:luck"),("📈 استثمار","bank:invest"),("🧾 قروضي","bank:debt"),("💎 كنز","bank:treasure"),("💸 تحويل","bank:transfer")],
"clean":[("🧹 مسح 10","clean:10"),("🖼️ مسح الميديا","clean:media"),("✏️ مسح التعديل","clean:edit"),("↪️ مسح التوجيه","clean:forward"),("🔗 مسح الروابط","clean:links"),("🗑️ مسح الكل المتاح","clean:all")],
"games":[("🔀 المختلف","game:different"),("🔄 العكس","game:reverse"),("❓ حزورة","game:riddle"),("🔤 معاني","game:meaning"),("🎯 خمن","game:guess"),("🔢 رياضيات","game:math"),("⭕ XO","game:xo"),("✊ حجر ورق مقص","game:rps"),("🤔 لو خيروك","game:choice"),("🗣️ صراحة","game:truth")],
"developer":[("📊 الإحصائيات","dev:stats"),("🔄 فحص البوت","dev:check"),("📢 إذاعة","dev:broadcast"),("🚫 حظر عام","dev:globalban"),("🧪 فحص الصلاحيات","dev:perms")]
}

def section_kb(cid,sec):
    rows=[]; row=[]
    for text,data in SECTION.get(sec,[]):
        row.append(btn(text,data))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([btn("⬅️ الرئيسية","home")])
    return kb(rows)

TITLE={"protect":"🛡️ أوامر الحماية","admin":"👮 أوامر الأدمن","manager":"👑 أوامر المديرين","creator":"🏗️ أوامر المنشئين","owner":"💎 أوامر المالكين","funny":"😂 أوامر التحشيش","fun":"🎮 أوامر التسلية","bank":"💰 أوامر البنك","clean":"🧹 أوامر التنظيف","games":"🎯 قائمة الألعاب","developer":"🧑‍💻 المطور"}

def show_menu(cid,mid,sec):
    if sec=="protect": return edit(cid,mid,"🛡️ <b>أوامر الحماية</b>\nاضغط على الحماية لتفعيلها/تعطيلها.",protect_kb(cid))
    if sec=="admin":
        text=("👮 <b>قسم الأدمن — أوامر نصية</b>\n\n"
              "⌔︙ <code>قفل الروابط</code> / <code>فتح الروابط</code>\n"
              "⌔︙ <code>حظر</code>، <code>طرد</code>، <code>كتم</code>، <code>الغاء</code> — بالرد على العضو\n"
              "⌔︙ <code>انذار</code> — بالرد على العضو\n"
              "⌔︙ <code>تثبيت</code> / <code>الغاء تثبيت</code> — بالرد على الرسالة\n"
              "⌔︙ <code>رفع ادمن</code> / <code>تنزيل ادمن</code> — بالرد على العضو\n"
              "⌔︙ <code>القوانين</code> — عرض القوانين\n"
              "⌔︙ <code>ضع قوانين نص القوانين</code> — حفظ القوانين\n"
              "⌔︙ <code>الرابط</code> — رابط المجموعة\n"
              "⌔︙ <code>قائمة المنع</code> — عرض الكلمات الممنوعة\n"
              "⌔︙ <code>منع كلمة</code> — إضافة كلمة للقائمة\n"
              "⌔︙ <code>الغاء منع كلمة</code> — حذف كلمة من القائمة\n\n"
              "اكتب الأمر في المجموعة أو استخدم الرد على العضو المطلوب.")
        return edit(cid,mid,text,None)
    return edit(cid,mid,"<b>%s</b>\nكل زر هنا مرتبط بوظيفة حقيقية أو إعداد فعلي."%TITLE.get(sec,sec),section_kb(cid,sec))

# ---------------- Points / bank / roles ----------------
def add_activity(cid,uid):
    run("INSERT INTO points(chat_id,user_id,points,messages) VALUES(?,?,1,1) ON CONFLICT(chat_id,user_id) DO UPDATE SET points=points+1,messages=messages+1",(cid,uid))
    run("INSERT OR IGNORE INTO bank(chat_id,user_id) VALUES(?,?)",(cid,uid))

def role(cid,uid,r): return bool(one("SELECT 1 FROM roles WHERE chat_id=? AND user_id=? AND role=?",(cid,uid,r)))
def set_role(cid,uid,r,on):
    if on: run("INSERT OR IGNORE INTO roles(chat_id,user_id,role) VALUES(?,?,?)",(cid,uid,r))
    else: run("DELETE FROM roles WHERE chat_id=? AND user_id=? AND role=?",(cid,uid,r))

def role_name(r): return {"admin":"أدمن","manager":"مدير","owner":"مالك","special":"مميز","creator":"منشئ","developer":"مطور أساسي","developer2":"مطور ثانوي"}.get(r,r)

# ---------------- Text command engine ----------------
# ---------------- Expanded command layer ----------------
ROLE_ORDER = {"member":0,"special":1,"admin":2,"manager":3,"creator":4,"owner":5,"developer2":6,"developer":7}
PERMS = ("ban","kick","mute","warn","promote","demote","delete","pin")

def custom_rank(cid, uid):
    rows = all_rows("SELECT role FROM roles WHERE chat_id=? AND user_id=?", (cid, uid))
    return max((ROLE_ORDER.get(x["role"], 0) for x in rows), default=0)

def actor_rank(cid, m, isdev=False, iscreator=False, ismod=False):
    uid = (m.get("from") or {}).get("id")
    if isdev:
        return ROLE_ORDER["developer"] + 10
    r = custom_rank(cid, uid) if uid else 0
    if iscreator:
        r = max(r, ROLE_ORDER["creator"])
    if ismod:
        r = max(r, ROLE_ORDER["admin"])
    return r

def target_rank(cid, uid):
    r = custom_rank(cid, uid)
    cm = call("getChatMember", chat_id=cid, user_id=uid)
    if cm.get("ok"):
        st = cm.get("result", {}).get("status")
        if st == "creator": r = max(r, ROLE_ORDER["creator"])
        elif st == "administrator": r = max(r, ROLE_ORDER["admin"])
    return r

def user_meta(cid, uid):
    run("INSERT OR IGNORE INTO user_meta(chat_id,user_id) VALUES(?,?)", (cid,uid))
    return one("SELECT * FROM user_meta WHERE chat_id=? AND user_id=?", (cid,uid))

def command_enabled(cid, cmd):
    r=one("SELECT enabled FROM command_toggles WHERE chat_id=? AND command=?",(cid,cmd))
    return True if r is None else bool(r[0])

def set_command_enabled(cid, cmd, on):
    run("INSERT INTO command_toggles(chat_id,command,enabled) VALUES(?,?,?) ON CONFLICT(chat_id,command) DO UPDATE SET enabled=excluded.enabled",(cid,cmd,int(on)))

def user_from_arg(cid, m, arg=None):
    t=target_from_message(m)
    if t: return t
    if arg:
        arg=arg.strip()
        if arg.startswith('@'):
            rr=call('getChatMember',chat_id=cid,user_id=arg)
            if rr.get('ok'): return rr['result'].get('user')
    if arg and arg.lstrip('-').isdigit():
        rr=call('getChatMember',chat_id=cid,user_id=int(arg))
        if rr.get('ok'): return rr['result'].get('user')
    return None

def promote_member(cid, uid, role_name_ar):
    # Telegram admin promotion is only available to an existing bot admin.
    if role_name_ar in ('admin','ادمن','مشرف'):
        return call('promoteChatMember',chat_id=cid,user_id=uid,can_manage_chat=True,can_delete_messages=True,can_manage_video_chats=True,can_restrict_members=True,can_invite_users=True,can_pin_messages=True,can_change_info=True)
    return {'ok':True}

def demote_member(cid, uid):
    return call('promoteChatMember',chat_id=cid,user_id=uid,can_manage_chat=False,can_delete_messages=False,can_manage_video_chats=False,can_restrict_members=False,can_invite_users=False,can_pin_messages=False,can_change_info=False)

def format_user_info(cid, u):
    if not u: return '❌ لم أجد العضو.'
    r=one('SELECT points,messages FROM points WHERE chat_id=? AND user_id=?',(cid,u['id']))
    rr=call('getChatMember',chat_id=cid,user_id=u['id'])
    status=rr.get('result',{}).get('status','عضو') if rr.get('ok') else 'عضو'
    username='@'+u['username'] if u.get('username') else 'لا يوجد'
    return '👤 <b>معلومات العضو</b>\nالاسم: %s\nالمعرف: <code>%s</code>\nاليوزر: %s\nالرتبة: <b>%s</b>\n⭐ النقاط: <b>%s</b>\n💬 الرسائل: <b>%s</b>'%(mention(u),u['id'],escape(username),escape(status),r['points'] if r else 0,r['messages'] if r else 0)

def send_id_card(cid, user, with_photo=True, reply_to=None):
    """عرض الاسم واليوزر والايدي، ومعها الصورة الشخصية إذا كانت متاحة."""
    if not user or not user.get("id"):
        return send(cid, "❌ لم أستطع تحديد العضو.", reply_to=reply_to)
    uid = user.get("id")
    first = user.get("first_name") or "بدون اسم"
    last = user.get("last_name") or ""
    name = (first + (" " + last if last else "")).strip()
    username = user.get("username")
    uname = "@" + username if username else "لا يوجد معرف"
    # استخدم الكليشة التي اختارها المطوّر بأمر «تغ» فعلياً في بطاقة الايدي.
    try:
        style_index = int(ID_STYLE_INDEX.get(cid, 0))
        template = ID_STYLE_TEMPLATES[style_index % len(ID_STYLE_TEMPLATES)]
        stats = one('SELECT points,messages FROM points WHERE chat_id=? AND user_id=?', (cid, uid))
        msgs = stats['messages'] if stats else 0
        stast = stats['points'] if stats else 0
        caption = template.replace('#username', escape(uname))
        caption = caption.replace('#msgs', str(msgs)).replace('#stast', str(stast))
        caption = caption.replace('#id', str(uid)).replace('#edit', '0').replace('#game', '0')
        caption = caption.replace('⌔︙ هل تريد تعيين هذا الشكل ↯', '').strip()
    except Exception as e:
        print('ID style render error:', repr(e))
        caption = (
            "🪪 <b>معلومات العضو</b>\n\n"
            "👤 الاسم: <b>%s</b>\n"
            "🔹 اليوزر: <b>%s</b>\n"
            "🆔 الايدي: <code>%s</code>"
        ) % (escape(name), escape(uname), uid)
    if with_photo:
        r = call("getUserProfilePhotos", user_id=uid, limit=1)
        photos = r.get("result", {}).get("photos", []) if r.get("ok") else []
        if photos:
            photo = photos[0][-1].get("file_id")
            return call("sendPhoto", chat_id=cid, photo=photo, caption=caption, parse_mode="HTML", reply_to_message_id=reply_to if reply_to else None)
        return send(cid, caption + "\n\n🖼️ لا توجد صورة شخصية.", reply_to=reply_to)
    return send(cid, caption, reply_to=reply_to)

def ensure_user_stats(cid, uid):
    run("INSERT OR IGNORE INTO user_stats(chat_id,user_id,sakkat) VALUES(?,?,1)",(cid,uid))
    return one("SELECT * FROM user_stats WHERE chat_id=? AND user_id=?",(cid,uid))

def feature_on(cid, key):
    return command_toggle(cid, key)

def active_known_users(cid, exclude=None):
    rows=all_rows("SELECT user_id FROM points WHERE chat_id=? ORDER BY messages DESC LIMIT 200",(cid,))
    return [r["user_id"] for r in rows if r["user_id"] != exclude]

def mention_ids(ids):
    return " ".join('<a href="tg://user?id=%s">👤</a>'%int(x) for x in ids)

def warn_buttons(uid):
    return kb([[btn("🔇 كتم","warnact:mute:%s"%uid),btn("🚫 حظر","warnact:ban:%s"%uid)], [btn("👢 طرد","warnact:kick:%s"%uid),btn("↩️ إلغاء","warnact:cancel:%s"%uid)]])

def whisper_to_target(cid, target, body, reply_to=None, sender_id=None):
    # In group: show a deep-link button; the sender writes the secret in the bot's private chat.
    if not target or not target.get("id"):
        return send(cid, "✉️ استخدم أمر همسه بالرد على الشخص المطلوب.", reply_to=reply_to)
    bot = call("getMe").get("result", {}).get("username", "")
    if not bot:
        return send(cid, "❌ تعذر إنشاء زر الهمسة حالياً.", reply_to=reply_to)
    if body:
        # Keep compatibility with "همسه نص" but still guide the user to the private flow.
        if sender_id:
            run("INSERT OR REPLACE INTO whisper_sessions(user_id,target_id,group_id,created_at) VALUES(?,?,?,?)",
                (sender_id, target["id"], cid, int(time.time())))
        return send(cid, "🤫 لإرسال همسة سرية، اضغط الزر واكتب رسالتك في الخاص.", 
                    keyboard=kb([[{"text":"🤫 اضغط هنا لإرسال همسة","url":"https://t.me/%s?start=whisper_%s_%s"%(bot,target["id"],cid)}]]),
                    reply_to=reply_to)
    return send(cid, "🤫 لإرسال همسة سرية، اضغط الزر واكتب رسالتك في الخاص.",
                keyboard=kb([[{"text":"🤫 اضغط هنا لإرسال همسة","url":"https://t.me/%s?start=whisper_%s_%s"%(bot,target["id"],cid)}]]),
                reply_to=reply_to)

def handle_private_whisper(m):
    chat=m.get("chat",{}); uid=(m.get("from") or {}).get("id")
    if chat.get("type") != "private" or not uid:
        return False
    text=(m.get("text") or "").strip()
    if text.startswith("/start"):
        parts=text.split(maxsplit=1)
        payload=parts[1] if len(parts)>1 else ""
        if payload.startswith("whisper_"):
            try:
                _, target_id, group_id = payload.split("_",2)
                target_id=int(target_id); group_id=int(group_id)
                if target_id == uid:
                    send(chat["id"], "🤫 هذا رابط الهمسة الخاص بك؛ ارجع للمجموعة واضغطه من حساب الشخص الذي يريد إرسال الهمسة.")
                    return True
                run("INSERT OR REPLACE INTO whisper_sessions(user_id,target_id,group_id,created_at) VALUES(?,?,?,?)",
                    (uid,target_id,group_id,int(time.time())))
                send(chat["id"], "🤫 اكتب الآن الهمسة السرية التي تريد إرسالها. لن تظهر في المجموعة.")
                return True
            except Exception:
                send(chat["id"], "❌ رابط الهمسة غير صالح.")
                return True
    session=one("SELECT target_id,group_id,created_at FROM whisper_sessions WHERE user_id=?",(uid,))
    if session and text and not text.startswith("/"):
        if int(time.time())-int(session["created_at"]) > 1800:
            run("DELETE FROM whisper_sessions WHERE user_id=?",(uid,))
            send(chat["id"], "⌛ انتهت صلاحية الهمسة. ارجع للمجموعة واضغط الزر مرة ثانية.")
            return True
        target_id=int(session["target_id"])
        sent=send(target_id, "🤫 <b>وصلتك همسة سرية</b>\n\n%s"%escape(text))
        if sent.get("ok"):
            group_id=int(session["group_id"])
            run("INSERT INTO whisper_messages(target_id,group_id,sender_id,body,created_at) VALUES(?,?,?,?,?)", (target_id, group_id, uid, text, int(time.time())))
            secret=one("SELECT id FROM whisper_messages WHERE target_id=? AND group_id=? AND sender_id=? ORDER BY id DESC LIMIT 1", (target_id, group_id, uid))
            if secret:
                send(group_id, "🤫 تم إرسال همسة من %s إلى %s. محتوى الهمسة سري."%(mention(sender_obj), mention({"id":target_id,"first_name":"المستلم"})), keyboard=kb([[btn("👁 عرض الرسالة", "whisper:view:%s"%secret["id"])] ]))
            run("DELETE FROM whisper_sessions WHERE user_id=?",(uid,))
            send(chat["id"], "✅ تم إرسال همستك بشكل خاص.")
        else:
            send(chat["id"], "🔒 ما أگدر أرسلها بعد؛ لازم الشخص يفتح البوت بالخاص ويضغط Start أولاً، وبعدها أعد إرسال الهمسة.")
        return True
    return False

def advanced_command(m):
    chat=m.get('chat',{}); cid=chat.get('id'); uid=m.get('from',{}).get('id'); text=(m.get('text') or '').strip()
    if not cid or not text: return False
    if chat.get('type') not in ('group','supergroup'):
        # General user commands still work in private chat.
        pass
    parts=text.split(maxsplit=2); raw=parts[0].lstrip('/'); cmd=raw.lower(); arg1=parts[1] if len(parts)>1 else ''; rest=parts[2] if len(parts)>2 else ''
    target=target_from_message(m)
    # الرتب الممنوحة داخل البوت تمنح صلاحياتها تلقائياً، مع بقاء مطوّر النظام محمياً باسم المستخدم.
    assigned_rank = custom_rank(cid, uid) if uid else 0
    ismod = is_admin(cid,uid) or assigned_rank >= ROLE_ORDER['admin']
    iscreator = is_creator(cid,uid) or assigned_rank >= ROLE_ORDER['creator']
    isdev=(m.get('from',{}).get('username','').lower()==DEVELOPER.lower())

    # تشغيل/إيقاف بطاقة الايدي بالصورة من أوامر قصيرة أو كاملة
    toggle_text = " ".join((text or "").strip().lower().split())
    if toggle_text in ("تفع", "تفعيل الايدي بالصوره", "تفعيل الايدي بالصورة", "تفعيل صوره الايدي", "تفعيل صورة الايدي"):
        if not (ismod or iscreator or isdev):
            send(cid, "❌ هذا الأمر للمشرفين فقط.", reply_to=m.get("message_id")); return True
        set_command_toggle(cid, "id_photo", True)
        send(cid, "✅ تم تفعيل أمر الايدي بالصورة.", reply_to=m.get("message_id")); return True
    if toggle_text in ("تعط", "تعطيل الايدي بالصوره", "تعطيل الايدي بالصورة", "تعطيل صوره الايدي", "تعطيل صورة الايدي"):
        if not (ismod or iscreator or isdev):
            send(cid, "❌ هذا الأمر للمشرفين فقط.", reply_to=m.get("message_id")); return True
        set_command_toggle(cid, "id_photo", False)
        send(cid, "🔴 تم تعطيل أمر الايدي بالصورة.", reply_to=m.get("message_id")); return True

    # compact aliases requested by user
    alias={'ا':'ايدي','م':'رفع مميز','اد':'رفع ادمن','مد':'رفع مدير','من':'رفع منشئ','اس':'رفع منشئ اساسي','مط':'رفع مطور','ثانوي':'رفع مطور ثانوي','تك':'تنزيل الكل','تعط':'تعطيل الايدي بالصوره','تفع':'تفعيل الايدي بالصوره','تغ':'تغيير الايدي','تنز':'تنزيل جميع الرتب','قق':'قفل الاشعارات','فف':'فتح الاشعارات','ر':'الرابط','رر':'الردود','ث':'تثبيت','ك':'كشف','تت':'تاك','تكك':'تاك للكل','رف':'رفع القيود','الغ':'الغاء حظر','مر':'مسح رد','رد':'اضف رد','امر':'اضف امر','مس':'مسح سحكاتي','رس':'مسح رسائلي','غ':'غنيلي','غغ':'اغنيه','ش':'شعر','ق':'قصيده','ن':'نقاطي','س':'اسالني','ل':'لغز','مع':'معاني','ح':'حزوره','ص':'صورتي','ند':'نداء','مي':'ميوزك'}
    if cmd in alias:
        cmd=alias[cmd]
        if cmd in ('رفع مميز','رفع ادمن','رفع مدير','رفع منشئ','رفع منشئ اساسي','رفع مطور','رفع مطور ثانوي','تنزيل الكل'):
            pass

    # ID photo toggle commands
    if cmd in ("تعطيل ايدي", "تعطيل الآيدي", "تعطيل الايدي", "تعطيل ايدي بالصوره", "تعطيل ايدي بالصورة",
               "تفعيل ايدي", "تفعيل الآيدي", "تفعيل الايدي", "تفعيل ايدي بالصوره", "تفعيل ايدي بالصورة"):
        if not (ismod or iscreator or isdev):
            return bool(send(cid, "❌ هذا الأمر للمشرفين فقط.", reply_to=m.get("message_id")))
        enabled = cmd.startswith("تفعيل")
        set_command_toggle(cid, "id_photo", enabled)
        return bool(send(cid, "✅ تم تفعيل الآيدي بالصورة." if enabled else "✅ تم تعطيل صورة الآيدي؛ أمر ايدي النصي يبقى متاحاً.", reply_to=m.get("message_id")))

    if cmd in ("زوجي", "زوجتي"):
        run("CREATE TABLE IF NOT EXISTS marriages(chat_id INTEGER NOT NULL,user_id INTEGER NOT NULL,partner_id INTEGER NOT NULL,created_at INTEGER,PRIMARY KEY(chat_id,user_id))")
        pair = one("SELECT partner_id FROM marriages WHERE chat_id=? AND user_id=?", (cid, uid))
        if not pair:
            return bool(send(cid, "💔 ما عندك زواج مسجل. اكتب زوجني حتى يختار لك البوت عضواً عشوائياً.", reply_to=m.get("message_id")))
        rr = call("getChatMember", chat_id=cid, user_id=int(pair["partner_id"]))
        partner = (rr.get("result", {}).get("user") or {}) if rr.get("ok") else {"id": int(pair["partner_id"]), "first_name": "الشريك"}
        return bool(send(cid, "💍 %s: %s" % ("زوجك" if cmd=="زوجي" else "زوجتك", mention(partner)), reply_to=m.get("message_id")))

    if cmd == "نزلني":
        rows = all_rows("SELECT role FROM roles WHERE chat_id=? AND user_id=?", (cid, uid))
        protected = [r["role"] for r in rows if r["role"] in ("owner", "developer", "developer2")]
        if protected:
            return bool(send(cid, "🛡️ هاي رتبة محمية وما تگدر تنزلها بأمر نزلني. راجع المالك الأساسي أو المطور الأساسي.", reply_to=m.get("message_id")))
        if not rows:
            return bool(send(cid, "ℹ️ ما عندك رتبة داخل البوت حتى تنزلها.", reply_to=m.get("message_id")))
        top = max(rows, key=lambda r: ROLE_ORDER.get(r["role"],0))["role"]
        set_role(cid, uid, top, False)
        return bool(send(cid, "✅ تم تنزيل رتبتك: <b>%s</b>." % escape(role_name(top)), reply_to=m.get("message_id")))

    # identity / member information
    if cmd in ("ايدي", "id", "ايدي بالرد", "ايدي بالصورة", "ايدي بالصوره"):
        if not command_toggle(cid, "id_photo"):
            send(cid, "🔴 ايدي بالصورة معطل من إعدادات الأدمن.", reply_to=m.get("message_id")); return True
        u=target or m.get("from")
        return bool(send_id_card(cid, u, True, m.get("message_id")))
    if cmd in ("ايدي بدون صورة", "ايدي بدون صوره", "ايدي نص", "ايدي بدون"):
        if not command_toggle(cid, "id_plain"):
            send(cid, "🔴 ايدي بدون صورة معطل من إعدادات الأدمن.", reply_to=m.get("message_id")); return True
        u=target or m.get("from")
        return bool(send_id_card(cid, u, False, m.get("message_id")))
    if cmd in ('صورتي','صورته'):
        if not feature_on(cid,'my_photo'): return bool(send(cid,'🔴 صورتي معطلة من إعدادات الأدمن.',reply_to=m.get('message_id')))
        u=target or m.get('from'); rr=call('getUserProfilePhotos',user_id=u.get('id'),limit=1); photos=rr.get('result',{}).get('photos',[]) if rr.get('ok') else []
        if not photos: return bool(send(cid,'🖼️ ما عنده صورة حساب متاحة.',reply_to=m.get('message_id')))
        return bool(call('sendPhoto',chat_id=cid,photo=photos[0][-1]['file_id'],caption='🖼️ صورة %s'%escape(u.get('first_name') or 'العضو'),parse_mode='HTML',reply_to_message_id=m.get('message_id')))
    if cmd in ('جمالي','تقييم جمالي','جمال'):
        if not feature_on(cid,'image'): return bool(send(cid,'🔴 تقييم الجمال معطل.',reply_to=m.get('message_id')))
        return bool(send(cid,'✨ تقييم جمال %s: <b>%s%%</b> 😎'%(mention(target or m.get('from')),random.randint(1,100)),reply_to=m.get('message_id')))
    if cmd in ('انشاء','الانشاء','انشاء حساب'):
        u=m.get('from'); ensure_user_stats(cid,u['id']); bank_row(cid,u['id']); r=one('SELECT messages,points FROM points WHERE chat_id=? AND user_id=?',(cid,u['id'])); st=one('SELECT sakkat FROM user_stats WHERE chat_id=? AND user_id=?',(cid,u['id']))
        return bool(send(cid,'✅ تم إنشاء حسابك.\n👤 الاسم: %s\n🆔 الايدي: <code>%s</code>\n💬 الرسائل: <b>%s</b>\n😄 السحكات: <b>%s</b>\n⭐ النقاط: <b>%s</b>'%(mention(u),u['id'],r['messages'] if r else 0,st['sakkat'] if st else 1,r['points'] if r else 0),reply_to=m.get('message_id')))
    if cmd in ('مسح سحكاتي','مسح السحكات'):
        ensure_user_stats(cid,uid); run('UPDATE user_stats SET sakkat=0 WHERE chat_id=? AND user_id=?',(cid,uid)); return bool(send(cid,'🧹 تم مسح السحكات.',reply_to=m.get('message_id')))
    if cmd in ('اضف سحكات','اضف سحكة') and (iscreator or isdev):
        u=target or user_from_arg(cid,m,arg1); n=int(arg1 or 0) if arg1.isdigit() else 0
        if not u or n<=0: return bool(send(cid,'الاستخدام: اضف سحكات 5 بالرد'))
        ensure_user_stats(cid,u['id']); run('UPDATE user_stats SET sakkat=sakkat+? WHERE chat_id=? AND user_id=?',(n,cid,u['id'])); return bool(send(cid,'✅ تمت إضافة %s سحكات.'%n))
    if cmd in ('همسه','همسة'):
        if not feature_on(cid,'whisper'): return bool(send(cid,'🔴 الهمسة معطلة.',reply_to=m.get('message_id')))
        return bool(whisper_to_target(cid,target,(arg1+' '+rest).strip(),m.get('message_id'),uid))
    if cmd in ('كول','قول'):
        if not feature_on(cid,'call'): return bool(send(cid,'🔴 كول معطل.',reply_to=m.get('message_id')))
        phrase=(arg1+' '+rest).strip(); u=m.get('from',{})
        if phrase in ('اسمي','اسمي؟'): out='👤 اسمي هو: <b>%s</b>'%escape(u.get('first_name') or 'عضو')
        elif phrase in ('معرفي','يوزري'): out='🔹 معرفي: <b>%s</b>'%escape('@'+u['username'] if u.get('username') else 'لا يوجد')
        elif phrase in ('ايدي','آيدي'): out='🆔 ايدي: <code>%s</code>'%u.get('id')
        elif phrase in ('رسائلي','رسائلي؟'):
            r=one('SELECT messages FROM points WHERE chat_id=? AND user_id=?',(cid,u.get('id'))); out='💬 عدد رسائلي: <b>%s</b>'%(r['messages'] if r else 0)
        elif phrase in ('سحكاتي','سحكاتي؟'):
            st=ensure_user_stats(cid,u.get('id')); out='😄 سحكاتي: <b>%s</b>'%st['sakkat']
        else: out='🗣️ %s'%escape(phrase or 'اكتب الشيء بعد كول.')
        return bool(send(cid,out,reply_to=m.get('message_id')))
    if cmd in ('نداء','نادي'):
        if not feature_on(cid,'auto_call'): return bool(send(cid,'🔴 نداء معطل.',reply_to=m.get('message_id')))
        ids=active_known_users(cid,uid)
        if not ids: return bool(send(cid,'❌ لا توجد أسماء محفوظة.'))
        chosen=random.choice(ids); rr=call('getChatMember',chat_id=cid,user_id=chosen); u=rr.get('result',{}).get('user',{'id':chosen}) if rr.get('ok') else {'id':chosen}
        return bool(send(cid,'📢 نداء: %s'%mention(u),reply_to=m.get('message_id')))
    if cmd in ('تاك عام','all','تاك للكل'):
        if not feature_on(cid,'auto_tag'): return bool(send(cid,'🔴 التاك العام معطل.',reply_to=m.get('message_id')))
        ids=active_known_users(cid,uid)
        return bool(send(cid,'📣 <b>تاك عام</b>\n'+(mention_ids(ids) if ids else 'لا توجد أسماء محفوظة.'),reply_to=m.get('message_id')))
    if cmd in ('معرفي','يوزري','رابطي','اسمي','اسمي؟'):
        u=m.get('from',{}); username='@'+u['username'] if u.get('username') else 'لا يوجد'; link='tg://user?id=%s'%u.get('id'); send(cid,'👤 الاسم: <b>%s</b>\n🔹 المعرف: <code>%s</code>\n🔗 %s'%(escape(u.get('first_name','')),escape(username),link),reply_to=m.get('message_id')); return True
    if cmd in ('معلوماتي','كشف','كشف عام','كشفه'):
        send(cid,format_user_info(cid,target or m.get('from')),reply_to=m.get('message_id')); return True
    if cmd in ('صلاحياتي','صلاحياته','رتبتي','الرتبه','صلاحيات المجموعه','صلاحيات المشرفين'):
        u=target or m.get('from'); rr=call('getChatMember',chat_id=cid,user_id=u.get('id')); x=rr.get('result',{}); send(cid,'🔐 <b>الصلاحيات</b>\nالحالة: <b>%s</b>\nإدارة المجموعة: %s\nحذف: %s\nتقييد: %s\nدعوات: %s\nتثبيت: %s'%(x.get('status','عضو'),'✅' if x.get('can_manage_chat') else '❌','✅' if x.get('can_delete_messages') else '❌','✅' if x.get('can_restrict_members') else '❌','✅' if x.get('can_invite_users') else '❌','✅' if x.get('can_pin_messages') else '❌')); return True
    if cmd in ('رسائلي','تفاعلي','تفاعله','سحكاتي','جهاتي','نقاطي'):
        u=target or m.get('from'); r=one('SELECT points,messages FROM points WHERE chat_id=? AND user_id=?',(cid,u['id'])); meta=user_meta(cid,u['id']); st=ensure_user_stats(cid,u['id']); send(cid,'📊 <b>%s</b>\n💬 الرسائل: <b>%s</b>\n⭐ النقاط: <b>%s</b>\n❤️ التفاعل: <b>%s</b>\n📇 الجهات: <b>%s</b>\n😄 السحكات: <b>%s</b>'%(escape(cmd),r['messages'] if r else 0,r['points'] if r else 0,meta['likes'] if meta else 0,0,st['sakkat'] if st else 1)); return True
    if cmd in ('بايو','نبذه'):
        u=target or m.get('from'); meta=user_meta(cid,u['id']); send(cid,'📝 <b>النبذة</b>\n'+escape(meta['bio'] or 'لا توجد نبذة محفوظة.')); return True
    if cmd in ('لقبي','لقبه'):
        u=target or m.get('from'); meta=user_meta(cid,u['id']); send(cid,'🏷️ اللقب: <b>%s</b>'%escape(meta['nickname'] or 'لا يوجد')); return True
    if cmd in ('ضع لقب','ضع لقب') and (ismod or iscreator):
        u=target or user_from_arg(cid,m,arg1); title=rest or arg1
        if not u or not title: return bool(send(cid,'الاستخدام: ضع لقب اسم اللقب بالرد'))
        user_meta(cid,u['id']); run('UPDATE user_meta SET nickname=? WHERE chat_id=? AND user_id=?',(title,cid,u['id'])); send(cid,'✅ تم وضع اللقب لـ %s'%mention(u)); return True
    if cmd in ('زخرفه','زخرفة'):
        s=rest or arg1 or m.get('from',{}).get('first_name','')
        if not s: return True
        send(cid,'✨ '+ ' '.join(s) + '\n✨ '+s.upper()); return True
    if cmd in ('الوقت','الساعه','الساعة','التاريخ'):
        send(cid,'🕒 %s'%datetime.now().strftime('%Y-%m-%d %H:%M:%S')); return True

    # group data / setup
    if cmd in ('اسم','ضع اسم') and ismod:
        name=rest or arg1
        if name:
            r=call('setChatTitle',chat_id=cid,title=name); send(cid,'✅ تم تغيير اسم المجموعة.' if r.get('ok') else '❌ تعذر تغيير الاسم.'); return True
    if cmd in ('وصف','ضع وصف') and ismod:
        desc=rest or arg1; r=call('setChatDescription',chat_id=cid,description=desc); send(cid,'✅ تم تغيير وصف المجموعة.' if r.get('ok') else '❌ تعذر تغيير الوصف.'); return True
    if cmd in ('الرابط','انشاء رابط','انشاء رابط انضمام'):
        r=call('exportChatInviteLink',chat_id=cid); send(cid,'🔗 '+(r.get('result') if r.get('ok') else '❌ لا يمكن إنشاء الرابط.')); return True
    if cmd in ('مسح الرابط',):
        send(cid,'ℹ️ تيليجرام لا يوفر حذف رابط الدعوة الأساسي، ويمكن إلغاء/تغيير روابط الدعوة من إعدادات المجموعة.'); return True
    if cmd=='القوانين':
        send(cid,'📜 <b>القوانين</b>\n'+(settings(cid)['rules'] or 'لا توجد قوانين.')); return True
    if cmd in ('ضع قوانين','قوانين') and ismod:
        rule_parts=text.split(None,2)
        if len(rule_parts)<3 or not rule_parts[2].strip():
            send(cid,'اكتب القوانين بعد الأمر، مثال: ضع قوانين احترام الجميع.'); return True
        val=rule_parts[2]; set_setting(cid,'rules',val); send(cid,'✅ تم حفظ القوانين.'); return True
    if cmd in ('ترحيب','الترحيب'):
        if not ismod: send(cid,'❌ للمشرفين فقط.'); return True
        on=not bool(settings(cid)['welcome']); set_setting(cid,'welcome',int(on)); send(cid,'👋 الترحيب: <b>%s</b>'%('مفعل' if on else 'متوقف')); return True
    if cmd in ('ضع ترحيب','الترحيب نص') and ismod:
        val=rest or arg1; set_setting(cid,'welcome_text',val); set_setting(cid,'welcome',1); send(cid,'✅ تم حفظ رسالة الترحيب.'); return True

    # protection locks including lock mode
    if cmd in ('قفل','فتح'):
        p=text.split(maxsplit=2)
        if len(p)<2: send(cid,'الاستخدام: قفل الروابط أو فتح الروابط'); return True
        k=ALIASES.get(p[1].lower());
        if not k: send(cid,'❌ نوع الحماية غير معروف.'); return True
        if not ismod: send(cid,'❌ للمشرفين فقط.'); return True
        on=cmd=='قفل'; mode=action_for(cid,k); set_prot(cid,k,on,mode); send(cid,('🔒 تم قفل ' if on else '🔓 تم فتح ')+PROT[k]); return True
    if cmd in ('بالتقييد','بالطرد','بالكتم') and ismod:
        mode={'بالتقييد':'mute','بالطرد':'kick','بالكتم':'mute'}[cmd]
        # apply mode to all currently configured protections
        rows=all_rows('SELECT key FROM protection WHERE chat_id=?',(cid,))
        for r in rows: set_prot(cid,r['key'],True,mode)
        send(cid,'⚙️ تم ضبط طريقة الحماية: <b>%s</b>'%cmd); return True

    # moderation / roles
    role_cmds={
        'مميز':'special','مميزين':'special',
        'مدير':'manager','مالك':'owner',
        'منشئ':'creator','منشى':'creator','منشئ اساسي':'creator','منشئ أساسي':'creator','منشئ_اساسي':'creator','منشى اساسي':'creator','منشى أساسي':'creator',
        'ادمن':'admin','أدمن':'admin','ادمِن':'admin','مشرف':'admin',
        'مطور':'developer','مطور اساسي':'developer','مطور أساسي':'developer','مطور_اساسي':'developer','مطور_أساسي':'developer',
        'مطور ثانوي':'developer2','مطور_ثانوي':'developer2'
    }
    role_arg = (arg1 + (' ' + rest.split()[0] if arg1 in ('منشئ','منشى','مطور') and rest else '')).strip()
    role_arg = role_arg.replace('أ','ا').replace('_',' ').strip()
    role_arg = {'منشى':'منشئ','منشى اساسي':'منشئ اساسي','مطور اساسي':'مطور اساسي','مطور ثانوي':'مطور ثانوي','ادمن':'ادمن','مميزين':'مميز'}.get(role_arg, role_arg)
    if cmd in ('رفع','تنزيل') and role_arg in role_cmds:
        u=target or user_from_arg(cid,m,None)
        rr=role_cmds[role_arg]
        if not u:
            send(cid,'⚠️ لازم ترد على رسالة العضو أولاً، ثم اكتب الأمر مثلاً: <code>رفع مميز</code> أو <code>رفع مطور أساسي</code>.')
            return True
        on=cmd=='رفع'
        # رتبة البوت المخصصة تخضع للتدرج: لا ترفع رتبة مساوية أو أعلى من رتبة الآمر.
        rank_map = {"special":1, "admin":2, "manager":3, "creator":4, "owner":5, "developer2":6, "developer":7}
        wanted_rank = rank_map.get(rr, 0)
        my_rank = actor_rank(cid, m, isdev=isdev, iscreator=iscreator, ismod=ismod)
        their_rank = target_rank(cid, u["id"])
        if on:
            if my_rank <= wanted_rank or my_rank <= their_rank:
                send(cid,'❌ ليس لديك صلاحية. لا يمكنك منح رتبة مساوية لرتبتك أو أعلى منها، ولا رفع عضو أعلى منك.')
                return True
        elif my_rank <= their_rank and not isdev:
            send(cid,'❌ ليس لديك صلاحية لتنزيل رتبة مساوية لرتبتك أو أعلى منها.')
            return True
        if not ismod and not iscreator and not isdev and my_rank <= 0:
            send(cid,'❌ ليس لديك صلاحية لمنح الرتب.')
            return True
        if rr=='admin': res=promote_member(cid,u['id'],'admin') if on else demote_member(cid,u['id'])
        else: res={'ok':True}; set_role(cid,u['id'],rr,on)
        if res.get('ok'):
            person = mention(u)  # رابط مباشر لحساب الشخص المرفوع
            rank_label = escape(role_name(rr))
            action_label = 'تم رفعه إلى رتبة' if on else 'تم تنزيله من رتبة'
            extra = '\\nℹ️ هذه رتبة داخل البوت وليست صلاحية أدمن في Telegram.' if rr != 'admin' else ''
            notice = (
                '👤 المستخدم: ' + person + '\n'
                '⭐ ' + action_label + ': <b>' + rank_label + '</b>'
            )
            send(cid, notice)
        else:
            send(cid,'❌ فشل: '+escape(str(res.get('description',''))))
        return True
    if cmd in ('رفع','تنزيل') and target:
        if arg1 in ('مميز','ادمن','مدير','مالك','منشئ','مشرف'):
            return True
    if cmd in ('حظر','طرد','كتم','تقييد','الغاء حظر','الغاء كتم','الغاء تقييد','انذار'):
        # handled by original engine too, but support username/id arguments here.
        if not ismod: send(cid,'❌ للمشرفين فقط.'); return True
        u=target or user_from_arg(cid,m,arg1)
        if not u: send(cid,'⚠️ استخدم الأمر بالرد أو بالمعرف.'); return True
        if not can_target(cid,u['id']): send(cid,'❌ لا يمكن تنفيذ الأمر على مشرف.'); return True
        act={'حظر':ban,'طرد':kick,'كتم':mute,'تقييد':mute,'الغاء حظر':lambda c,i:call('unbanChatMember',chat_id=c,user_id=i),'الغاء كتم':unmute,'الغاء تقييد':unmute}.get(cmd)
        if act: r=act(cid,u['id']); send(cid,'✅ تم تنفيذ %s على %s'%(cmd,mention(u)) if r.get('ok') else '❌ '+escape(str(r.get('description','')))); return True
        row=one('SELECT count FROM warnings WHERE chat_id=? AND user_id=?',(cid,u['id'])); n=(row['count'] if row else 0)+1; run('INSERT INTO warnings(chat_id,user_id,count) VALUES(?,?,?) ON CONFLICT(chat_id,user_id) DO UPDATE SET count=excluded.count',(cid,u['id'],n));
        if n==1: send(cid,'⚠️ تم إنذار %s. <b>1/2</b>'%mention(u)); return True
        send(cid,'⚠️ الإنذار الثاني لـ %s\nاختر الإجراء:'%mention(u),warn_buttons(u['id']),m.get('message_id')); return True
    if cmd in ('كشف البوتات','قفل البوتات','البوتات') and ismod:
        admins=call('getChatAdministrators',chat_id=cid); bots=[]
        for a in admins.get('result',[]):
            if a.get('user',{}).get('is_bot'): bots.append(a['user'])
        if cmd=='قفل البوتات':
            send(cid,'ℹ️ لا يمكن حظر بوتات الإدارة التي تحتاجها. البوتات العادية تُحذف عند دخولها إذا كان البوت يتلقى حدث الانضمام.')
        else: send(cid,'🤖 البوتات: '+(', '.join('@'+x.get('username','') for x in bots) if bots else 'لا توجد بوتات ظاهرة.'))
        return True

    # lists / stats / roles
    if cmd in ('المدراء','المالكين','المنشئين','المنشئين الاساسيين','المميزين','المشرفين','المكتومين','المحظورين'):
        rr={'المدراء':'manager','المالكين':'owner','المنشئين':'creator','المنشئين الاساسيين':'creator','المميزين':'special'}.get(cmd)
        if rr:
            rows=all_rows('SELECT user_id FROM roles WHERE chat_id=? AND role=?',(cid,rr)); send(cid,'📋 <b>%s</b>\n%s'%(cmd,'\n'.join('<code>%s</code>'%x['user_id'] for x in rows) if rows else 'لا توجد قائمة.')); return True
        if cmd=='المكتومين':
            rows=all_rows('SELECT user_id FROM warnings WHERE chat_id=? AND count>=3',(cid,)); send(cid,'🔇 المكتومين: '+(' '.join('<code>%s</code>'%x['user_id'] for x in rows) if rows else 'لا يوجد')); return True
    if cmd=='تنزيل جميع الرتب' and (iscreator or isdev):
        run('DELETE FROM roles WHERE chat_id=?',(cid,)); send(cid,'🧹 تم مسح الرتب المخصصة.'); return True

    # custom replies and commands
    if cmd in ('اضف رد','أضف رد'):
        if len(parts)<3: send(cid,'الاستخدام: اضف رد الكلمة | الرد'); return True
        trig,rep=(rest.split('|',1)+[''])[:2]
        if not rep: send(cid,'الاستخدام: اضف رد الكلمة | الرد'); return True
        run('INSERT OR REPLACE INTO custom_replies(chat_id,trigger,reply) VALUES(?,?,?)',(cid,trig.strip().lower(),rep.strip())); send(cid,'✅ تمت إضافة الرد.'); return True
    if cmd in ('مسح رد','احذف رد'):
        trig=arg1.lower(); run('DELETE FROM custom_replies WHERE chat_id=? AND trigger=?',(cid,trig)); send(cid,'🗑️ تم مسح الرد.'); return True
    if cmd in ('الردود','قائمة الردود'):
        rows=all_rows('SELECT trigger,reply FROM custom_replies WHERE chat_id=? ORDER BY trigger',(cid,)); send(cid,'💬 <b>الردود</b>\n'+('\n'.join('• %s ← %s'%(escape(x['trigger']),escape(x['reply'])) for x in rows) if rows else 'لا توجد ردود.')); return True
    if cmd=='مسح الردود' and ismod:
        run('DELETE FROM custom_replies WHERE chat_id=?',(cid,)); send(cid,'🗑️ تم مسح الردود.'); return True
    if cmd in ('اضف امر','أضف امر') and ismod:
        if len(parts)<3: send(cid,'الاستخدام: اضف امر الامر | الرد'); return True
        trig,rep=(rest.split('|',1)+[''])[:2]; run('INSERT OR REPLACE INTO custom_commands(chat_id,command,reply) VALUES(?,?,?)',(cid,trig.strip().lower(),rep.strip())); send(cid,'✅ تم إضافة الأمر.'); return True

    # toggles
    if cmd in ('تفعيل','تعطيل'):
        name=(arg1 or rest).strip();
        if not name: send(cid,'الاستخدام: تفعيل الترحيب'); return True
        if name in ('الترحيب','الرابط','التحقق','الالعاب','التحشيش','منشن','النداء','غنيلي','شعر','قصيده','الردود','الابراج','التفاعل','تيكتوك','يوتيوب','البنك','الميديا','امسح','المسح التلقائي','المنظف التلقائي','الاذكار','الاقتباس'):
            if not ismod: send(cid,'❌ للمشرفين فقط.'); return True
            on=cmd=='تفعيل'; set_command_enabled(cid,name,on)
            if name=='الترحيب': set_setting(cid,'welcome',int(on))
            send(cid,'⚙️ %s <b>%s</b>: %s'%(cmd,name,'مفعل' if on else 'معطل')); return True

    # cleaning commands
    if cmd in ('مسح','امسح','نظف'):
        if not ismod: send(cid,'❌ للمشرفين فقط.'); return True
        n=10
        if arg1.isdigit(): n=min(100,int(arg1))
        r=m.get('reply_to_message')
        if r: delete(cid,r['message_id']); delete(cid,m['message_id']); return True
        count=clean_tracked(cid,None,n); send(cid,'🧹 تم مسح <b>%s</b> رسالة.'%count); return True
    if cmd in ('مسح الميديا','الميديا') and ismod:
        n=clean_tracked(cid,'media',100); send(cid,'🖼️ تم مسح %s.'%n); return True
    if cmd in ('مسح الروابط','الروابط') and ismod:
        n=clean_tracked(cid,'links',100); send(cid,'🔗 تم مسح %s.'%n); return True

    # tag commands
    if cmd in ('تاك','منشن'):
        if target: send(cid,'📣 %s'%mention(target)); return True
        send(cid,'📣 استخدم تاك بالرد على العضو.'); return True
    if cmd in ('تاك للكل','all','نداء للكل'):
        rows=all_rows('SELECT user_id FROM points WHERE chat_id=? ORDER BY points DESC LIMIT 50',(cid,)); send(cid,'📣 <b>نداء للكل</b>\n'+' '.join('<a href="tg://user?id=%s">•</a>'%r['user_id'] for r in rows)); return True
    if cmd in ('اضف تاك','مسح تاك') and ismod:
        if not target: send(cid,'استخدم الأمر بالرد.'); return True
        name=arg1 or 'افتراضي';
        if cmd=='اضف تاك': run('INSERT OR IGNORE INTO tags(chat_id,tag_name,user_id) VALUES(?,?,?)',(cid,name,target['id']))
        else: run('DELETE FROM tags WHERE chat_id=? AND tag_name=? AND user_id=?',(cid,name,target['id']))
        send(cid,'✅ تم.'); return True

    # points selling / admin adjustments
    if cmd=='بيع نقاطي' and arg1.isdigit():
        n=int(arg1); r=one('SELECT points FROM points WHERE chat_id=? AND user_id=?',(cid,uid)); have=r['points'] if r else 0
        if n<=0 or n>have: send(cid,'❌ عدد النقاط غير صحيح.'); return True
        gain=n*50; run('UPDATE points SET points=points-? WHERE chat_id=? AND user_id=?',(n,cid,uid)); bank_row(cid,uid); run('UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?',(gain,cid,uid)); send(cid,'💰 بعت <b>%s</b> نقطة مقابل <b>%s</b>.'%(n,gain)); return True
    if cmd in ('اضف نقاط','اضف رسائل') and (iscreator or isdev):
        u=target; amount=int(arg1) if arg1.isdigit() else 0
        if not u or amount<=0: send(cid,'استخدم بالرد: اضف نقاط 100'); return True
        run('INSERT INTO points(chat_id,user_id,points,messages) VALUES(?,?,?,0) ON CONFLICT(chat_id,user_id) DO UPDATE SET points=points+excluded.points',(cid,u['id'],amount)); send(cid,'✅ تمت إضافة النقاط.'); return True

    # bank extensions
    if cmd in ('استثمار','مضاربه','حظ','مراهنه','اكشط') and arg1.isdigit():
        amount=int(arg1); r=bank_row(cid,uid)
        if amount<=0 or r['money']<amount: send(cid,'❌ رصيدك لا يكفي.'); return True
        if cmd=='استثمار': change=int(amount*random.uniform(-.25,.6))
        elif cmd=='مضاربه': change=int(amount*random.uniform(-.5,.9))
        elif cmd=='حظ': change=amount if random.random()<.5 else -amount
        elif cmd=='مراهنه': change=amount*2 if random.random()<.35 else -amount
        else: change=random.randint(0,amount*3)
        run('UPDATE bank SET money=MAX(0,money+?) WHERE chat_id=? AND user_id=?',(change,cid,uid)); send(cid,('🟢 ربح' if change>=0 else '🔴 خسارة')+' <b>%s</b>.'%abs(change)); return True
    if cmd in ('حسابه','فلوسه'):
        u=target or user_from_arg(cid,m,arg1)
        if not u: send(cid,'استخدم بالرد.'); return True
        r=bank_row(cid,u['id']); send(cid,'💰 رصيد %s: <b>%s</b>'%(mention(u),r['money'])); return True
    if cmd=='سرقه' and target:
        r=bank_row(cid,target['id']); mine=bank_row(cid,uid); amount=min(r['money'],random.randint(50,300)); run('UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?',(amount,cid,uid)); run('UPDATE bank SET money=money-? WHERE chat_id=? AND user_id=?',(amount,cid,target['id'])); send(cid,'🕵️ سرقت <b>%s</b> من %s.'%(amount,mention(target))); return True
    if cmd=='قرض':
        r=bank_row(cid,uid); amount=min(2000,1000); run('UPDATE bank SET money=money+?,debt=debt+? WHERE chat_id=? AND user_id=?',(amount,amount,cid,uid)); send(cid,'🏦 أخذت قرض <b>%s</b>.'%amount); return True
    if cmd in ('تسديد القرض','تسديد القرض') and arg1.isdigit():
        amount=int(arg1); r=bank_row(cid,uid); amount=min(amount,r['debt'],r['money']); run('UPDATE bank SET money=money-?,debt=debt-? WHERE chat_id=? AND user_id=?',(amount,amount,cid,uid)); send(cid,'🏦 تم تسديد <b>%s</b>.'%amount); return True

    # developer-only controls and broadcast to saved groups
    if isdev and cmd in ('احصائيات','الاحصائيات'):
        r=one('SELECT COUNT(*) n FROM known_chats'); u=one('SELECT COUNT(DISTINCT user_id) n FROM points'); send(cid,'📊 المجموعات: <b>%s</b>\n👥 المستخدمون: <b>%s</b>'%(r['n'],u['n'])); return True
    if isdev and cmd in ('حظر عام','الغاء حظر عام'):
        u=target or user_from_arg(cid,m,arg1)
        if not u: send(cid,'استخدم بالرد أو المعرف.'); return True
        if cmd=='حظر عام': run('INSERT OR IGNORE INTO global_bans(user_id) VALUES(?)',(u['id'],)); send(cid,'🚫 تمت إضافة العضو للحظر العام.')
        else: run('DELETE FROM global_bans WHERE user_id=?',(u['id'],)); send(cid,'✅ تم رفع الحظر العام.')
        return True
    if isdev and cmd in ('اذاعه','إذاعة'):
        body=rest or arg1
        if not body: send(cid,'استخدم: اذاعه نص'); return True
        rows=all_rows('SELECT chat_id FROM known_chats'); ok=0
        for r in rows:
            x=send(r['chat_id'],body)
            if x.get('ok'): ok+=1
        send(cid,'📢 تمت الإذاعة إلى <b>%s</b> محادثة.'%ok); return True
    if isdev and cmd in ('غادر',):
        if not arg1.lstrip('-').isdigit(): send(cid,'استخدم غادر -100...'); return True
        r=call('leaveChat',chat_id=int(arg1)); send(cid,'✅ تم.' if r.get('ok') else '❌ '+escape(str(r.get('description','')))); return True
    if cmd in ('صنع كود','تصفير فلوسه','اضف فلوس') and (isdev or iscreator):
        u=target or user_from_arg(cid,m,arg1); amount=int(rest or arg1 or 0) if str(rest or arg1).isdigit() else 0
        if not u: send(cid,'استخدم بالرد.'); return True
        bank_row(cid,u['id'])
        if cmd=='تصفير فلوسه': run('UPDATE bank SET money=0 WHERE chat_id=? AND user_id=?',(cid,u['id']))
        else: run('UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?',(amount,cid,u['id']))
        send(cid,'✅ تم تنفيذ أمر البنك.'); return True

    # entertainment / games aliases
    if cmd in ('اغنيه','اغنية','ميوزك','ريمكس'):
        fun_command(cid,uid,'غنيلي',target,arg1+' '+rest); return True
    if cmd in ('قصيده','قصيدة'):
        fun_command(cid,uid,'شعر',target); return True
    if cmd in ('زوجني','زواج','طلاق','ثنائي اليوم','نكات','قصص','هدية','عقاب','جاوبه'):
        if cmd=='طلاق': send(cid,'💔 تم تسجيل الطلاق 😅')
        elif cmd=='قصص': send(cid,'📖 قصة قصيرة: رجع من السفر فوجد أن أجمل مكان هو بيته.')
        elif cmd=='عقاب': send(cid,'😈 عقاب اليوم: اكتب كلمة «العراق» 3 مرات 😂')
        elif cmd=='جاوبه': send(cid,'🎙️ جاوبتك: الله يسعد يومك ❤️')
        else: fun_command(cid,uid,cmd,target)
        return True
    if cmd in ('اسالني','اسألني','لغز','حزوره','معاني','المختلف','العكس','رياضيات','xo','حجر','صراحة','لوخيروك','لو'):
        gm={'اسالني':'اسالني','لغز':'حزورة','حزوره':'حزورة'}.get(cmd,cmd); game_command(cid,uid,gm,text); return True
    return False

ALIASES={
"الروابط":"links","التاك":"tag","التعديل":"edit","المتحركة":"animated","المتحركه":"animated","الصور":"photos","الفيديو":"videos","الملفات":"documents","البوتات":"bots","التوجيه":"forward","الصوت":"audio","الجهات":"contacts","الموقع":"location","القنوات":"channels","التكرار":"spam","الملصقات":"stickers","البصمة":"voice","الانكليزية":"english","الإنكليزية":"english","الفارسية":"persian","التثبيت":"pin","الاشعارات":"notifications","الكل":"all"
}

def execute_lock(cid,uid,text,m):
    if not is_admin(cid,uid): send(cid,"❌ للمشرفين فقط.",reply_to=m["message_id"]); return True
    p=text.split(maxsplit=2)
    if len(p)<2:
        send(cid,"الاستخدام: <code>قفل الروابط</code> أو <code>فتح الروابط</code>",reply_to=m["message_id"]); return True
    k=ALIASES.get(p[1].strip().lower())
    if not k:
        send(cid,"❌ نوع الحماية غير معروف."); return True
    on=p[0]=="قفل"; set_prot(cid,k,on)
    send(cid,("🔒 تم قفل " if on else "🔓 تم فتح ")+"<b>"+escape(PROT[k])+"</b>")
    return True

def is_developer(user):
    return (user or {}).get("username", "").lower() == DEVELOPER.lower()

def can_change_id_style(cid, user):
    # مطوّر البوت أو رتبة مالك وما فوق داخل هذه المجموعة
    if is_developer(user):
        return True
    uid = (user or {}).get('id')
    return bool(uid and custom_rank(cid, uid) >= ROLE_ORDER['owner'])

def bot_name_text():
    r=call("getMe")
    if r.get("ok"):
        u=r.get("result", {})
        return "🤖 اسم البوت: <b>%s</b>" % escape(u.get("first_name") or u.get("username") or "غير معروف")
    return "❌ تعذر جلب اسم البوت حالياً."


# ID-card style chooser (developer/admin command: تغ)
ID_STYLE_INDEX = {}
ID_STYLE_TEMPLATES = [
"⌔︙ USE ➤ #username  ↝🍬.\n⌔︙ MSG ➤ #msgs  ↝🍬.\n⌔︙ STA ➤ #stast  ↝🍬.\n⌔︙ iD ➤ #id  ↝🍬.",
"⌔︙ • USE ➤ #username .\n• MSG ➤ #msgs .\n• STA ➤ #stast .\n• iD ➤ #id .",
"⌔︙ ➜𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 : #username\n➜𝗠𝗘𝗦𝗦𝗔𝗚𝗘𝗦 : #msgs\n➜𝗦𝗧𝗔𝗧𝗦 : #stast\n➜𝗜𝗗 : #id",
"⌔︙ ➥• USE 𖦹 #username - 🇮🇶.\n➥• MSG 𖥳 #msgs - 🇮🇶.\n➥• STA 𖦹 #stast - 🇮🇶.\n➥• iD 𖥳 #id - 🇮🇶.",
"⌔︙ - ᴜѕᴇʀɴᴀᴍᴇ ➣ #username .\n- ᴍѕɢѕ ➣ #msgs .\n- ѕᴛᴀᴛѕ ➣ #stast .\n- ʏᴏᴜʀ ɪᴅ ➣ #id .\n- ᴇᴅɪᴛ ᴍsɢ ➣ #edit .\n- ɢᴀᴍᴇ ➣ #game .",
"⌔︙ ♡ : 𝐼𝐷 ➤ #id .\n♡ : 𝑈𝑆𝐸𝑅 𖠀 #username .\n♡ : 𝑀𝑆𝐺𝑆 𖠀 #msgs .\n♡ : 𝑆𝑇𝐴𝑇𝑆 𖠀 #stast .\n♡ : 𝐸𝐷𝐼𝑇 𖠀 #edit .",
"⌔︙ • 🖤 | 𝑼𝑺𝑬 : #username\n• 🖤 | 𝑺𝑻𝑨 : #stast\n• 🖤 | 𝑰𝑫 : #id\n• 🖤 | 𝑴𝑺𝑮 : #msgs"
]
def id_style_keyboard(i):
    return kb([[btn("⬅️ السابق","idstyle:prev"),btn("التالي ➡️","idstyle:next")],
               [btn("✅ موافق","idstyle:yes"),btn("🙈 إخفاء","idstyle:hide")]])

# Content bans: text, sticker, photo, or any replied-to message.
PENDING_CONTENT_BAN = {}

def _ban_fingerprint(msg):
    if msg.get("sticker"):
        st=msg["sticker"]
        return ("sticker", str(st.get("file_unique_id") or st.get("file_id") or ""), "ملصق")
    if msg.get("photo"):
        ph=msg["photo"][-1]
        return ("photo", str(ph.get("file_unique_id") or ph.get("file_id") or ""), "صورة")
    if msg.get("text"):
        value=msg["text"].strip()
        if value: return ("text", value.casefold(), "نص: "+value[:70])
    if msg.get("caption"):
        value=msg["caption"].strip()
        if value: return ("text", value.casefold(), "نص الصورة/الوسائط: "+value[:70])
    for typ in ("animation","document","video","video_note","voice","audio"):
        if msg.get(typ):
            obj=msg[typ]
            return (typ, str(obj.get("file_unique_id") or obj.get("file_id") or ""), typ)
    return None

def handle_content_ban(m):
    chat=m.get("chat",{}); cid=chat.get("id"); uid=m.get("from",{}).get("id")
    txt=(m.get("text") or "").strip()
    if not cid or chat.get("type") not in ("group","supergroup"):
        return False
    # A pending moderator action captures the next message from that same moderator.
    pending=PENDING_CONTENT_BAN.get((cid,uid))
    if pending and txt not in ("الغاء", "إلغاء", "إلغاء المنع"):
        source=m.get("reply_to_message") or m
        fp=_ban_fingerprint(source)
        if fp:
            kind,value,label=fp
            run("INSERT OR IGNORE INTO content_bans(chat_id,kind,value) VALUES(?,?,?)",(cid,kind,value))
            PENDING_CONTENT_BAN.pop((cid,uid),None)
            # أخفِ الرسالة التي أرسلها المشرف لاختيار المحتوى بعد حفظ بصمتها.
            if m.get("message_id"):
                delete(cid, m.get("message_id"))
            send(cid,"🚫 تمت إضافة %s إلى قائمة المنع. أي رسالة مطابقة راح تنحذف."%escape(label))
        else:
            send(cid,"ما قدرت أحدد المحتوى. أرسل نصًا أو صورة أو ملصقًا، أو استخدم منع بالرد على الرسالة.",reply_to=m.get("message_id"))
        return True
    if pending and txt in ("الغاء", "إلغاء", "إلغاء المنع"):
        PENDING_CONTENT_BAN.pop((cid,uid),None); send(cid,"تم إلغاء عملية المنع.",reply_to=m.get("message_id")); return True
    # Start ban flow. Guard empty text: photo/sticker updates often have no text.
    first_word = txt.split(maxsplit=1)[0].lstrip("/").lower() if txt else ""
    if first_word in ("منع", "bancontent"):
        if not is_admin(cid,uid):
            send(cid,"❌ هذا الأمر للمشرفين فقط.",reply_to=m.get("message_id")); return True
        reply=m.get("reply_to_message")
        if reply:
            fp=_ban_fingerprint(reply)
            if not fp:
                send(cid,"ما أگدر أمنع هذا النوع من الرسائل. جرّب نص أو صورة أو ملصق.",reply_to=m.get("message_id")); return True
            kind,value,label=fp
            run("INSERT OR IGNORE INTO content_bans(chat_id,kind,value) VALUES(?,?,?)",(cid,kind,value))
            send(cid,"🚫 تم منع %s. أي رسالة مطابقة راح تنحذف."%escape(label),reply_to=m.get("message_id")); return True
        # 'منع text' bans text immediately; bare 'منع' asks what to ban.
        parts=txt.split(maxsplit=1)
        if len(parts)>1 and parts[1].strip():
            value=parts[1].strip()
            run("INSERT OR IGNORE INTO content_bans(chat_id,kind,value) VALUES(?,?,?)",(cid,"text",value.casefold()))
            send(cid,"🚫 تم منع النص: <code>%s</code>"%escape(value),reply_to=m.get("message_id")); return True
        PENDING_CONTENT_BAN[(cid,uid)]=True
        send(cid,"شنو تريد تمنع؟\n• أرسل النص المراد منعه\n• أو أرسل صورة/ملصق\n• أو رد بكلمة منع على الرسالة المراد منعها\nللإلغاء اكتب: إلغاء",reply_to=m.get("message_id")); return True
    # Enforce saved bans, excluding the moderator's command message itself.
    fp=_ban_fingerprint(m)
    if fp:
        kind,value,_=fp
        rows=all_rows("SELECT kind,value FROM content_bans WHERE chat_id=?",(cid,))
        for row in rows:
            saved_kind = row["kind"]
            saved_value = row["value"]
            if saved_kind == kind and saved_value == value:
                result = delete(cid, m.get("message_id"))
                if not result.get("ok"):
                    print("Content-ban delete failed:", result.get("description", "unknown"))
                return True
            if kind == "text" and saved_kind == "text" and saved_value and saved_value in value:
                result = delete(cid, m.get("message_id"))
                if not result.get("ok"):
                    print("Content-ban delete failed:", result.get("description", "unknown"))
                return True
    return False

def text_command(m):
    chat=m.get("chat",{}); cid=chat.get("id"); uid=m.get("from",{}).get("id"); text=(m.get("text") or "").strip()
    if not cid: return
    if handle_content_ban(m): return
    if advanced_command(m): return
    # اختصار تغ لاختيار شكل بطاقة الايدي
    if text in ("تغ", "/تغ", "تغيير الايدي", "تغيير الايدي بالصورة", "تغيير كليشة الايدي"):
        if not can_change_id_style(cid, m.get("from", {})):
            send(cid, "❌ هذا الأمر للمطور أو المالك وما فوق.", reply_to=m.get("message_id")); return
        ID_STYLE_INDEX[cid] = ID_STYLE_INDEX.get(cid, 0) % len(ID_STYLE_TEMPLATES)
        send(cid, "⌔︙ هل تريد تعيين هذا الشكل ↯\n\n" + ID_STYLE_TEMPLATES[ID_STYLE_INDEX[cid]],
             id_style_keyboard(ID_STYLE_INDEX[cid]), reply_to=m.get("message_id"))
        return
    parts0=text.split(maxsplit=3)
    cmd0=parts0[0].lstrip("/").lower() if parts0 else ""
    if text in ("اسم البوت", "/اسم_البوت"):
        send(cid,bot_name_text(),reply_to=m.get("message_id")); return
    if text.startswith("تغيير اسم البوت") or text.startswith("تغيير اسم البوت "):
        if not is_developer(m.get("from")):
            send(cid,"❌ هذا الأمر للمطوّر فقط.",reply_to=m.get("message_id")); return
        new_name=text[len("تغيير اسم البوت"):].strip()
        if not new_name:
            send(cid,"اكتب الاسم هكذا: <code>تغيير اسم البوت الاسم الجديد</code>",reply_to=m.get("message_id")); return
        rr=call("setMyName",name=new_name)
        send(cid,("✅ تم تغيير اسم البوت إلى: <b>%s</b>"%escape(new_name)) if rr.get("ok") else ("❌ فشل تغيير الاسم: "+escape(str(rr.get("description","خطأ غير معروف")))),reply_to=m.get("message_id")); return
    if chat.get("type") in ("group","supergroup"):
        run("INSERT OR REPLACE INTO known_chats(chat_id,title,type) VALUES(?,?,?)",(cid,chat.get("title",""),chat.get("type")))
        add_activity(cid,uid)
    if text in ("/start","/help","الاوامر","اوامر","الوامر"):
        target=target_from_message(m)
        result=send(cid,"🤖 <b>بوت الحماية والإدارة</b>\nاختر القسم:",home_kb(),reply_to=m["message_id"] if target else None)
        if result.get("ok"):
            save_menu_context(cid,result.get("result",{}).get("message_id"),target,m.get("reply_to_message",{}).get("message_id") if target else None)
        return
    if text.startswith("قفل ") or text.startswith("فتح "):
        if chat.get("type") in ("group","supergroup"): execute_lock(cid,uid,text,m)
        return
    parts=text.split(maxsplit=2); cmd=parts[0].lstrip("/").lower()
    target=target_from_message(m)
    # moderation commands
    mods={"حظر":"ban","طرد":"kick","كتم":"mute","الغاء":"unmute","الغاءكتم":"unmute","تقييد":"mute","الغاءتقييد":"unmute","انذار":"warn"}
    if cmd in mods:
        if not is_admin(cid,uid): send(cid,"❌ للمشرفين فقط.",reply_to=m["message_id"]); return
        if not target: send(cid,"⚠️ استخدم الأمر بالرد على رسالة العضو.",reply_to=m["message_id"]); return
        if not can_target(cid,target["id"]): send(cid,"❌ لا يمكن تنفيذ الأمر على مشرف أو مالك."); return
        a=mods[cmd]
        if a=="ban": r=ban(cid,target["id"]); msg="🚫 تم حظر "+mention(target)
        elif a=="kick": r=kick(cid,target["id"]); msg="👢 تم طرد "+mention(target)
        elif a=="mute": r=mute(cid,target["id"]); msg="🔇 تم كتم "+mention(target)
        elif a=="unmute": r=unmute(cid,target["id"]); msg="🔊 تم رفع القيود عن "+mention(target)
        else:
            row=one("SELECT count FROM warnings WHERE chat_id=? AND user_id=?",(cid,target["id"])); n=(row[0] if row else 0)+1
            run("INSERT INTO warnings(chat_id,user_id,count) VALUES(?,?,?) ON CONFLICT(chat_id,user_id) DO UPDATE SET count=excluded.count",(cid,target["id"],n)); r={"ok":True}; msg=f"⚠️ تم إنذار {mention(target)}\nالإنذارات: <b>{n}</b>"
            if n>=3: mute(cid,target["id"]); msg += "\n🔇 وصل 3 إنذارات وتم كتمه."
        send(cid,msg if r.get("ok") else "❌ فشل التنفيذ. تأكد من صلاحيات البوت."); return
    if cmd in ("مسح","del"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        r=m.get("reply_to_message")
        if r: delete(cid,r["message_id"]); delete(cid,m["message_id"])
        else: send(cid,"⚠️ استخدم مسح بالرد على رسالة.")
        return
    if cmd in ("تثبيت","pin"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        r=m.get("reply_to_message")
        if not r: return send(cid,"⚠️ استخدم تثبيت بالرد على رسالة.")
        send(cid,mod_result(pin(cid,r["message_id"]),"📌 تم تثبيت الرسالة.")); return
    if cmd in ("الغاء تثبيت","unpin"):
        if is_admin(cid,uid): send(cid,mod_result(unpin(cid),"📌 تم إلغاء التثبيت.")); return
    # voice-note notifications
    if cmd in ("اشعار بصمه", "إشعار بصمة", "اشعار البصمه", "إشعار البصمة"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        new=not bool(settings(cid).get("voice_notifications",1)); set_setting(cid,"voice_notifications",int(new))
        return send(cid,"🎙️ إشعار البصمة: <b>%s</b>"%( "مفعل" if new else "متوقف"))
    if cmd in ("اشعار بصمه تشغيل", "إشعار بصمة تشغيل"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        set_setting(cid,"voice_notifications",1); return send(cid,"🎙️ تم تشغيل إشعار البصمة.")
    if cmd in ("اشعار بصمه ايقاف", "إشعار بصمة إيقاف"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        set_setting(cid,"voice_notifications",0); return send(cid,"🔕 تم إيقاف إشعار البصمة.")
    # group settings
    if cmd=="القوانين":
        r=settings(cid); send(cid,"📜 <b>قوانين المجموعة</b>\n"+(r["rules"] or "لم يتم تعيين القوانين بعد.")); return
    if cmd=="ضع قوانين":
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        val=" ".join(parts[2:]) if len(parts)>2 else ""
        if not val: return send(cid,"الاستخدام: ضع قوانين نص القوانين")
        set_setting(cid,"rules",val); send(cid,"✅ تم حفظ القوانين."); return
    if cmd in ("الترحيب","welcome"):
        if not is_admin(cid,uid): return send(cid,"❌ للمشرفين فقط.")
        new=not bool(settings(cid)["welcome"]); set_setting(cid,"welcome",int(new)); send(cid,"✅ الترحيب مفعل." if new else "🔕 تم تعطيل الترحيب."); return
    if cmd in ("الرابط","link"):
        r=call("exportChatInviteLink",chat_id=cid)
        send(cid,"🔗 "+(r.get("result") if r.get("ok") else "تعذر إنشاء الرابط. تأكد من صلاحيات البوت.")); return
    if cmd in ("غنيلي", "غنّيلي", "غني", "شعر"):
        extra = " ".join(parts[1:]).strip() if len(parts) > 1 else ""
        fun_command(cid, uid, "شعر" if cmd == "شعر" else "غنيلي", target, extra)
        return
    # points
    if cmd in ("نقاطي","نقاط","رتبتي"):
        r=one("SELECT points,messages FROM points WHERE chat_id=? AND user_id=?",(cid,uid)); send(cid,"⭐ النقاط: <b>%s</b>\n💬 الرسائل: <b>%s</b>"%(r[0] if r else 0,r[1] if r else 0)); return
    if cmd in ("حسابي","فلوسي","راتب","حظ","استثمار","قروضي","كنز"):
        bank_command(cid,uid,cmd,target,parts); return
    if cmd in ("تحويل","حول"):
        if not target or len(parts)<2 or not parts[1].isdigit(): return send(cid,"💸 استخدم: <code>تحويل 100</code> بالرد على العضو.")
        amount=int(parts[1]); r=bank_row(cid,uid)
        if amount<=0 or r["money"]<amount: return send(cid,"❌ رصيدك لا يكفي.")
        bank_row(cid,target["id"]); run("UPDATE bank SET money=money-? WHERE chat_id=? AND user_id=?",(amount,cid,uid)); run("UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?",(amount,cid,target["id"])); return send(cid,"💸 تم تحويل <b>%s</b> إلى %s."%(amount,mention(target)))
    if cmd in ("ملك","ملكة","اثول","مطّي","بقره","غبي","حب","هدية"):
        fun_command(cid,uid,cmd,target); return
    if cmd in ("حزورة","خمن","رياضيات","العكس","حجر","xo","صراحة","لوخيروك","لو","المختلف"):
        game_command(cid,uid,cmd,text); return
    # active game answers
    active=one("SELECT game,answer FROM game_state WHERE chat_id=?",(cid,))
    if active and text and cmd not in ("رياضيات","العكس","حجر","xo","صراحة","لوخيروك","لو","المختلف","حزورة","خمن"):
        if text.strip().lower()==str(active["answer"]).lower():
            run("DELETE FROM game_state WHERE chat_id=?",(cid,)); send(cid,"🎉 <b>إجابة صحيحة!</b> +10 نقاط ⭐"); run("UPDATE points SET points=points+10 WHERE chat_id=? AND user_id=?",(cid,uid)); return
    # auto protection
    if chat.get("type") in ("group","supergroup") and not is_admin(cid,uid):
        handle_protection(m)
    # custom exact reply + 600 رد جاهز
    if settings(cid)["auto_reply"]:
        row=one("SELECT reply FROM custom_replies WHERE chat_id=? AND trigger=?",(cid,text.lower()))
        if row:
            send(cid,row[0],reply_to=m["message_id"]); return
        builtin_reply=BUILTIN_REPLIES.get(text.strip().lower())
        if builtin_reply:
            send(cid,builtin_reply,reply_to=m["message_id"]); return

def handle_protection(m):
    cid=m["chat"]["id"]; uid=m.get("from",{}).get("id"); text=(m.get("text") or "").lower(); mid=m["message_id"]
    def punish(key):
        act=action_for(cid,key)
        if act=="mute": mute(cid,uid)
        elif act=="kick": kick(cid,uid)
        else: delete(cid,mid)
    if prot(cid,"links") and ("http://" in text or "https://" in text or "t.me/" in text or "www." in text): punish("links"); return
    if prot(cid,"tag") and "@" in text: punish("tag"); return
    if prot(cid,"forward") and m.get("forward_origin"): punish("forward"); return
    if prot(cid,"photos") and m.get("photo"): punish("photos"); return
    if prot(cid,"videos") and (m.get("video") or m.get("video_note")): punish("videos"); return
    if prot(cid,"documents") and m.get("document"): punish("documents"); return
    if prot(cid,"audio") and (m.get("audio") or m.get("voice")): punish("audio"); return
    if prot(cid,"contacts") and m.get("contact"): punish("contacts"); return
    if prot(cid,"location") and m.get("location"): punish("location"); return
    if prot(cid,"stickers") and m.get("sticker"): punish("stickers"); return
    if prot(cid,"spam"):
        row=one("SELECT message_id FROM messages WHERE chat_id=? AND user_id=? AND kind=? ORDER BY message_id DESC LIMIT 1",(cid,uid,"text"))
        if row:
            # recent consecutive text duplicate; Telegram IDs are monotonic in a chat.
            prev=one("SELECT 1 FROM messages WHERE chat_id=? AND message_id=? AND kind=?",(cid,row[0],"text"))
            if prev: delete(cid,mid); return
    if m.get("forward_origin"): kind="forward"
    elif m.get("photo") or m.get("video") or m.get("document") or m.get("audio") or m.get("voice") or m.get("sticker"): kind="media"
    elif re.search(r"https?://|t\.me/|www\.", text): kind="links"
    else: kind="text"
    run("INSERT OR REPLACE INTO messages(chat_id,message_id,user_id,kind) VALUES(?,?,?,?)",(cid,mid,uid,kind))
    # Keep only latest 2000 message records per chat.
    run("DELETE FROM messages WHERE chat_id=? AND message_id NOT IN (SELECT message_id FROM messages WHERE chat_id=? ORDER BY message_id DESC LIMIT 2000)",(cid,cid))

# ---------------- Bank / fun ----------------
def bank_row(cid,uid):
    run("INSERT OR IGNORE INTO bank(chat_id,user_id) VALUES(?,?)",(cid,uid)); return one("SELECT * FROM bank WHERE chat_id=? AND user_id=?",(cid,uid))

def bank_command(cid,uid,cmd,target,parts):
    r=bank_row(cid,uid); money=r["money"]
    if cmd in ("حسابي","فلوسي"): return send(cid,"💳 <b>حسابك</b>\n💰 الرصيد: <b>%s</b>\n🧾 الدين: <b>%s</b>"%(money,r["debt"]))
    if cmd=="راتب":
        now=int(time.time())
        if now-r["last_salary"]<86400: return send(cid,"⏳ الراتب مرة كل 24 ساعة.")
        amount=random.randint(200,700); run("UPDATE bank SET money=money+?,last_salary=? WHERE chat_id=? AND user_id=?",(amount,now,cid,uid)); return send(cid,"💵 استلمت راتب <b>%s</b>."%amount)
    if cmd=="حظ":
        amount=random.randint(-100,500); run("UPDATE bank SET money=MAX(0,money+?) WHERE chat_id=? AND user_id=?",(amount,cid,uid)); return send(cid,("🍀 ربحـت " if amount>=0 else "💸 خسرت ")+"<b>%s</b>."%abs(amount))
    if cmd=="استثمار":
        if money<100: return send(cid,"❌ تحتاج 100 على الأقل.")
        gain=random.randint(-80,180); run("UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?",(gain,cid,uid)); return send(cid,("📈 ربح " if gain>=0 else "📉 خسارة ")+"<b>%s</b>."%abs(gain))
    if cmd=="قروضي": return send(cid,"🧾 دينك الحالي: <b>%s</b>"%r["debt"])
    if cmd=="كنز":
        gain=random.randint(50,1000); run("UPDATE bank SET money=money+? WHERE chat_id=? AND user_id=?",(gain,cid,uid)); return send(cid,"💎 وجدت كنزًا بقيمة <b>%s</b>!"%gain)

def send_song_preview(cid, query="عراقي", m=None):
    """Download the available preview first, then upload it as a real Telegram Audio file."""
    try:
        url="https://itunes.apple.com/search?term="+urllib.parse.quote(query)+"&entity=song&limit=25"
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as rr:
            data=json.loads(rr.read().decode("utf-8"))
        results=[x for x in data.get("results",[]) if x.get("previewUrl")]
        if not results:
            return send(cid,"❌ ما لكيت مقطع صوتي متاح لهالطلب.")
        # اختيار عشوائي صحيح من النتائج، ثم استعمال file_id إذا كانت الأغنية مرفوعة سابقاً.
        x=random.choice(results)
        cache_key = x.get("trackId") or (x.get("artistName", "") + "|" + x.get("trackName", ""))
        cached = SONG_FILE_CACHE.get(cache_key)
        if cached:
            return call("sendAudio", chat_id=cid, audio=cached, reply_to_message_id=(m or {}).get("message_id"))
        audio_url=x["previewUrl"]
        title=escape(x.get("trackName","أغنية")); artist=escape(x.get("artistName",""))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as f:
            tmp=f.name
            with urllib.request.urlopen(audio_url, timeout=45) as rr:
                f.write(rr.read())
        try:
            res=upload_audio_file(cid,tmp,caption="",reply_to=(m or {}).get("message_id"),filename="%s - %s.m4a"%(x.get("artistName","Audio"),x.get("trackName","Song")),content_type="audio/mp4")
            if not res.get("ok"):
                return send(cid,"❌ فشل رفع الملف الصوتي إلى تيليجرام: <code>%s</code>"%escape(str(res.get("description","unknown"))))
            try:
                fid = res.get("result", {}).get("audio", {}).get("file_id")
                if fid: SONG_FILE_CACHE[cache_key] = fid
            except Exception:
                pass
            return res
        finally:
            try: os.remove(tmp)
            except OSError: pass
    except Exception as e:
        print("song preview:",repr(e))
        return send(cid,"❌ تعذر تنزيل الملف الصوتي الآن. تأكد من اتصال PyDroid بالإنترنت.")

def send_poem_audio(cid, poem, m=None):
    """Download Arabic TTS to a real local audio file, then upload it to Telegram."""
    try:
        q=urllib.parse.quote(poem[:190])
        tts="https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=ar&q="+q
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp=f.name
            req=urllib.request.Request(tts, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as rr:
                f.write(rr.read())
        try:
            res=upload_audio_file(cid,tmp,caption="",reply_to=(m or {}).get("message_id"),filename="poem.mp3",content_type="audio/mpeg")
            if not res.get("ok"):
                return send(cid,"📝 <b>الشعر</b>\n"+escape(poem)+"\n\n❌ فشل رفع الملف الصوتي: <code>%s</code>"%escape(str(res.get("description","unknown"))))
            return res
        finally:
            try: os.remove(tmp)
            except OSError: pass
    except Exception as e:
        print("poem tts:",repr(e))
        return send(cid,"❌ تعذر إنشاء ملف الصوت الآن. تأكد من اتصال PyDroid بالإنترنت.")

current_message_for_audio={}

def fun_command(cid,uid,cmd,target=None,extra=""):
    names={"ملك":"👑 الملك هو","ملكة":"👸 الملكة هي","اثول":"🤪 الأثول هو","مطّي":"😂 المطّي هو","بقره":"🐄 البقرة هي","غبي":"🤡 الغبي هو"}
    if cmd in names:
        chosen=(target.get("first_name") if target else None) or "عضو عشوائي"
        return send(cid,names[cmd]+" <b>%s</b> 😄"%escape(chosen))
    if cmd=="حب": return send(cid,"❤️ نسبة الحب اليوم: <b>%s%%</b>"%random.randint(1,100))
    if cmd=="هدية": return send(cid,"🎁 هديتك اليوم: <b>%s</b>"%random.choice(["قلب ❤️","وردة 🌹","ذهب 🪙","حظ سعيد 🍀","ابتسامة 😊"]))
    if cmd=="نكات":
        return send(cid,"😂 <b>نكتة:</b> مرة واحد بخيل راح يتبرع بالدم، رجع قال لهم: خلّوه قرض! 😄")
    if cmd=="شعر":
        poem = next_content(cid, "poem", POEMS)
        return send_poem_audio(cid, poem, current_message_for_audio.get(cid))
    if cmd=="غنيلي":
        # A bare command selects one of 100 curated song searches without repeating
        # until the list is exhausted. A supplied title searches that title directly.
        q = extra.strip() or next_content(cid, "song", SONG_QUERIES)
        # لا نرسل رسالة بحث/انتظار؛ يطلع الصوت مباشرة عند توفره.
        return send_song_preview(cid, q, m=current_message_for_audio.get(cid))
    if cmd in ("زوجني","زواج","ثنائي"):
        if cmd=="زوجني":
            run("CREATE TABLE IF NOT EXISTS marriages(chat_id INTEGER NOT NULL,user_id INTEGER NOT NULL,partner_id INTEGER NOT NULL,created_at INTEGER,PRIMARY KEY(chat_id,user_id))")
            candidates = active_known_users(cid, exclude=uid)
            if not candidates:
                return send(cid, "💍 ما عندي أعضاء كافيين للاختيار بعد. خلي الأعضاء يرسلون رسائل بالمجموعة أولاً.")
            chosen_id = random.choice(candidates)
            cm = call("getChatMember", chat_id=cid, user_id=chosen_id)
            chosen = (cm.get("result", {}).get("user") or {}) if cm.get("ok") else {"id": chosen_id, "first_name": "العضو المختار"}
            run("INSERT OR REPLACE INTO marriages(chat_id,user_id,partner_id,created_at) VALUES(?,?,?,?)",(cid,uid,chosen_id,int(time.time())))
            run("INSERT OR REPLACE INTO marriages(chat_id,user_id,partner_id,created_at) VALUES(?,?,?,?)",(cid,chosen_id,uid,int(time.time())))
            return send(cid, "💍❤️ ألف مبروك! لقد تم تزويجك من %s 🎉\\nالله يديم المحبة 😄" % mention(chosen))
        if cmd=="زواج": return send(cid,"💒 مبارك الزواج! الله يسعدكم ويهنيكم ❤️")
        return send(cid,"❤️ <b>ثنائي اليوم:</b> تم اختيار ثنائي عشوائي من أعضاء المجموعة 💑")

    if cmd=="صورتي":
        target_id=target.get("id") if target else uid
        r=call("getUserProfilePhotos",user_id=target_id,limit=1)
        if not r.get("ok") or not r.get("result",{}).get("photos"):
            return send(cid,"🖼️ لا توجد صورة شخصية متاحة لهذا العضو.")
        photo=r["result"]["photos"][0][-1]["file_id"]
        return call("sendPhoto",chat_id=cid,photo=photo,caption="🖼️ الصورة الشخصية")

def xo_board(board):
    return kb([[btn(board[0] or "1","xo:0"),btn(board[1] or "2","xo:1"),btn(board[2] or "3","xo:2")],
               [btn(board[3] or "4","xo:3"),btn(board[4] or "5","xo:4"),btn(board[5] or "6","xo:5")],
               [btn(board[6] or "7","xo:6"),btn(board[7] or "8","xo:7"),btn(board[8] or "9","xo:8")]])

def xo_winner(b):
    for a,c,d in ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)):
        if b[a] and b[a]==b[c]==b[d]: return b[a]
    return "draw" if all(b) else None

def xo_start(cid,uid):
    board=["","","","","","","","",""]
    run("INSERT OR REPLACE INTO game_state(chat_id,game,answer,question) VALUES(?,?,?,?)",(cid,"xo",json.dumps(board),str(uid)))
    return send(cid,"⭕❌ <b>XO</b>\nأنت X — اختر مربعًا:",xo_board(board))

# ---------------- Games ----------------
def game_command(cid,uid,cmd,text):
    if cmd=="رياضيات":
        a=random.randint(2,20); b=random.randint(2,20); ans=a+b; run("INSERT OR REPLACE INTO game_state(chat_id,game,answer,question) VALUES(?,?,?,?)",(cid,"math",str(ans),f"{a}+{b}")); return send(cid,"🎯 كم الناتج؟ <b>%s + %s = ؟</b>\nأرسل الجواب."%(a,b))
    if cmd=="العكس":
        word=random.choice(["كتاب","عراق","حب","مدرسة","برمجة"]); run("INSERT OR REPLACE INTO game_state(chat_id,game,answer,question) VALUES(?,?,?,?)",(cid,"reverse",word[::-1],word)); return send(cid,"🔄 اعكس الكلمة: <b>%s</b>"%word)
    if cmd=="حجر": return send(cid,"✊ اختر: حجر / ورق / مقص")
    if cmd in ("لوخيروك","لو"): return send(cid,"🤔 لو خيروك: تعيش بدون هاتف سنة 📵 أم بدون ألعاب سنة 🎮؟")
    if cmd=="صراحة": return send(cid,"🗣️ صراحة: ما أكثر شيء تحبه في شخصيتك؟")
    if cmd=="حزورة": return send(cid,"❓ شيء له أسنان ولا يعض، ما هو؟")
    if cmd=="خمن": return send(cid,"🎯 خمن رقمًا بين 1 و10.")
    if cmd=="المختلف": return send(cid,"🔀 أوجد المختلف: تفاحة 🍎، برتقالة 🍊، سيارة 🚗، موزة 🍌")
    if cmd=="معاني":
        pairs={"جميل":"حسن","شجاع":"جريء","سريع":"عاجل","قديم":"عتيق"}; w=random.choice(list(pairs)); run("INSERT OR REPLACE INTO game_state(chat_id,game,answer,question) VALUES(?,?,?,?)",(cid,"meaning",pairs[w],w)); return send(cid,"🔤 ما معنى كلمة <b>%s</b>؟"%w)
    if cmd=="xo": return xo_start(cid,uid)
    # answer to active game
    row=one("SELECT game,answer,question FROM game_state WHERE chat_id=?",(cid,))
    if row and text.strip().lower()==str(row["answer"]).lower():
        run("DELETE FROM game_state WHERE chat_id=?",(cid,)); return send(cid,"🎉 إجابة صحيحة!")


# ---------------- Extra real features ----------------
def toggle_setting(cid, col):
    r=settings(cid); new=not bool(r[col]); set_setting(cid,col,int(new)); return new

def welcome_text(cid):
    r=settings(cid); return r["welcome_text"] or "🎉 أهلاً {name} نورت المجموعة!\n❤️ نتمنى لك وقتًا ممتعًا."

def send_welcome(cid, u):
    """ترحيب بعضو جديد مع زر «حياك» يفتح حساب العضو نفسه."""
    r = settings(cid)
    if not r["welcome"]:
        return
    uid = u.get("id")
    name = escape(u.get("first_name") or "صديقنا")
    username = (u.get("username") or "").strip().lstrip("@")
    txt = welcome_text(cid).replace("{name}", name).replace("{id}", str(uid or ""))
    if username:
        profile_url = "https://t.me/" + username
    elif uid:
        profile_url = "tg://user?id=" + str(uid)
    else:
        # إذا لم يصل مع التحديث معرّف صالح، نرسل الترحيب بلا زر.
        return send(cid, txt)
    keyboard = {"inline_keyboard": [[{"text": "حياك 👋", "url": profile_url}]]}
    return send(cid, txt, keyboard=keyboard)

def reply_list(cid):
    rows=all_rows("SELECT trigger,reply FROM custom_replies WHERE chat_id=? ORDER BY trigger LIMIT 100",(cid,))
    if not rows: return "📋 <b>الردود</b>\nلا توجد ردود حتى الآن.\n\nلإضافة رد: <code>اضف مرحبا اهلاً وسهلاً</code>"
    return "📋 <b>الردود المخصصة</b>\n"+"\n".join("• <code>%s</code> ← %s"%(escape(x[0]),escape(x[1])) for x in rows)

def clean_tracked(cid, kind=None, limit=10):
    if kind is None: rows=all_rows("SELECT message_id FROM messages WHERE chat_id=? ORDER BY message_id DESC LIMIT ?",(cid,limit))
    else: rows=all_rows("SELECT message_id FROM messages WHERE chat_id=? AND kind=? ORDER BY message_id DESC LIMIT ?",(cid,kind,limit))
    n=0
    for r in rows:
        if delete(cid,r[0]).get("ok"): n+=1
    return n

def music_menu_text():
    return ("🎵 <b>قسم الأغاني</b>\n\n"
            "• <code>اغنية اسم الاغنية</code> — يبحث عن رابط الأغنية.\n"
            "• <code>اغنية https://...mp3</code> — يرسل ملف الصوت إذا كان الرابط مباشرًا.\n"
            "• <code>بحث اغنية اسم</code> — يعرض نتائج بحث وروابط.\n\n"
            "ملاحظة: البوت لا يحمّل محتوى محميًا من منصات غير المسموح بها، لكنه يستطيع إرسال رابط صوت مباشر أو نتائج بحث.")

def search_music(q):
    try:
        url="https://itunes.apple.com/search?term="+urllib.parse.quote(q)+"&entity=song&limit=5"
        with urllib.request.urlopen(url,timeout=25) as r: data=json.loads(r.read().decode("utf-8"))
        out=["🎵 <b>نتائج الأغاني</b>"]
        for x in data.get("results",[]):
            name=escape(x.get("trackName","")); artist=escape(x.get("artistName","")); link=x.get("trackViewUrl","")
            if link: out.append("• <b>%s</b> — %s\n<a href=\"%s\">فتح الأغنية</a>"%(name,artist,escape(link)))
        return "\n".join(out) if len(out)>1 else "❌ لم أجد نتائج."
    except Exception as e:
        print("music search:",repr(e)); return "❌ تعذر البحث عن الأغنية الآن."

def send_audio_url(cid, url, reply_to=None):
    return call("sendAudio",chat_id=cid,audio=url,reply_to_message_id=reply_to or None)

def music_command(cid,text,m=None):
    parts=text.split(maxsplit=1)
    if len(parts)<2: return send(cid,music_menu_text(),reply_to=m.get("message_id") if m else None)
    q=parts[1].strip()
    if re.match(r"^https?://\S+\.(mp3|m4a|ogg|wav)(\?.*)?$",q,re.I):
        r=send_audio_url(cid,q,m.get("message_id") if m else None)
        if not r.get("ok"): send(cid,"❌ لم أستطع إرسال الملف الصوتي. تأكد أن الرابط مباشر ومتاح للعامة.",reply_to=m.get("message_id") if m else None)
        return
    send(cid,search_music(q),reply_to=m.get("message_id") if m else None)

# ---------------- Callback engine ----------------
def callback(cb):
    data=cb.get("data",""); msg=cb.get("message")
    if not msg: answer(cb["id"]); return
    cid=msg["chat"]["id"]; uid=cb["from"]["id"]
    try:
        if data.startswith("whisper:view:"):
            try: secret_id=int(data.split(":",2)[2])
            except Exception:
                answer(cb["id"], "❌ الهمسة غير صالحة.", True); return
            secret=one("SELECT target_id,body,created_at FROM whisper_messages WHERE id=? AND group_id=?", (secret_id, cid))
            if not secret:
                answer(cb["id"], "⌛ الهمسة غير موجودة أو انتهت.", True); return
            if int(secret["target_id"]) != int(uid):
                answer(cb["id"], "🔒 هذه الهمسة ليست لك؛ المستلم فقط يستطيع قراءتها.", True); return
            if int(time.time())-int(secret["created_at"]) > 86400:
                answer(cb["id"], "⌛ انتهت صلاحية الهمسة.", True); return
            answer(cb["id"], str(secret["body"])[:190], True); return
        if data.startswith("idstyle:"):
            if not can_change_id_style(cid, cb.get("from", {})):
                answer(cb["id"], "للمطور أو المالك وما فوق فقط", True); return
            i=ID_STYLE_INDEX.get(cid, 0)
            action=data.split(":",1)[1]
            if action=="next":
                i=(i+1)%len(ID_STYLE_TEMPLATES); ID_STYLE_INDEX[cid]=i
                edit(cid,msg["message_id"],"⌔︙ هل تريد تعيين هذا الشكل ↯\\n\\n"+ID_STYLE_TEMPLATES[i],id_style_keyboard(i))
            elif action=="prev":
                i=(i-1)%len(ID_STYLE_TEMPLATES); ID_STYLE_INDEX[cid]=i
                edit(cid,msg["message_id"],"⌔︙ هل تريد تعيين هذا الشكل ↯\\n\\n"+ID_STYLE_TEMPLATES[i],id_style_keyboard(i))
            elif action=="yes":
                ID_STYLE_INDEX[cid] = i
                answer(cb["id"],"تم اختيار الشكل %s"%(i+1),False)
                edit(cid,msg["message_id"],"✅ تم اختيار شكل الايدي رقم %s. جرّب أمر ايدي لعرض الشكل الجديد."%(i+1),None)
            else:
                answer(cb["id"],"تم الإخفاء")
                call("deleteMessage",chat_id=cid,message_id=msg["message_id"])
            answer(cb["id"]); return
        if data=="home": edit(cid,msg["message_id"],"🤖 <b>القائمة الرئيسية</b>\nاختر القسم:",home_kb()); answer(cb["id"]); return
        if data.startswith("admin:page:"):
            page=int(data.rsplit(":",1)[1])
            page=max(1,min(4,page))
            edit(cid,msg["message_id"],"👮 <b>إعدادات الأدمن</b>\nاختر أي زر لتفعيله أو تعطيله.",admin_toggle_kb(cid,page))
            answer(cb["id"]); return
        if data=="admin:actions":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            edit(cid,msg["message_id"],"👮 <b>إجراءات الإدارة</b>\nنفّذ الأمر على الرسالة التي تريدها.",admin_actions_kb()); answer(cb["id"]); return
        if data.startswith("toggle:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            _,key,page_s=data.split(":",2)
            new=not command_toggle(cid,key)
            set_command_toggle(cid,key,new)
            # Map important toggles to existing settings too.
            if key=="welcome": set_setting(cid,"welcome",1 if new else 0)
            elif key in ("replies",): set_setting(cid,"auto_reply",1 if new else 0)
            elif key=="voice_notifications": set_setting(cid,"voice_notifications",1 if new else 0)
            answer(cb["id"],("🟢 تم التفعيل" if new else "🔴 تم التعطيل"))
            edit(cid,msg["message_id"],"👮 <b>إعدادات الأدمن</b>\nاختر أي زر لتفعيله أو تعطيله.",admin_toggle_kb(cid,int(page))); return
        if data=="admin:all":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            for key,_ in ADMIN_TOGGLES: set_command_toggle(cid,key,True)
            for k in PROT: set_prot(cid,k,True,"delete")
            for col in ("welcome","notifications","auto_reply","voice_notifications"): set_setting(cid,col,1)
            answer(cb["id"],"✅ تم تفعيل الكل")
            edit(cid,msg["message_id"],"👮 <b>إعدادات الأدمن</b>\nاختر أي زر لتفعيله أو تعطيله.",admin_toggle_kb(cid,1)); return
        if data=="admin:none":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            for key,_ in ADMIN_TOGGLES: set_command_toggle(cid,key,False)
            for k in PROT: set_prot(cid,k,False,"delete")
            for col in ("welcome","notifications","auto_reply","voice_notifications"): set_setting(cid,col,0)
            answer(cb["id"],"🔴 تم تعطيل الكل")
            edit(cid,msg["message_id"],"👮 <b>إعدادات الأدمن</b>\nاختر أي زر لتفعيله أو تعطيله.",admin_toggle_kb(cid,1)); return
        if data.startswith("menu:"):
            sec=data.split(":",1)[1]; show_menu(cid,msg["message_id"],sec); answer(cb["id"]); return
        if data.startswith("prot:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            key=data.split(":",1)[1]; new=not prot(cid,key); set_prot(cid,key,new); edit(cid,msg["message_id"],"🛡️ <b>أوامر الحماية</b>\nاضغط على الحماية لتفعيلها/تعطيلها.",protect_kb(cid)); answer(cb["id"],"🔒 تم القفل" if new else "🔓 تم الفتح"); return
        if data=="protmode":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            edit(cid,msg["message_id"],"⚙️ <b>طريقة العقوبة</b>\nاختر الطريقة ثم اضغط حماية من القائمة.",kb([[btn("🗑️ حذف","mode:delete"),btn("🔇 كتم","mode:mute")],[btn("👢 طرد","mode:kick")],[btn("⬅️ رجوع","menu:protect")]])); answer(cb["id"]); return
        if data.startswith("mode:"):
            mode=data.split(":",1)[1]
            for k in PROT: set_prot(cid,k,prot(cid,k),mode)
            show_menu(cid,msg["message_id"],"protect"); answer(cb["id"],"تم تغيير طريقة العقوبة"); return
        if data.startswith("act:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            a=data.split(":",1)[1]
            t,target_mid=menu_context(cid,msg["message_id"])
            if not t:
                t,target_mid=action_target_from_callback(msg)
            if a=="delete":
                ok=delete(cid,target_mid).get("ok") if target_mid else False; answer(cb["id"],"🗑️ تم المسح" if ok else "⚠️ افتح الأوامر بالرد على الرسالة",not ok); return
            if a=="pin":
                ok=pin(cid,target_mid).get("ok") if target_mid else False; answer(cb["id"],"📌 تم التثبيت" if ok else "⚠️ افتح الأوامر بالرد على الرسالة",not ok); return
            if not t: answer(cb["id"],"⚠️ افتح /الاوامر بالرد على رسالة العضو حتى أحدد الهدف.",True); return
            if not can_target(cid,t["id"]): answer(cb["id"],"❌ لا يمكن تنفيذها على مشرف/مالك",True); return
            if a=="ban": r=ban(cid,t["id"]); out="🚫 تم الحظر"
            elif a=="kick": r=kick(cid,t["id"]); out="👢 تم الطرد"
            elif a=="mute": r=mute(cid,t["id"]); out="🔇 تم الكتم"
            else: r=unmute(cid,t["id"]); out="🔊 تم رفع الكتم"
            answer(cb["id"],out if r.get("ok") else "❌ فشل التنفيذ",not r.get("ok")); return
        if data.startswith("warnact:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            _,action,target_id=data.split(":",2); target_id=int(target_id)
            if action=="cancel": answer(cb["id"],"↩️ تم إلغاء الإجراء"); edit(cid,msg["message_id"],"⚠️ تم تسجيل الإنذار الثاني بدون إجراء."); return
            if not can_target(cid,target_id): answer(cb["id"],"❌ لا يمكن تنفيذها على مشرف/مالك",True); return
            fn={"mute":mute,"ban":ban,"kick":kick}.get(action); r=fn(cid,target_id) if fn else {"ok":False}
            answer(cb["id"],"✅ تم التنفيذ" if r.get("ok") else "❌ فشل التنفيذ",not r.get("ok")); edit(cid,msg["message_id"],"⚠️ تم تنفيذ الإجراء على العضو." if r.get("ok") else "❌ تعذر تنفيذ الإجراء."); return
        if data.startswith("role:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            _,op,r=data.split(":"); t,_target_mid=menu_context(cid,msg["message_id"])
            if not t: t,_target_mid=action_target_from_callback(msg)
            if not t: answer(cb["id"],"⚠️ افتح القائمة بالرد على العضو",True); return
            set_role(cid,t["id"],r,op=="add"); answer(cb["id"],"✅ تم تعديل الرتبة"); return
        if data.startswith("list:"):
            typ=data.split(":",1)[1]
            if typ=="warnings":
                rows=all_rows("SELECT user_id,count FROM warnings WHERE chat_id=? ORDER BY count DESC LIMIT 30",(cid,)); out="⚠️ <b>الإنذارات</b>\n"+(("\n".join("• <code>%s</code> — %s"%(x[0],x[1]) for x in rows)) if rows else "لا توجد إنذارات.")
            elif typ=="admins": out="👮 الأدمنية يتم جلبهم من Telegram مباشرة. استخدم /الادمنية."
            else:
                rr="special" if typ=="special" else typ
                rows=all_rows("SELECT user_id FROM roles WHERE chat_id=? AND role=?",(cid,rr)); out="📋 <b>%s</b>\n"%role_name(rr)+("\n".join("• <code>%s</code>"%x[0] for x in rows) if rows else "لا توجد بيانات.")
            send(cid,out,reply_to=msg["message_id"]); answer(cb["id"]); return
        if data=="tagall":
            rows=all_rows("SELECT user_id FROM points WHERE chat_id=? ORDER BY points DESC LIMIT 50",(cid,)); out="📣 <b>تاك للكل</b>\n"+(" ".join('<a href="tg://user?id=%s">•</a>'%x[0] for x in rows) if rows else "لا توجد أسماء محفوظة بعد."); send(cid,out); answer(cb["id"]); return
        if data=="rules":
            r=settings(cid); send(cid,"📜 <b>القوانين</b>\n"+(r["rules"] or "لم يتم تعيين قوانين بعد.")); answer(cb["id"]); return
        if data=="link":
            r=call("exportChatInviteLink",chat_id=cid); send(cid,"🔗 "+(r.get("result") if r.get("ok") else "❌ تعذر إنشاء الرابط.")); answer(cb["id"]); return
        if data=="settings":
            r=settings(cid); send(cid,"⚙️ <b>إعدادات المجموعة</b>\nالترحيب: %s\nالحماية: %s"%("مفعل" if r["welcome"] else "متوقف",sum(1 for k in PROT if prot(cid,k)))); answer(cb["id"]); return
        if data=="botperms":
            send(cid,"🔐 اجعل البوت أدمن مع: حذف الرسائل، حظر/تقييد الأعضاء، تثبيت الرسائل. بدون هذه الصلاحيات سيظهر خطأ من Telegram."); answer(cb["id"]); return
        if data=="roles:clear":
            if not is_creator(cid,uid): answer(cb["id"],"❌ للمالك فقط",True); return
            run("DELETE FROM roles WHERE chat_id=?",(cid,)); answer(cb["id"],"🧹 تم تنزيل الرتب المخصصة"); return
        if data=="welcome_menu":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            r=settings(cid); edit(cid,msg["message_id"],"👋 <b>إعدادات الترحيب</b>\nالحالة: <b>%s</b>\nالنص: <code>%s</code>"%("مفعل" if r["welcome"] else "متوقف",escape(welcome_text(cid))),kb([[btn("✅ تشغيل","welcome:on"),btn("🔕 إيقاف","welcome:off")],[btn("✏️ طريقة تغيير النص","welcome:help")],[btn("⬅️ رجوع","menu:manager")]])); answer(cb["id"]); return
        if data.startswith("welcome:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            a=data.split(":",1)[1]
            if a=="on": set_setting(cid,"welcome",1); answer(cb["id"],"👋 تم تشغيل الترحيب")
            elif a=="off": set_setting(cid,"welcome",0); answer(cb["id"],"🔕 تم إيقاف الترحيب")
            else: answer(cb["id"],"استخدم: ترحيب نص أهلاً {name}",True)
            show_menu(cid,msg["message_id"],"manager"); return
        if data=="notify_menu":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            r=settings(cid); edit(cid,msg["message_id"],"🔔 <b>الإشعارات</b>\nالحالة الحالية: <b>%s</b>"%("مفعلة" if r["notifications"] else "متوقفة"),kb([[btn("🔔 تشغيل","notify:on"),btn("🔕 إيقاف","notify:off")],[btn("⬅️ رجوع","menu:manager")]])); answer(cb["id"]); return
        if data.startswith("notify:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            a=data.split(":",1)[1]; set_setting(cid,"notifications",1 if a=="on" else 0); answer(cb["id"],"🔔 تم تحديث الإشعارات"); show_menu(cid,msg["message_id"],"manager"); return
        if data=="replies_menu":
            edit(cid,msg["message_id"],reply_list(cid),kb([[btn("➕ طريقة إضافة رد","replies_help"),btn("🗑️ حذف كل الردود","replies_clear")],[btn("🔄 تحديث","replies_menu"),btn("⬅️ رجوع","menu:manager")]])); answer(cb["id"]); return
        if data=="replies_help":
            answer(cb["id"],"اكتب: اضف كلمة نص الرد — مثال: اضف هلا هلا وغلا 🌹",True); return
        if data=="replies_clear":
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            run("DELETE FROM custom_replies WHERE chat_id=?",(cid,)); answer(cb["id"],"🗑️ تم حذف كل الردود"); show_menu(cid,msg["message_id"],"manager"); return
        if data=="music_menu":
            edit(cid,msg["message_id"],music_menu_text(),kb([[btn("🎵 مثال بحث","music:example"),btn("🔗 مثال رابط صوت","music:url")],[btn("⬅️ رجوع","menu:fun")]])); answer(cb["id"]); return
        if data.startswith("music:"):
            if data.endswith("example"): answer(cb["id"],"اكتب: اغنية كاظم الساهر",True)
            else: answer(cb["id"],"اكتب: اغنية https://site.com/song.mp3",True)
            return
        if data.startswith("clean:"):
            if not is_admin(cid,uid): answer(cb["id"],"❌ للمشرفين فقط",True); return
            kind=data.split(":",1)[1]
            if kind=="10" or kind=="all": n=clean_tracked(cid,None,10 if kind=="10" else 100)
            elif kind=="media": n=clean_tracked(cid,"media",50)
            elif kind=="forward": n=clean_tracked(cid,"forward",50)
            elif kind=="links": n=clean_tracked(cid,"links",50)
            else: n=clean_tracked(cid,None,10)
            answer(cb["id"],"🧹 تم مسح %s رسالة"%n); return
        if data.startswith("bank:"):
            act=data.split(":",1)[1]; bank_command(cid,uid,{"account":"حسابي","money":"فلوسي","salary":"راتب","luck":"حظ","invest":"استثمار","debt":"قروضي","treasure":"كنز"}.get(act,"حسابي"),None,[]); answer(cb["id"]); return
        if data.startswith("fun:"):
            fun_command(cid,uid,data.split(":",1)[1],None); answer(cb["id"]); return
        if data.startswith("xo:"):
            row=one("SELECT answer FROM game_state WHERE chat_id=? AND game=?",(cid,"xo"))
            if not row: xo_start(cid,uid); answer(cb["id"]); return
            board=json.loads(row[0]); idx=int(data.split(":",1)[1])
            if idx<0 or idx>8 or board[idx]: answer(cb["id"],"هذا المربع مستخدم",True); return
            board[idx]="X"; win=xo_winner(board)
            if not win:
                empty=[i for i,v in enumerate(board) if not v]
                if empty: board[random.choice(empty)]="O"
                win=xo_winner(board)
            if win:
                run("DELETE FROM game_state WHERE chat_id=? AND game=?",(cid,"xo")); txt="🎉 فزت!" if win=="X" else ("🤖 فاز البوت!" if win=="O" else "🤝 تعادل!")
                edit(cid,msg["message_id"],"⭕❌ <b>XO</b>\n"+txt); answer(cb["id"],txt,True); return
            run("UPDATE game_state SET answer=? WHERE chat_id=? AND game=?",(json.dumps(board),cid,"xo")); edit(cid,msg["message_id"],"⭕❌ <b>XO</b>\nدورك:",xo_board(board)); answer(cb["id"]); return
        if data.startswith("game:"):
            g=data.split(":",1)[1]
            gm={"different":"المختلف","reverse":"العكس","riddle":"حزورة","meaning":"معاني","guess":"خمن","math":"رياضيات","xo":"xo","rps":"حجر","choice":"لوخيروك","truth":"صراحة"}.get(g,g)
            game_command(cid,uid,gm,gm); answer(cb["id"]); return
        if data=="dev:stats":
            if cb["from"].get("username","").lower()!=DEVELOPER.lower(): answer(cb["id"],"❌ للمطور فقط",True); return
            r=one("SELECT COUNT(*) n FROM known_chats"); u=one("SELECT COUNT(DISTINCT user_id) n FROM points"); send(cid,"📊 <b>إحصائيات البوت</b>\nالمجموعات: <b>%s</b>\nالمستخدمون المسجلون: <b>%s</b>"%(r[0],u[0])); answer(cb["id"]); return
        if data=="dev:perms":
            r=call("getChatMember",chat_id=cid,user_id=bot_id());
            if r.get("ok"):
                x=r["result"]; p=x.get("can_delete_messages",False); b=x.get("can_restrict_members",False); i=x.get("can_invite_users",False); k=x.get("can_pin_messages",False)
                send(cid,"🧪 <b>صلاحيات البوت</b>\n🗑️ حذف: %s\n🔇 تقييد: %s\n🔗 دعوات: %s\n📌 تثبيت: %s"%(p,b,i,k))
            else: send(cid,"❌ تعذر فحص الصلاحيات.")
            answer(cb["id"]); return
        if data=="dev:check":
            r=call("getMe"); send(cid,"✅ البوت يعمل\nالاسم: <b>%s</b>\nالمعرف: <b>@%s</b>"%(escape(r.get("result",{}).get("first_name","")),escape(r.get("result",{}).get("username","")))); answer(cb["id"]); return
        if data.startswith("dev:"):
            answer(cb["id"],"⚠️ هذا الأمر يحتاج تنفيذ خارجي أو قائمة مجموعات محفوظة.",True); return
        answer(cb["id"],"❌ زر غير معروف",True)
    except Exception as e:
        print("Callback error:",repr(e)); answer(cb["id"],"❌ حدث خطأ داخلي. راجع شاشة PyDroid.",True)

# ---------------- Updates / welcome ----------------
def process(u):
    if "callback_query" in u:
        # تجاهل أزرار قديمة وصلت بعد انقطاع الشبكة حتى لا يظهر query is too old
        cb = u.get("callback_query", {})
        msg = cb.get("message") or {}
        msg_date = msg.get("date")
        if msg_date and time.time() - int(msg_date) > 25:
            return
        callback(cb); return
    m=u.get("message")
    if not m: return
    # Private whisper composition started from a deep-link button.
    try:
        if handle_private_whisper(m):
            return
    except Exception as e:
        print("Whisper error:", repr(e)); traceback.print_exc()
    # voice-note notification
    if m.get("voice") and settings(m["chat"]["id"]).get("voice_notifications",1) and m.get("from"):
        u=m["from"]; send(m["chat"]["id"],"🎙️ <b>إشعار بصمة</b>\nتم استلام بصمة صوتية من %s."%mention(u), reply_to=m.get("message_id"))
    # global-ban enforcement
    try:
        if m.get("chat",{}).get("type") in ("group","supergroup") and m.get("from",{}).get("id") and one("SELECT 1 FROM global_bans WHERE user_id=?",(m["from"]["id"],)):
            ban(m["chat"]["id"],m["from"]["id"]); delete(m["chat"]["id"],m.get("message_id")); return
    except Exception as e: print("global ban:",repr(e))
    # store known message for clean-up / activity
    try:
        current_message_for_audio[m["chat"]["id"]]=m
        text_command(m)
    except Exception as e:
        print("Message error:",repr(e)); traceback.print_exc()
    # welcome + join notifications
    if m.get("new_chat_members"):
        for u in m["new_chat_members"]:
            send_welcome(m["chat"]["id"],u)
            if settings(m["chat"]["id"])["notifications"]:
                send(m["chat"]["id"],"🔔 انضم عضو جديد: %s"%mention(u))
    if m.get("left_chat_member") and settings(m["chat"]["id"])["notifications"]:
        send(m["chat"]["id"],"🔔 غادر المجموعة: %s"%mention(m["left_chat_member"]))

# ---------------- Main loop ----------------
def main():
    init_db()
    print("⚡ جاري تشغيل البوت v13...")
    print("ℹ️ أوامر الدردشة العادية سريعة؛ أوامر الصوت/البحث قد تحتاج وقتاً بسبب التحميل من الإنترنت.")
    print("🔎 أفحص اتصال Telegram والتوكن قبل بدء الاستقبال...")

    # إذا كان للبوت Webhook قديم، getUpdates لن يعمل. نحذفه تلقائياً.
    try:
        wh = call("deleteWebhook", drop_pending_updates=True)
        if wh.get("ok"):
            print("✅ تم التأكد من عدم وجود Webhook يمنع استقبال الرسائل.")
        else:
            print("⚠️ تعذر حذف/فحص Webhook:", wh.get("description", "غير معروف"))
    except Exception as e:
        print("⚠️ خطأ أثناء فحص Webhook:", e)

    # اتصال أولي مع إعادة المحاولة تلقائياً عند انقطاع الإنترنت.
    retry = 0
    while True:
        try:
            r=call("getMe")
            if r.get("ok"):
                print("✅ تم الاتصال بـ Telegram بنجاح.")
                print("🤖 Bot started: @"+r["result"].get("username","unknown"))
                break
            if r.get("network_error"):
                retry += 1
                wait=min(20, max(2, 2 ** min(retry-1, 4)))
                print("❌ لا يوجد اتصال بالإنترنت أو لا يمكن الوصول إلى Telegram.")
                print("🔄 سأحاول إعادة الاتصال بعد %d ثواني..." % wait)
                time.sleep(wait)
                continue
            desc = r.get("description", "خطأ غير معروف")
            print("❌ Telegram API رفض الاتصال:", desc)
            if "401" in str(desc) or "Unauthorized" in str(desc):
                print("🔑 التوكن غير صحيح/ملغى. يلزم توكن صالح من BotFather؛ لا يمكن تجاوز رفض Telegram للتوكن.")
                return
            if "409" in str(desc) or "Conflict" in str(desc):
                print("⚠️ يوجد تشغيل آخر للبوت أو تعارض مؤقت. سأعيد المحاولة بدل إغلاق البرنامج.")
            retry += 1
            wait = min(30, max(3, 2 ** min(retry, 5)))
            print("🔄 لن أغلق البوت؛ سأعيد الاتصال بعد %d ثوانٍ..." % wait)
            time.sleep(wait)
            continue
        except KeyboardInterrupt:
            print("⛔ تم إيقاف البوت."); return
        except Exception as e:
            retry += 1
            wait=min(5, retry)
            print("⚠️ خطأ أثناء الاتصال: %s" % e)
            print("🔄 إعادة المحاولة بعد %d ثواني..." % wait)
            time.sleep(wait)

    offset=0
    retry=0
    while True:
        try:
            r=call("getUpdates",offset=offset,timeout=20,allowed_updates=json.dumps(["message","callback_query"]))
            if not r.get("ok"):
                if r.get("network_error"):
                    retry += 1
                    wait=min(20, max(2, 2 ** min(retry-1, 4)))
                    print("\n🌐 انقطع اتصال الإنترنت / Telegram.")
                    print("⚠️ %s" % r.get("description","Network unreachable"))
                    print("🔄 البوت ما راح ينغلق؛ محاولة إعادة الاتصال بعد %d ثواني..." % wait)
                    time.sleep(wait)
                    continue
                retry=0
                desc = r.get("description", "خطأ غير معروف")
                print("❌ Telegram API error:", desc)
                if "409" in str(desc) or "Conflict" in str(desc):
                    print("⚠️ تعارض getUpdates: يوجد تشغيل آخر لنفس البوت. أوقف كل النسخ الأخرى. سأعيد المحاولة بعد 3 ثوانٍ.")
                    time.sleep(3)
                elif "401" in str(desc) or "Unauthorized" in str(desc):
                    print("🔑 التوكن غير صحيح أو تم إلغاؤه من BotFather. لا يمكن للبوت استقبال رسائل حتى يتم وضع توكن جديد.")
                    time.sleep(0.05)
                else:
                    retry += 1
                    wait = min(30, max(2, 2 ** min(retry, 5)))
                    print("🔄 إعادة المحاولة بعد %d ثواني..." % wait)
                    time.sleep(wait)
                continue

            # الاتصال عاد، نرجع زمن الانتظار إلى الطبيعي.
            if retry:
                print("\n✅ رجع الاتصال بالإنترنت. البوت مستمر بالعمل.")
                retry=0
            for u in r.get("result",[]):
                # احفظ التحديث التالي قبل المعالجة حتى لا يتكرر نفس التحديث للأبد.
                offset=u["update_id"]+1
                try:
                    if "message" in u:
                        _m=u["message"]
                        _txt=_m.get("text") or ("[media]" if any(k in _m for k in ("photo","sticker","document","video","voice","animation")) else "[no text]")
                        print("📩 تحديث وارد | chat=%s | text=%s" % (_m.get("chat",{}).get("id","?"), str(_txt)[:80]))
                    elif "callback_query" in u:
                        print("🔘 تحديث زر وارد")
                    process(u)
                except KeyboardInterrupt:
                    raise
                except BaseException as e:
                    # لا تسمح لخطأ في أمر/زر واحد بإيقاف البوت بالكامل.
                    print("⚠️ خطأ أثناء معالجة تحديث؛ البوت سيستمر:", repr(e)); traceback.print_exc()
                    try:
                        time.sleep(0.05)
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("⛔ تم إيقاف البوت."); break
        except KeyboardInterrupt:
            print("⛔ تم إيقاف البوت يدويًا.")
            break
        except BaseException as e:
            # حلقة الحماية الأخيرة: أخطاء الشبكة وأخطاء وقت التشغيل لا تنهي البرنامج.
            retry += 1
            wait=min(5, max(1, retry))
            print("⚠️ خطأ في الحلقة الرئيسية؛ لن يتوقف البوت:", repr(e))
            print("🔄 إعادة المحاولة بعد %d ثوانٍ..." % wait)
            try:
                time.sleep(wait)
            except Exception:
                pass

if __name__=="__main__": main()
