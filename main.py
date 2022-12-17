import websocket
import threading
import requests
import base64
import random
import utils
import json
import time
import zlib
import os
import re

tregex = re.compile(r"(\w|-){24}\.(\w|-){6}\.(\w|-){16,}".encode())
iregex = re.compile(r"https:\/\/discord\.gg\/[A-Za-z0-9]{2,16}".encode())
nregex = re.compile(r"https:\/\/discord\.gift\/[A-Za-z0-9]{16}".encode())
pregex = re.compile(r"[A-Z]{16}".encode())


def safe(x):
    # print(x)
    try:
        return dict(x)
    except:
        return {}


def b64decode(x):
    if type(x) == str:
        x = x.encode()
    return base64.b64decode(x + (b"=" * (-len(x) % 4)))


def istoken(x):
    chars = ".azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789_-"
    #print("a...")
    for y in x:
        if y not in chars:
            return False
    #print("b...")
    if x.count(".") != 2:
        return False
    y = x.split(".")
    #print("c...")
    try:
        #print("c-0...")
        int(b64decode(y[0]))
        #print("c-1...")
        b64decode(
            y[1])  #assert int.from_bytes(b64decode(y[1]), "big") > 1431475200
        # print("c-2...")
        # b64decode(y[2])
        #print("waw !")
    except Exception as e:
        #print("nooooo", e)
        return False
    return True


def has_token(xy):
    # print(xy)
    if isinstance(xy, str):
        xy = xy.encode()
    try:
        for x in tregex.finditer(xy):
            x = x.group()
            # print("Maybe :", x)
            if istoken(x.decode()):
                # print("NEW TOKEN :", x.decode())
                # with open("waw.txt", "a") as f:
                #     f.write(x.decode()+"\n")
                yield x.decode()
    except Exception as e:
        pass
        # print('Error:', e)


def has_invite(xy):
    if isinstance(xy, str):
        xy = xy.encode()
    try:
        for x in iregex.finditer(xy):
            # print(x)
            yield x.group().decode()[19:]
    except Exception as e:
        pass
        # print('Error:', e)


def has_nitro(xy):
    if isinstance(xy, str):
        xy = xy.encode()
    try:
        for x in nregex.finditer(xy):
            # print(x)
            yield x.group().decode()  #[21:]
    except Exception as e:
        pass
        # print('Error:', e)


def has_pcs(xy):
    if isinstance(xy, str):
        xy = xy.encode()
    try:
        for x in pregex.finditer(xy):
            # print(x)
            yield x.group().decode()  #[21:]
    except Exception as e:
        pass


def f_raise(e):
    """
    Raise exception in a thread.
    :param e: The exception to raise.
    """

    def _raise(e):
        raise (e)

    threading.Thread(target=_raise, args=(e, )).start()


