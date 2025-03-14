from fastapi import FastAPI, Query
from stream_chat import StreamChat
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://getstream.io", "https://frontend-tka5.onrender.com"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

STREAM_API_KEY = "bknpx6eut9sj"
STREAM_API_SECRET = "3es4893mzf6m64mjj59pmzznhvta895ur297dpuet3g449aky22q9fhunweh2xua"

OPENAI_API_KEY = "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"

chat_client = StreamChat(api_key=STREAM_API_KEY, api_secret=STREAM_API_SECRET)

app = FastAPI()

@app.get("/")  # This should respond at "https://your-api.onrender.com/"
def read_root():
    return {"message": "Backend is running!"}

@app.get("/ping")  # Optional health check
def ping():
    return {"status": "OK"}
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

    # ✅ Use .get() to avoid KeyErrors
    event_type = event.get("type")
    user_info = event.get("user", {})
    message_info = event.get("message", {})

    # ✅ Validate event before processing
    if event_type == "message.new" and user_info.get("id") != "ai-bot":
        user_message = message_info.get("text", "")
        logging.debug(f"User message: {user_message}")

        if not user_message:
            logging.debug("No message text found, skipping response.")
            return {"status": "no_message"}

        # ✅ Call AI response function
        ai_reply = await ai_response({"text": user_message})

        # ✅ Log AI response before sending
        logging.debug(f"AI Reply: {ai_reply}")

        # ✅ Send AI response to chat
        chat_client.channel("messaging", "ai-bot").send_message({
            "text": ai_reply.get("reply", "I'm sorry, I couldn't generate a response."),
            "user": {"id": "ai-bot"}  # ✅ Correct format
        })

        logging.debug("AI response sent successfully.")

    return {"status": "ok"}

