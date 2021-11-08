import re
import time
import random
import string
import asyncio
import requests
import websockets

cache = {
  "username": False,
  "password": False
  }

""" Function to generate a randomized account """
def generate():
    email = "".join([random.choice(string.ascii_lowercase) for x in range(6)])
    cache["username"] = "".join([random.choice(string.ascii_lowercase + string.digits) for x in range(20)])
    cache["password"] = random.choice(string.ascii_lowercase)
    data = requests.post("https://chatango.com/signupdir", data={"email": f"{random.randint(0, 99999999)}@{random.randint(0, 99999999)}.{email}", "login": cache["username"], "password": cache["password"], "password_confirm": cache["password"], "storecookie": "on", "checkerrors": "yes"}).text
    if "Download Message Catcher" in data: return True
    else: return False

""" The authentication token of the account used to log in to private messages """
def token(username, password):
    try:
      get = requests.post("https://chatango.com/login", data={"user_id": username, "password": password, "storecookie": "on", "checkerrors": "yes"}).cookies.get("auth.chatango.com", False)
      return get
    except Exception as error: return False

""" Function to convert milliseconds of time in to a readable format """
def convert(data, state=False):
    if state: x = float(data) - time.time()
    else: x = time.time() - float(data)
    minute, hour, day = 60, 3600, 86400
    seconds, minutes, hours, days = int(x % minute), int((x % hour) / minute), int((x % day) / hour), int(x / day)
    string = ""
    if days > 0: string += f"{days}" + (" day" if days == 1 else " days") + (" and " if hours > 0 and minutes == 0 and seconds == 0 else
                                                                             " and " if minutes > 0 and hours == 0 and seconds == 0 else
                                                                             " and " if seconds > 0 and hours == 0 and minutes == 0 else
                                                                             ", " if days > 0 and hours > 0 else
                                                                             ", " if hours > 0 and minutes > 0 else
                                                                             ", " if minutes > 0 and seconds > 0 else "")
    if hours > 0: string += f"{hours}" + ( " hour" if hours == 1 else " hours") + (" and " if minutes > 0 and seconds == 0 else
                                                                                   " and " if seconds > 0 and minutes == 0 else
                                                                                   ", " if minutes > 0 else "")
    if minutes > 0: string += f"{minutes}" + (" minute" if minutes == 1 else " minutes") + (" and " if seconds > 0 else "")
    if seconds > 0: string += f"{seconds}" + (" second" if seconds == 1 else " seconds")
    if string: return string

""" Function to log in to private messages using the details randomized or provided to check an account """
async def private(data):
  username = cache["username"]
  password = cache["password"]
  authenticate = token(username, password)
  if authenticate:
    try:
      async with websockets.connect("ws://c1.chatango.com:8080/", origin="https://st.chatango.com", ping_interval=None, ping_timeout=None) as client:
        await client.send(f"tlogin:{authenticate}:2\x00")
        while True:
          frame = await client.recv()
          capture = frame.split(":")
          command, handle = capture[0].strip("\r\n\x00"), capture[1:]
          if command:
            if command == "OK": await client.send(f"track:{data}\r\n")
            elif command == "connect":
              status = handle[2].strip("\r\n\x00")
              if status == "invalid": print(f"{data.capitalize()} is invalid.")
              await client.close()
            elif command == "track":
              status = handle[2].strip("\r\n\x00")
              if status == "offline":
                track = convert(handle[1])
                print(f"{data.capitalize()} has been offline for {track}.")
              elif status == "online" and handle[1] != "0":
                track = convert(time.time() + int(handle[1]) * 60, True)
                print(f"{data.capitalize()} is online but has been idle for {track}.")
              elif status == "app": print(f"{data.capitalize()} is online from the mobile app.")
              elif status == "invalid": print(f"{data.capitalize()} does not exist or is a group.")
              else: print(f"{data.capitalize()} is online.")
              await client.close()
    except websockets.exceptions.ConnectionClosedError: pass
  else: print("Account authentication failed, please restart."); exit()

generator = input("Generate a dummy account? (Y/N)\n")
if generator.lower() in ["y", "ye", "yes", "1"]:
  make = generate()
  if make: print(f'Using dummy account - ({cache["username"]}: {cache["password"]})\n')
  else: print("Dummy account creation failed, please restart."); exit()
else:
  if cache["username"] and cache["password"]: print(f'Using dummy account - ({cache["username"]})\n')
  else:
    make = generate()
    if make: print(f'No manual account input, using dummy account - ({cache["username"]}: {cache["password"]})\n')
    else: print("No manual account input but dummy account creation failed, please restart."); exit()

print("Type [exit] to stop.")

while True:
  stalk = input("Username: ")
  if stalk == "[exit]": break; exit()
  else:
    check = re.search("([A-Za-z0-9]{1,20})", stalk)
    if check:
      seek = private(check[1])
      asyncio.run(seek)