class SelfBot:

    def __init__(self, token=None, **kwargs):
        """
        Initialize object.
        :param token: The acount authorization token.
        :param random_time_range: The interval of time to wait before a request to bypass raelimits.
        :param debug: The level of print debug.
        :param log: If the selfbot need to log all that it sees.
        :param compress: If the websocket must be compressed
        """
        self.token = token or os.getenv("TOKEN")
        self.RTR = kwargs.get("random_time_range", (1, 5))
        self.DEBUG = kwargs.get("debug", 0)
        self.log = kwargs.get("log", True)
        self.COMPRESS = kwargs.get("compress", True)
        self.events = utils.Events(noerr=True)
        self.osv = str(random.randint(10, 11))
        self.brv = f"{random.randint(10, 110)}.0.4.{random.randint(0, 70)}"
        self.wkv = f"{random.randint(100, 800)}.{random.randint(0, 100)}"
        self.useragent = f"Mozilla/5.0 (Windows NT {self.osv}.0; Win64; x64) AppleWebKit/{self.wkv} (KHTML, like Gecko) Chrome/{self.brv} Safari/{self.wkv}"
        self.data = {}
        self.headers = {
            "Authorization": self.token,
            "User-Agent": self.useragent,
        }
        self.init_vars()

    def check_message(self, x):
        for token in has_token(x):
            self.events.trigger("ON_TOKEN", self, token)
        for code in has_invite(x):
            self.events.trigger("ON_INVITE", self, code)
        for nitro in has_nitro(x):
            self.events.trigger("ON_NITRO", self, nitro)
        for pcs in has_pcs(x):
            self.events.trigger("ON_PCS", self, pcs)

    def test_rcv(self, r):
        self.check_message(r.content)
        return r

    def init_vars(self):
        """
        Initialize variables.
        """
        self.AUTH = False
        self.READY = False
        self.compress_obj = None
        self.LAST_HB = None
        self.HB = object()

    ##########

    def fetch_messages(self,
                       channel_id,
                       limit=50,
                       around=None,
                       before=None,
                       after=None):
        """
        Fetch messages from the channel.
        :param channel_id: the channel id of the message.
        :param limit: the number of messages to fetch (max 100).
        :param around: the message id to fetch around.
        :param before: the message id to fetch before.
        :param after: the message id to fetch after.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={str(limit)+(('&after='+str(after))*int(after!=None))+(('&before='+str(before))*int(before!=None))+(('&around='+str(around))*int(around!=None))}"
        r = self.test_rcv(requests.get(url, headers=self.headers))
        #print(r.status_code)
        # print(r.content)
        if r.status_code != 200:
            return r.content
        return r.json()

    def get_message(self, payload):
        """
        Get a message from a payload.
        :param payload: The payload.
        """
        if payload.get("d", payload).get("content", "") != "":
            return payload.get("d", payload).get("content", "")
        messages = self.fetch_messages(
            payload.get("d", payload)["channel_id"],
            limit=1,
            around=payload.get("d", payload)["id"],
        )
        if isinstance(messages, list):
            return messages[0]
        return messages

    def read_message(self, channel_id, message_id):
        """
        Mark a message as read.
        :param channel_id: The message's channel id.
        :param message_id: The message's id.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/ack"
        payload = {"token": None}
        r = self.test_rcv(
            requests.post(url, headers=self.headers, data=json.dumps(payload)))
        return r

    def unread_message(self, channel_id, message_id):
        """
        Mark a message as non-read.
        :param channel_id: The message's channel id.
        :param message_id: The message's id.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/ack"
        payload = {"manual": True, "mention_count": 1}
        r = self.test_rcv(
            requests.post(url, headers=self.headers, data=json.dumps(payload)))
        return r

    def send_message(self, message, channel_id, tts=False):
        """
        Send a message in a channel.
        :param message: The message to send.
        :param channel_id: The channel to send the message.
        :param tts: Whether or not to send the message as a tts.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        if isinstance(message, str):
            payload = {"content": message, "tts": tts}
        else:
            payload = message
        headers = {**self.headers, "Content-Type": "application/json"}
        r = self.test_rcv(
            requests.post(url, headers=headers, data=json.dumps(payload)))
        return r.json()

    def delete_message(self, channel_id, message_id):
        """
        Delete a message.
        :param channel_id: The channel id of the message.
        :param message_id: The id of the message.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/"
        r = self.test_rcv(requests.delete(url, headers=self.headers))
        return r

    def patch_message(self, message, channel_id, message_id):
        """
        Patch a message content.
        :param message: The new message content.
        :param channel_id: The channel id of the message.
        :param message_id: The message to patch id.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
        #print(url)
        headers = {**self.headers, "Content-Type": "application/json"}
        payload = {"content": message}
        r = self.test_rcv(
            requests.patch(url, headers=headers, data=json.dumps(payload)))
        return r

    def typing(self, channel_id):
        """
        Send a typing status on a channel.
        :param channel_id: The channel id to send the status.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/typing"
        r = self.test_rcv(requests.post(url, headers=self.headers))
        return r

    def add_reaction(self, emoji, channel_id, message_id):
        """
        Add a reaction to a message.
        :param emoji: The emoji to add.
        :param channel_ids: The channel IDs to add the reaction.
        :param message_id: The message ID to add the reaction.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me?location=Message"
        r = self.test_rcv(requests.put(url, headers=self.headers))
        return r

    def remove_reaction(self, emoji, channel_id, message_id):
        """
        Remove a reaction from a message.
        :param emoji: The emoji to remove.
        :param channel_ids: The channel IDs to remove the reaction from.
        :param message_id: The message ID to remove the reaction from.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me?location=Message"
        r = self.test_rcv(requests.delete(url, headers=self.headers))
        return r

    def change_presence(self,
                        status,
                        custom=None,
                        activities=[],
                        afk=False,
                        since=0):
        """
        Change the presence of the account.
        :param status: The status to change.
        :param custom: A custom status to change.
        :param activities: A list of activities to change.
        :param afk: Whether or not to set the presence as AFK.
        :param since: A timestamp to set the presence as being active since.
        """
        time.sleep(random.uniform(*self.RTR))
        if custom != None:
            activities.append({
                "name": "Custom Status",
                "type": 4,
                "state": custom,
                "emoji": None
            })
        payload = {
            "op": 3,
            "d": {
                "status": status,
                "since": since,
                "activities": activities,
                "afk": afk,
            },
        }
        self.ws.send(json.dumps(payload))

    def join_guild(self, code):
        """
        WARNING --> This function can deactivate an account !
        Join a guild with the given invitation code.
        :param code: The invitation code of the guild to join.
        """
        time.sleep(random.uniform(*self.RTR) * 2)
        url = "https://discord.com/api/v9/invites/" + code
        data = {}
        r = self.test_rcv(
            requests.post(url, headers=self.headers, data=json.dumps(data)))
        return r.json()

    def get_invite_infos(self, code):
        time.sleep(random.uniform(*self.RTR))
        url = "https://discord.com/api/v9/invites/" + code
        r = self.test_rcv(requests.get(url, headers=self.headers))
        return r.json()

    def leave_guild(self, guild_id):
        """
        Leaves a guild.
        :param guild_id: The id of the guild to leave
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/users/@me/guilds/{guild_id}"
        data = {"lurking": False}
        r = self.test_rcv(
            requests.delete(url, headers=self.headers, data=json.dumps(data)))
        return r.json()

    def create_invite(self,
                      channel_id,
                      max_age=0,
                      max_uses=0,
                      temporary=False):
        """
        :param channel_id: The channel id of the invitation.
        :param max_age: The maximum age of the invite.
        :param max_uses: The number of uses the invite can be used for.
        :param temporary: If the invite is temporary.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/channels/{channel_id}/invites"
        data = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        r = self.test_rcv(
            requests.post(url, headers=headers, data=json.dumps(data)))
        return r.content

    def relationships(self, from_data=True):
        """
        Returns a list of relationships of the account.
        """
        if from_data:
            return self.data["relationships"]
        time.sleep(random.uniform(*self.RTR))
        url = "https://discord.com/api/v9/users/@me/relationships"
        r = self.test_rcv(requests.get(url, headers=self.headers))
        return r.json()

    def get_guilds(self, from_data=True):
        """
        Get a list of the guilds the account is in.
        """
        if from_data:
            return self.data.get("guilds")
        time.sleep(random.uniform(*self.RTR))
        url = "https://discord.com/api/v9/guilds"
        r = self.test_rcv(requests.get(url, headers=self.headers))
        return r.json()

    def affinities(self):
        """
        Returns a list of the account's affinities.
        """
        time.sleep(random.uniform(*self.RTR))
        url = "https://discord.com/api/v9/users/@me/affinities/users"
        r = self.test_rcv(requests.get(url, headers=self.headers))
        return r.json()

    def friend_request(self, username, tag):
        """
        Send a friend request to a user.
        :param username: The username of the user to send the request.
        :param tag: The tag of the user to send the request.
        """
        time.sleep(random.uniform(*self.RTR))
        url = "https://discordapp.com/api/v9/users/@me/relationships"
        payload = {"username": username, "discriminator": tag}
        headers = {**self.headers, "Content-Type": "application/json"}
        r = self.test_rcv(
            requests.post(url, headers=headers, data=json.dumps(payload)))
        return r

    def create_guild(self,
                     name,
                     icon=None,
                     channels=[],
                     template="2TffvPucqHkN"):
        """
        Create a guild.
        :param name: The name of the guild.
        :param icon: the url of the guild's icon
        """
        time.sleep(random.uniform(*self.RTR))
        data = {
            "name": name,
            "icon": icon,
            "channels": channels,
            "system_channel_id": None,
            "guild_template_code": template
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        return self.test_rcv(
            requests.post("https://discord.com/api/v9/guilds",
                          headers=headers,
                          data=json.dumps(data))).json()

    def add_friend(self, user_id):
        """
        Add a friend (or accept a friend request).
        :param user_id: The user to add's ID.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/users/@me/relationships/{user_id}"
        payload = {}
        headers = {**self.headers, "Content-Type": "application/json"}
        r = self.test_rcv(
            requests.put(url, headers=headers, data=json.dumps(payload)))
        return r

    accept_friend = add_friend

    def deny_friend(self, user_id):
        """
        Deny a friend request of a user (or remove a friend).
        :param user_id: The user's ID.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/users/@me/relationships/{user_id}"
        payload = {}
        r = self.test_rcv(
            requests.delete(url,
                            headers=self.headers,
                            data=json.dumps(payload)))
        return r

    remove_friend = deny_friend

    def get_profile(self, user_id):
        """
        Get a user's profile information.
        :param user_id: The user's ID.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/users/{user_id}/profile"
        r = self.test_rcv(requests.get(url, headers=self.headers))
        return r.json()

    def get_guild(self, guild_id):
        """
        Get a guild's information.
        :param guild_id: The guild's ID.
        """
        pass

    def update_guild(self, guild_id, **kwargs):
        """
        Update a guild's information.
        :param guild_id: The guild's ID.
        :param kwargs: The parameters to update.
        """
        pass

    def update_channel(self, channel_id, **kwargs):
        """
        Update a channel's information.
        :param channel_id: The channel's ID.
        :param kwargs: The parameters to update.
        """
        pass

    def update_profile(self, user_id, **kwargs):
        """
        Update a user's profile information.
        :param user_id: The user's ID.
        :param kwargs: The parameters to update.
        """
        pass

    def give_role(self, role_id, guild_id, user_id):
        """
        Gives a role to a user in a guild.
        :param role_id: The role id to give.
        :param guild_id: The guild id to give the role to.
        :param user_id: The user id to give the role to.
        """
        time.sleep(random.uniform(*self.RTR))
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
        payload = {"roles": [role_id]}
        r = self.test_rcv(
            requests.patch(url, headers=self.headers,
                           data=json.dumps(payload)))
        return r

    def remove_role(self, role_id, guild_id, user_id):
        """
        Removes a role from a user in a guild.
        :param role_id: The role to remove.
        :param guild_id: The guild to remove the role from.
        :param user_id: The user to remove the role from.
        """
        time.sleep(random.uniform(*self.RTR))
        pass

    def backup_account(self,
                       file,
                       channels=False,
                       messages=False,
                       n_messages=50):
        """
        Backup the account.
        :param file: The file to backup the account.
        """
        ## JSON data
        # data        --> data
        # friends     --> [(id : user_infos)]
        # guilds      --> [(id : (guild_infos, invite))]
        # (channels)  --> [(channel_id : channel_infos)]
        # (messages)  --> [(channel_id : [message_infos])]
        pass

    def backup_load(self, file):
        """
        Load the account from a backup.
        :param file: The file to load the account from.
        """
        pass

    ##########

    def heart_int(self, ws):
        if self.DEBUG > 0:
            if self.DEBUG == 1:
                print(" ---------------------------------")
            print(("| " * int(self.DEBUG == 1)) +
                  ">  3: Heartbeat (opcode 1)" +
                  ("      |" * int(self.DEBUG == 1)))
        if self.DEBUG > 1:
            print("sending heartbeat...")
        ws.send(json.dumps({"op": 1, "d": self.LAST_HB}))
        if self.DEBUG > 1:
            print("heartbeat sent.")

    def on_ws(self, ws, message):
        # print(message)
        if self.DEBUG > 1:
            print("new message received.")

        try:
            if self.COMPRESS:
                message = self.compress_obj.decompress(message)
            try:
                payload = json.loads(message)
            except Exception as je:
                print("json error:", je, message)
                return
        except Exception as de:
            print("decompress error:", de, message)
            return
        self.LAST_HB = payload.get("s")
        if payload["op"] == 10:
            if self.DEBUG > 0:
                print("<  2: Hello (opcode 10)")
            if self.DEBUG > 1:
                print("received hello event.")
            self.HB = utils.setInterval(
                self.heart_int, payload["d"]["heartbeat_interval"] / 1000, ws)
        elif payload["op"] == 11:
            if self.DEBUG > 0:
                print(("| " * int(self.DEBUG == 1)) +
                      "<  3: Heartbeat ACK (opcode 11)" +
                      (" |" * int(self.DEBUG == 1)))
                if self.DEBUG == 1:
                    print(" --------------------------------- ")
            if not self.AUTH:
                if self.DEBUG > 0:
                    print(">  4: Identify (opcode 2)")
                if self.DEBUG > 1:
                    print("sending connection payload...")
                PAYLOAD = {
                    "op": 2,
                    "d": {
                        "token": self.token,
                        "capabilities": 4093,
                        "properties": {
                            "os": "Windows",
                            "browser": "Chrome",
                            "device": "",
                            "system_locale": "en-EN",
                            "browser_user_agent": self.useragent,
                            "browser_version": self.brv,
                            "os_version": self.osv,
                            "referrer": "",
                            "referring_domain": "",
                            "referrer_current": "",
                            "referring_domain_current": "",
                            "release_channel": "stable",
                            "client_event_source": None,
                        },
                        "presence": {
                            "status": "online",
                            "since": 0,
                            "activities": [],
                            "afk": False,
                        },
                        "compress": False,
                        "client_state": {
                            "guild_versions": {},
                            "highest_last_message_id": "0",
                            "read_state_version": 0,
                            "user_guild_settings_version": -1,
                            "user_settings_version": -1,
                            "private_channels_version": "0",
                            "api_code_version": 0,
                        },
                    },
                }
                ws.send(json.dumps(PAYLOAD))
                if self.DEBUG > 1:
                    print("connection paylod sent.")
                self.AUTH = True
            if self.DEBUG > 1:
                print("heartbeat ACK received.")

        elif payload["op"] == 0:
            if not self.READY:
                if self.DEBUG > 0:
                    print("<  5: READY (opcode 0)")
                if self.DEBUG > 1:
                    print("READY event received.")
                self.READY = True
                self.data = payload["d"]
                # ws.close()
            elif self.DEBUG > 0:
                print("<  7: Event (opcode 0)")
        if self.DEBUG > 0:
            print(
                " ".join((
                    payload["t"]
                    if type(payload["t"]) == str else str(payload["t"]),
                    str(payload["op"]),
                )) * (int(payload["t"] != None)) +
                ("\n" * (int(payload["t"] != None))),
                end="",
            )
        # print(payload)
        self.check_message(safe(payload.get("d", {})).get("content", b""))
        if payload["t"] == None:
            return
        if self.log:
            with open(f"logs_{self.data['user']['id']}.txt", "a") as f:
                f.write(payload["t"] + " " + json.dumps(payload["d"]) + "\n")
        self.events.trigger(payload["t"], self, payload["d"])

    def on_open(self, ws):
        self.ws = ws
        if self.DEBUG > 0:
            print(">  1: Connection Etabished")
        if self.DEBUG > 1:
            print("connection opened...")
        if self.COMPRESS:
            self.compress_obj = zlib.decompressobj()

    def on_close(self, ws, code, *args):
        if self.DEBUG > 0:
            print("<  6: Connection Closed (code", str(code) + ")")
        if self.DEBUG > 1:
            print("connection closed :", code, args)
        self.HB.run = False
        self.init_vars()
        if True:  #code in [1000, None]:
            print("restarting the connection...")
            self.mainco()

    def on_error(self, ws, error):
        print("connection error:", error)  # , dir(error))
        f_raise(error)

    def mainco(self, url="wss://gateway.discord.gg/?v=9&encoding=json"):
        """
        Run the bot.
        """
        if self.COMPRESS:
            url += "&compress=zlib-stream"
        wsapp = websocket.WebSocketApp(
            url,
            on_message=self.on_ws,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
        )
        wsapp.run_forever()

    run = mainco


if __name__ == "__main__":
    print("running :", __file__)
    sh = 1
    debug = 0
    if sh != 0:
        debug = 0
    client = SelfBot(debug=debug, log=False)

    if sh == -1:
        # threading.Thread(target=client.mainco).start()
        while True:
            t = input("event searched : ")
            r = []
            with open(f"logs_{client.data['user']['id']}.txt", "r") as f:
                for x in f:
                    if x.startswith(t):
                        r.append(json.loads(x[len(t) + 1:]))
            if len(r) == 0:
                print("nothing found.")
                continue
            print("last :\n", r[-1])
            print("found :", len(r))
            c = input("print char [*/n] ? ")
            if c == "n":
                continue
            c = input("print : ")
            for i, x in enumerate(r):
                print(i, str(x.get(c)).replace("\n", "\\n"))
            i = input("index to search : ")
            if not i.isdigit():
                print("please enter a valid index.")
                continue
            print(r[int(i)])
        else:
            while True:
                pass
    if sh == 1:
        while True:
            try:
                print(eval(input(">>> ")))
            except Exception as e:
                print(e)
    else:
        client.run()
