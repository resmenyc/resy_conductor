import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os
from utils import Utils
import sys
from database import Database
from datetime import datetime
import pytz

utils = Utils()
database = Database()

load_dotenv()

bot = Bot(command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    utils.thread_log("Discord bot ready!")

# a command to do ping pong
@bot.command(name='ping', help='Responds with Pong!')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='total', help='Total number of reservations')
async def total(ctx):
    await ctx.send(f"Total number of reservations: {len(database.get_reservations_safe())}")

@bot.command(name='today', help='Total reservations today so far')
async def today(ctx):
    reservations = get_today_ress()
    
    await ctx.send(f"Total number of reservations so far today: {len(reservations)}")
    return

def get_today_ress():
    est = pytz.timezone("America/New_York")
    current_dt = datetime.now(est)
    
    start_of_day_ts = current_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_day_epoch = int(start_of_day_ts.timestamp())
    
    reservations = database.get_reservations_safe(query={"createdAt": {"$gt": start_of_day_epoch}})
    reservations_new = database.get_reservations_safe(query={"createdAt": {"$gt": str(start_of_day_ts)}})
    
    for rn in reservations_new:
        reservations.append(rn)
    
    return reservations

@bot.command(name='breakdown', help='Breakdown of reservations today')
async def breakdown(ctx):
    reservations = get_today_ress()
    
    breakdown = {}
    
    for res in reservations:
        if res["venue_name"] not in breakdown:
            breakdown[res["venue_name"]] = 1
        else:
            breakdown[res["venue_name"]] += 1
    
    embed = discord.Embed(title="Reservation Stats", description="Breakdown of todays reservations", color=discord.Color.light_gray())
    for key in breakdown.keys():
        embed.add_field(name=key, value=breakdown[key], inline=False)
        
    await ctx.send(embed=embed)

@bot.command('total_breakdown', help="All time reservation breakdown")
async def total_breakdown(ctx):
    reservations = database.get_reservations_safe()
    
    breakdown = {}
    
    for res in reservations:
        if res["venue_name"] not in breakdown:
            breakdown[res["venue_name"]] = 1
        else:
            breakdown[res["venue_name"]] += 1
    
    embed = discord.Embed(title="Reservation Stats", description="Breakdown of all time reservations", color=discord.Color.light_gray())
    for key in breakdown.keys():
        embed.add_field(name=key, value=breakdown[key], inline=False)
        
    await ctx.send(embed=embed)

if __name__ == '__main__':
    utils.thread_log("Discord bot to do some fun stuff")
    if not os.getenv("DISCORD_TOKEN"):
        utils.thread_error("No discord token provided")
        sys.exit(1)
    
    bot.run(os.getenv("DISCORD_TOKEN"))