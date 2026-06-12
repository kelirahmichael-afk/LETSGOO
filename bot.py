import discord
from discord.ext import commands
import json
import sqlite3
import os
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable not set!")

DB_FILE = "servers.db"
MEMBERS_FILE = "members.json"

# ── Database setup ───────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id   TEXT NOT NULL,
            username    TEXT NOT NULL,
            tag         TEXT,
            status      TEXT,
            role        TEXT,
            joined      TEXT,
            messages    INTEGER,
            added_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

def insert_members(server_id: str, members: list[dict]) -> int:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    rows = [
        (
            server_id,
            m["username"],
            m.get("tag"),
            m.get("status"),
            m.get("role"),
            m.get("joined"),
            m.get("messages", 0),
        )
        for m in members
    ]
    cur.executemany(
        "INSERT INTO members (server_id, username, tag, status, role, joined, messages) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    con.commit()
    inserted = cur.rowcount
    con.close()
    return inserted

def count_for_server(server_id: str) -> int:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM members WHERE server_id = ?", (server_id,))
    n = cur.fetchone()[0]
    con.close()
    return n

def clear_server(server_id: str) -> int:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("DELETE FROM members WHERE server_id = ?", (server_id,))
    deleted = cur.rowcount
    con.commit()
    con.close()
    return deleted

def get_sample(server_id: str, limit: int = 5) -> list[dict]:
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM members WHERE server_id = ? ORDER BY RANDOM() LIMIT ?",
        (server_id, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

# ── Bot setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    init_db()
    print(f"✅  Logged in as {bot.user} (ID: {bot.user.id})")
    print("──────────────────────────────────")

# ── Commands ─────────────────────────────────────────────────────────────────

@bot.command(name="put")
async def put_members(ctx, server_id: str = None):
    """!put <server_id>  →  Load members.json into that server's slot."""
    if server_id is None:
        await ctx.send("⚠️  Usage: `!put <server_id>`")
        return

    if not os.path.exists(MEMBERS_FILE):
        await ctx.send(f"❌  `{MEMBERS_FILE}` not found. Run your generator first!")
        return

    async with ctx.typing():
        with open(MEMBERS_FILE, "r") as f:
            members = json.load(f)

        inserted = insert_members(server_id, members)
        total = count_for_server(server_id)

    role_counts: dict[str, int] = {}
    for m in members:
        role_counts[m.get("role", "Unknown")] = role_counts.get(m.get("role", "Unknown"), 0) + 1

    role_lines = "\n".join(
        f"  `{role:<12}` — {count:,}" for role, count in sorted(role_counts.items())
    )

    embed = discord.Embed(
        title="✅  Members loaded",
        color=0x5865F2,
        timestamp=datetime.utcnow(),
    )
    embed.add_field(name="Server ID", value=f"`{server_id}`", inline=True)
    embed.add_field(name="Inserted", value=f"**{inserted:,}**", inline=True)
    embed.add_field(name="Total in DB", value=f"**{total:,}**", inline=True)
    embed.add_field(name="Roles breakdown", value=role_lines, inline=False)
    embed.set_footer(text="Use !list <server_id> to preview · !clear <server_id> to reset")

    await ctx.send(embed=embed)


@bot.command(name="list")
async def list_members(ctx, server_id: str = None):
    """!list <server_id>  →  Show 5 random members for that server."""
    if server_id is None:
        await ctx.send("⚠️  Usage: `!list <server_id>`")
        return

    sample = get_sample(server_id, 5)
    total = count_for_server(server_id)

    if not sample:
        await ctx.send(f"❌  No members found for server `{server_id}`. Try `!put {server_id}` first.")
        return

    STATUS_EMOJI = {"online": "🟢", "idle": "🟡", "dnd": "🔴", "offline": "⚫"}

    lines = []
    for m in sample:
        emoji = STATUS_EMOJI.get(m["status"], "⚫")
        lines.append(
            f"{emoji} **{m['username']}**{m['tag']}  ·  `{m['role']}`  ·  {m['messages']:,} msgs"
        )

    embed = discord.Embed(
        title=f"👥  Sample members — `{server_id}`",
        description="\n".join(lines),
        color=0x57F287,
    )
    embed.set_footer(text=f"{total:,} total members stored for this server")
    await ctx.send(embed=embed)


@bot.command(name="clear")
async def clear_members(ctx, server_id: str = None):
    """!clear <server_id>  →  Remove all members for that server from the DB."""
    if server_id is None:
        await ctx.send("⚠️  Usage: `!clear <server_id>`")
        return

    deleted = clear_server(server_id)
    await ctx.send(f"🗑️  Cleared **{deleted:,}** members from server `{server_id}`.")


@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="📖  Commands", color=0xFEE75C)
    embed.add_field(name="`!put <server_id>`", value="Load all members from `members.json` into the DB under that server ID.", inline=False)
    embed.add_field(name="`!list <server_id>`", value="Preview 5 random members stored for that server.", inline=False)
    embed.add_field(name="`!clear <server_id>`", value="Delete all stored members for that server.", inline=False)
    await ctx.send(embed=embed)


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(TOKEN)
