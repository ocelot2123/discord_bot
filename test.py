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

table = """CREATE TABLE people (
	disc_id varchar(30) NOT NULL,
	disc_name varchar(30) NOT NULL,
	first_name varchar(15) NOT NULL,
	last_name varchar(15) NOT NULL,
	address varchar(100) NOT NULL,
	phone_num varchar(20) NOT NULL,
	description varchar(300) NOT NULL,
	gift_advisor varchar(15) NOT NULL,
	santa varchar(30) DEFAULT NULL,
	recipient varchar(30) DEFAULT NULL,
	PRIMARY KEY (disc_id))"""

add_people = """INSERT INTO people
				(disc_id, first_name, last_name, address, phone_num, description, gift_advisor)
				VALUES (%(disc_id)s, %(first_name)s, %(last_name)s, %(address)s, %(phone_num)s, %(description)s, %(gift_advisor)s)
				ON DUPLICATE KEY UPDATE first_name=%(first_name)s, last_name=%(last_name)s, address=%(address)s, phone_num=%(phone_num)s, description=%(description)s, gift_advisor=%(gift_advisor)s"""
	
db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
						host = '127.0.0.1',
						database = 'mydatabase',
						auth_plugin= 'caching_sha2_password')

cursor = db.cursor()

try:
	print("Creating table")
	cursor.execute(table)
except mysql.Error as err:
	if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
		print("table exists.")
	else:
		print(err.msg)
else:
	print("OK")


@bot.command()
#secretsanta
async def ping(ctx):
	channel_type = ctx.channel.type
	if channel_type == discord.ChannelType.private:
		data_people = dict()
		data_people["disc_id"] = ctx.author.id
		data_people["disc_name"] = ctx.author.name
		channel_id = ctx.channel.id
		def check(msg):
			return msg.channel.id == channel_id and msg.author == ctx.author
		
		await ctx.author.send("Please enter your first name:")
		msg = await bot.wait_for('message', check=check)
		data_people["first_name"] = msg.content
		time.sleep(1.5)
		await ctx.author.send("Please enter your last name:")
		msg = await bot.wait_for('message', check=check)
		data_people["last_name"] = msg.content
		time.sleep(1.5)
		await ctx.author.send("Please enter your address:")
		msg = await bot.wait_for('message', check=check)
		data_people["address"] = msg.content
		time.sleep(1.5)
		await ctx.author.send("Please enter your phone number:")
		msg = await bot.wait_for('message', check=check)
		data_people["phone_num"] = msg.content
		time.sleep(1.5)
		await ctx.author.send("Please write a short description of what you like so your secret santa can have an idea of what to get you:")
		msg = await bot.wait_for('message', check=check)
		data_people["description"] = msg.content
		time.sleep(1.5)
		await ctx.author.send("Please designate a gift advisor that your secret santa can consult with for what to get you (reply with n if you don't want to input one):")
		msg = await bot.wait_for('message', check=check)
		data_people["gift_advisor"] = msg.content
		time.sleep(1.5)
		
		for keys, values in data_people.items():
			print(keys)
			print(values)

db.commit()
cursor.close()
db.close()
bot.run(DISCORD_TOKEN)
