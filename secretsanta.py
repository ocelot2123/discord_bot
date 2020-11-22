import discord
from discord.ext import commands
import mysql.connector as mysql
from mysql.connector import errorcode
from dotenv import load_dotenv
import random
import os
import time

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
#SQL stuff
#SQL statement for adding to the people table
add_people = """INSERT INTO people
				(disc_id, disc_name, first_name, last_name, address, phone_num, description, gift_advisor)
				VALUES ({disc_id}, {disc_name}, {first_name}, {last_name}, {address}, {phone_num}, {description}, {gift_advisor})
				ON DUPLICATE KEY UPDATE disc_name={disc_name}, first_name={first_name}, last_name={last_name}, address={address}, phone_num={phone_num}, description={description}, gift_advisor={gift_advisor}"""


class SecretSanta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command()
    async def nodrawsanta(self, ctx):
        db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
                                host = '127.0.0.1',
                                database = 'mydatabase',
                                auth_plugin= 'caching_sha2_password')

        cursor = db.cursor()
        people_list = list()
        dup_list = list()
        dup_dup_list = list()
        select_sql = "SELECT disc_id FROM people;"
        update_recip_sql = "UPDATE people SET recipient = {0} WHERE disc_id = {1}"
        update_santa_sql = "UPDATE people SET santa = {0} WHERE disc_id = {1}"
        cursor.execute(select_sql)
        for res in cursor:
            for disc_id in res:
                people_list.append(disc_id)
                dup_list.append(disc_id)
                dup_dup_list.append(disc_id)

        for people in dup_dup_list:
            recip_id = ""
            if len(dup_list) == 2 and len(list(set(people_list) & set(dup_list))) > 0:
                if people != list(set(people_list) & set(dup_list))[0]:
                    recip_id = list(set(people_list) & set(dup_list))[0]
                else:
                    for recip in dup_list:
                        if recip != people:
                            recip_id = recip
            while recip_id == people or recip_id == "":
                recip_id = random.choice(dup_list)

            dup_list.remove(recip_id)
            people_list.remove(people)
            cursor.execute(update_recip_sql.format(recip_id, people))
            cursor.execute(update_santa_sql.format(people, recip_id))

        db.commit()
        cursor.close()
        db.close()
        await ctx.send("ok")

    @commands.command()
    async def nosendinfo(self, ctx):
        db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
                                host = '127.0.0.1',
                                database = 'mydatabase',
                                auth_plugin= 'caching_sha2_password')
        cursor = db.cursor()
        select_sql = "SELECT disc_id, recipient FROM people;"
        select_santa_sql = "SELECT * FROM people WHERE disc_id = {0}"
        cursor.execute(select_sql)
        user_recip_pair = list()
        for res in cursor:
            user_recip_pair.append(res)

        cursor = db.cursor()
        for pair in user_recip_pair:
            user_id = pair[0]
            recip_id = pair[1]
            user = await self.bot.fetch_user(user_id)

            cursor.execute(select_santa_sql.format(recip_id))
            for res in cursor:
                await user.send("Full Name:\n" + res[2] + " " + res[3])
                await user.send("Address:\n" + res[4])
                await user.send("Phone number:\n" + res[5])
                await user.send("Description:\n" + res[6])
                await user.send("Please consult their gift advisor if you have questions on what to get them:\n" + res[7])
        
        await ctx.send("done")
        cursor.close()
        db.close()

    @commands.command()
    async def nosantalist(self, ctx):
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

    @commands.command()
    async def nosecretsanta(self, ctx):

        channel_type = ctx.channel.type
        if channel_type == discord.ChannelType.private:
            data_people = dict()
            data_people['disc_id'] = ctx.author.id
            """
            data_people dict format
            data_people['disc_id'] = discord id int
            data_people['disc_name'] = discord name string
            data_people['first_name'] = first name string
            data_people['last_name'] = lats name string
            data_people['address'] = address string
            data_people['phone_num'] = phone num string
            data_people['description'] = description string
            data_people['gift_advisor'] = gift advisor string
            """

            s = "Hi there, I will be asking you a series of questions about your personal details so your secret santa can send their gift to you! "
            s += "Feel free to call this function again if you need to change anything about your personal details.\n\n\n"
            s += "Data privacy: data will be deleted after this thing is over (I can stream that or something), but I will not be encrypting the data for privacy because I'm too lazy, "
            s += "but I will be the only one who has access to the data and you just have to take my word that I wont do anything with it. -Ed"
            await ctx.author.send(s)


            data_people["disc_name"] = "\'" + ctx.author.name + "\'"
            channel_id = ctx.channel.id
            time.sleep(3)
            def check(msg):
                return msg.channel.id == channel_id and msg.author == ctx.author
            
            await ctx.author.send("Please enter your first name:")
            msg = await self.bot.wait_for('message', check=check)
            data_people["first_name"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            await ctx.author.send("Please enter your last name:")
            msg = await self.bot.wait_for('message', check=check)
            data_people["last_name"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            await ctx.author.send("Please enter your full address:")
            msg = await self.bot.wait_for('message', check=check)
            data_people["address"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            await ctx.author.send("Please enter your phone number (with country code please):")
            msg = await self.bot.wait_for('message', check=check)
            data_people["phone_num"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            await ctx.author.send("Please write a short description of what you like so your secret santa can have an idea of what to get you:")
            msg = await self.bot.wait_for('message', check=check)
            data_people["description"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            await ctx.author.send("Please designate a gift advisor that your secret santa can consult with for what to get you (reply with n if you don't want to input one):")
            msg = await self.bot.wait_for('message', check=check)
            if msg.content.lower() == 'n':
                data_people["gift_advisor"] = "\'N/A\'"
            else:
                data_people["gift_advisor"] = "\'" + msg.content + "\'"
            time.sleep(1.5)
            
            db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
                                host = '127.0.0.1',
                                database = 'mydatabase',
                                auth_plugin= 'caching_sha2_password')

            cursor = db.cursor()
            try:
                cursor.execute(add_people.format(**data_people))
                await ctx.author.send("Information received")

            except Exception as err:
                await ctx.author.send("oops something went wrong, send this to Ed:\n" + err)
                print(err)

            db.commit()
            cursor.close()
            db.close()

def setup(bot):
    bot.add_cog(SecretSanta(bot))