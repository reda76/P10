from flask import Flask, request, Response
from botbuilder.schema import Activity
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, ConversationState, MemoryStorage

import asyncio
from luisbot import LuisBot
from config import DefaultConfig

CONFIG = DefaultConfig()

app = Flask(__name__)
loop = asyncio.get_event_loop()

port = CONFIG.PORT

microsoftAppId = CONFIG.MICROSOFT_APP_ID
microsoftAppPswd = CONFIG.MICROSOFT_APP_PSWD

botsettings = BotFrameworkAdapterSettings(microsoftAppId, microsoftAppPswd)
# botsettings = BotFrameworkAdapterSettings("", "")
botadapter = BotFrameworkAdapter(botsettings)

CONMEMORY = ConversationState(MemoryStorage())
botdialog = LuisBot(CONMEMORY)


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        body = request.json
    else:
        return Response(status=415)

    # Json où contient les informations
    activity = Activity().deserialize(body)

    auth_header = (request.headers["Authorization"]
                   if "Authorization" in request.headers else "")

    async def call_fun(turncontext):
        await botdialog.on_turn(turncontext)

    task = loop.create_task(
        botadapter.process_activity(activity, auth_header, call_fun))
    loop.run_until_complete(task)
    print(CONMEMORY)


if __name__ == '__main__':
    app.run('localhost', port, debug=True)