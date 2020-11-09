import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import mysql.connector as mysql
from mysql.connector import errorcode
import time

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")

bot = commands.Bot(command_prefix = "!")

@bot.command()
async def santalist(ctx):
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

	cursor = db.cursor()

	sql = "SELECT first_name FROM people;"
	cursor.execute(sql)
	out_s = "Heres a list of people who signed up:\n"
	for i, res in enumerate(cursor, 1):
		for first_name in res:
			out_s += str(i) + ". " + first_name + "\n"
	await ctx.send(out_s)

	cursor.close()
	db.close()

bot.run(DISCORD_TOKEN)