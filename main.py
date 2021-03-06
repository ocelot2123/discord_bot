import discord
from discord.ext import commands
from utils import *
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

startup_extensions = ["amongusbot", "secretsanta"]
bot = commands.Bot(command_prefix = '!')

@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type = discord.ActivityType.listening, name = "Beep boop I'm red and you're SUS"))

	create_table = """CREATE TABLE people (
		disc_id BIGINT NOT NULL,
		disc_name varchar(30) NOT NULL,
		first_name varchar(20) NOT NULL,
		last_name varchar(20) NOT NULL,
		address varchar(150) NOT NULL,
		phone_num varchar(20) NOT NULL,
		description varchar(200) NOT NULL,
		gift_advisor varchar(40) NOT NULL,
		santa BIGINT DEFAULT NULL,
		recipient BIGINT DEFAULT NULL,
		PRIMARY KEY (disc_id))"""

	#connect to DB	
	"""
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

	cursor = db.cursor()

	try:
		print("Creating table")
		cursor.execute(create_table)
	except mysql.Error as err:
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			print("table exists.")
		else:
			print(err.msg)
	else:
		print("OK")
	db.close()
	cursor.close()
	"""


@bot.command()
async def emojiname(ctx, emoji):
	await ctx.send(get_name(emoji))


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(DISCORD_TOKEN)
