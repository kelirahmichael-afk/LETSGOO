# Discord Member Bot

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your bot token as an environment variable:
   ```
   export DISCORD_TOKEN="your_token_here"
   ```

3. Generate members:
   ```
   python generate_members.py
   ```

4. Run the bot:
   ```
   python bot.py
   ```

## Commands
| Command | Description |
|---|---|
| `!put <server_id>` | Load all members from members.json into that server |
| `!list <server_id>` | Preview 5 random members |
| `!clear <server_id>` | Wipe all members for that server |
| `!help` | Show all commands |

## Files
- `bot.py` — the bot
- `generate_members.py` — generates members.json
- `members.json` — the generated members
- `requirements.txt` — dependencies

## DO NOT push to GitHub
- `.env` — contains your secret token
- `servers.db` — local database
