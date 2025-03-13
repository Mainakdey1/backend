from fastapi import FastAPI, Query
from stream_chat import StreamChat
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

STREAM_API_KEY = "bknpx6eut9sj"
STREAM_API_SECRET = "3es4893mzf6m64mjj59pmzznhvta895ur297dpuet3g449aky22q9fhunweh2xua"

OPENAI_API_KEY = "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"

chat_client = StreamChat(api_key=STREAM_API_KEY, api_secret=STREAM_API_SECRET)
openai.api_key = OPENAI_API_KEY

app = FastAPI()


@app.get("/token")
def generate_token(user_id: str = Query(...)):
    token = chat_client.create_token(user_id)
    return {"token": token}


@app.post("/ai-response")
async def ai_response(message: dict):
    user_message = message.get("text", "")

    return {"reply": user_message}

import logging

logging.basicConfig(level=logging.DEBUG)

@app.post("/webhook")
async def stream_webhook(event: dict):
    logging.debug(f"Received event: {event}")

    if event["type"] == "message.new" and event["user"]["id"] != "ai-bot":
        user_message = event["message"]["text"]
        logging.debug(f"User message: {user_message}")

        ai_reply = await ai_response({"text": user_message})

        logging.debug(f"AI Reply: {ai_reply}")

        chat_client.channel("messaging", "ai-bot").send_message({
            "text": ai_reply["reply"],
            "user_id": "ai-bot"
        })

    return {"status": "ok"}

