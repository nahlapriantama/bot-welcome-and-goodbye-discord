import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
GOODBYE_CHANNEL_ID = int(os.getenv("GOODBYE_CHANNEL_ID"))

# === INTENTS ===
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================================
#   FUNGSI MEMBUAT GAMBAR (STYLE FIX PERSIS SEPERTI CONTOH)
# ==========================================================
async def create_card(title_text, username, message_text, avatar_url):
    width, height = 900, 500
    img = Image.new("RGB", (width, height), "#0d0d0d")
    draw = ImageDraw.Draw(img)

    # FONT
    font_title = ImageFont.truetype("assets/font.ttf", 65)
    font_name = ImageFont.truetype("assets/font.ttf", 55)
    font_msg = ImageFont.truetype("assets/font.ttf", 40)

    # === AMBIL AVATAR ===
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avatar_bytes = await resp.read()

    pfp = Image.open(io.BytesIO(avatar_bytes)).convert("RGB")
    pfp = pfp.resize((240, 240))

    # MASK LINGKARAN
    mask = Image.new("L", (240, 240), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((0, 0, 240, 240), fill=255)

    # Avatar center
    avatar_x = (width - 240) // 2
    avatar_y = 30
    img.paste(pfp, (avatar_x, avatar_y), mask)

    # Helper: draw text centered
    def center(text, y, font):
        w, h = draw.textbbox((0, 0), text, font=font)[2:]
        draw.text(((width - w) / 2, y), text, font=font, fill="white")

    # === DRAW TEXT (SESUAI FORMAT YANG DIINGINKAN) ===
    center(title_text, 300, font_title)
    center(username, 370, font_name)
    center(message_text, 430, font_msg)

    # Output file
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out

# ==========================================================
#   EVENT MEMBER JOIN
# ==========================================================
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    img = await create_card(
        "WELCOME",
        member.name,
        "Selamat datang di NexCore Moga Betah ya",
        member.display_avatar.url
    )

    await channel.send(
        f"Selamat datang {member.mention}! 🎉",
        file=discord.File(img, "welcome.png")
        
    )

# ==========================================================
#   EVENT MEMBER LEAVE
# ==========================================================
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(GOODBYE_CHANNEL_ID)

    img = await create_card(
        "GOODBYE!",
        member.name,
        "NITIP GORENGAN SAMA KOPI SATU YA!",
        member.display_avatar.url
    )

    await channel.send(
        f"Selamat Berbahagia dengan pilihan mu ya {member.name}! 👋",
        file=discord.File(img, "goodbye.png")
    )

# ==========================================================
#   RUN BOT
# ==========================================================
bot.run(TOKEN)
