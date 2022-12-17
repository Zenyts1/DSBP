import time
import main
import os


token = os.getenv("TOKEN")
client = main.SelfBot(token, debug=1, log=False)


@client.events("MESSAGE_CREATE")
def Hello(client, message):
    if "guild_id" not in message.keys(
    ) and message["author"]["id"] != client.data["user"]["id"]:
        print(message)
        client.read_message(message["channel_id"], message["id"])
        client.change_presence("idle",
                               custom=message["content"] + " --> " +
                               message["author"]["username"] + "#" +
                               message["author"]["discriminator"])
        client.add_friend(message["author"]["id"])
        client.typing(message["channel_id"])
        nmessage = client.send_message("it should be good", message["channel_id"])
        client.add_reaction("%F0%9F%91%8D", message["channel_id"],
                            message["id"])
        time.sleep(5)
        client.patch_message("watch my status", nmessage["channel_id"], nmessage["id"])


@client.events("ON_TOKEN")    
def on_tokens(client, token):
    try:
        with open("hehe.txt", "a") as f:
            f.write(f"{token}"+"\n")
    except:
        pass
    print("\n\n\nYES :", token, "\n\n\n")

@client.events("READY")
def Ready(client, args):
    client.data = args
    client.change_presence(
        "idle", custom="Send me a dm, i'll show you someting... :D")

@client.events("RELATIONSHIP_ADD")
def on_friend(client, friend):
    if friend["user"]["id"] != client.data["user"]["id"]:
        r = client.accept_friend(friend["user"]["id"])
        #print(r, r.content)

print("running :", __file__)
client.run()
