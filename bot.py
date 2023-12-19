from typing import Optional
import discord
from discord.ext import commands
import sqlite3
#import aiosqlite
import os


description = 'a discord todo bot running on Azure Web App'

TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

con = sqlite3.connect(':memory:')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS todo (
    task TEXT NOT NULL,
    user_id INTEGER NOT NULL
)''')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.group()
async def todo(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not todo')


@todo.command(name='add')
async def add(ctx, *msg):
    msg = ' '.join(msg)
    cur.execute('INSERT INTO todo (task, user_id) VALUES(?, ?)', [msg, ctx.author.id])
    con.commit()
    await ctx.send(f'Successfully added `{msg}` to your todo list')


@todo.command(name='remove')
async def remove(ctx, index: int):
    index -= 1
    cur.execute('SELECT rowid, task FROM todo WHERE user_id = ? ORDER BY rowid LIMIT 1 OFFSET ?', [ctx.author.id, index])
    entry = cur.fetchone()
    cur.execute('DELETE FROM todo WHERE rowid = ?', [entry[0]])

    await ctx.send(f'Successfully completed `{entry[1]}`!')


@todo.command(name='list')
async def list(ctx):
    cur.execute('SELECT task FROM todo WHERE user_id = ? ORDER BY rowid', [ctx.author.id])
    result = cur.fetchall()
    content = f'You have {len(result)} pending tasks:\n'
    for i, c in enumerate(result):
        content += f'{i}. {c[0]}\n'
    await ctx.send(content)


bot.run(TOKEN)

cur.close()
con.close()
