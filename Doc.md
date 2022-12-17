# DSBP : Discord SelfBot Python
By Louisspioupiou

## object SelfBot
The SelfBot object is the main class in this module, it permit to create a simple selfbot.
example :
```py
client = SelfBot(token, debug=1, log=False)

@client.events("MESSAGE_CREATE")
def on_message(client, message):
    print("new message :", message["content"])

@client.events("READY")
def Ready(client, args):
    print("I'm ready !")

client.run()
```

### method \_\_init\_\_ (self, token: str, random_time_range=(1, 5), debug=0, log=True, compress=True)
Initialize object.
<br/>
**`token`**: The acount authorization token.
<br/>
**`random_time_range`**: The interval of time to wait before a request to bypass raelimits.
<br/>
**`debug`**: The level of print debug.
<br/>
**`log`**: If the selfbot need to log all that it sees.
<br/>
**`compress`**: If the websocket must be compressed

### method fetch_message (self, channel_id, limit=50, around=None, before=None, after=None)
Fetch messages from the channel.
<br/>
**`channel_id`**: The channel id of the message.
<br/>
**`limit`**: The number of messages to fetch (max 100).
<br/>
**`around`**: The message id to fetch around.
<br/>
**`before`**: The message id to fetch before.
<br/>
**`after`**: The message id to fetch after.

### method get_message(self, payload: dict)
Get the message content if not in the payload.
<br/>
**`payload`**: The message infos or the payload sent in the websocket gateway.

### method read_message (self, channel_id, message_id)
Mark a message as read.
<br/>
**`channel_id`**: The message's channel id.
<br/>
**`message_id`**: The message's id.