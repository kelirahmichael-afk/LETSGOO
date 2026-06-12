import json
import random
from datetime import datetime, timedelta

adjectives = ['shadow','pixel','neon','void','cosmic','silent','blazing','crystal',
              'frozen','hyper','dark','swift','lunar','stellar','iron','ghost',
              'cyber','acid','storm','wild']
nouns = ['wolf','queen','knight','panda','viper','fox','eagle','shark','titan',
         'monk','ghost','ninja','dragon','rebel','sniper','raven','blade','hawk',
         'rogue','comet']
roles = ['Owner','Admin','Moderator','Booster','Member','Member','Member','New']
statuses = ['online','idle','dnd','offline']

def random_date():
    days_ago = random.randint(1, 1500)
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

def generate_member():
    username = random.choice(adjectives) + '_' + random.choice(nouns)
    if random.random() > 0.5:
        username += str(random.randint(1, 9999))
    return {
        "username": username,
        "tag": f"#{random.randint(1000, 9999)}",
        "status": random.choice(statuses),
        "role": random.choice(roles),
        "joined": random_date(),
        "messages": random.randint(0, 15000)
    }

def generate(count=1000):
    members = [generate_member() for _ in range(count)]
    with open("members.json", "w") as f:
        json.dump(members, f, indent=2)
    print(f"✅ Generated {count} members → members.json")

generate(1000)
