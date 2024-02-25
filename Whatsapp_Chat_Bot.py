import os
import logging
import google.generativeai as genai
from whatsapp import WhatsApp, Message
from dotenv import load_dotenv
from flask import Flask, request, Response

# Initialize Flask App
app = Flask(__name__)

# Load .env file
load_dotenv("../.env")
messenger = WhatsApp(os.getenv("TOKEN"),
                     phone_number_id=os.getenv("ID"))
VERIFY_TOKEN = "Verify_token"

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



@app.get("/")
def verify_token():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        logging.info("Verified webhook")
        challenge = request.args.get("hub.challenge")
        return str(challenge)
    logging.error("Webhook Verification failed")
    return "Invalid verification token"


@app.post("/")
def hook():
    # Handle Webhook Subscriptions
    data = request.get_json()
    if data is None:
        return Response(status=200)
    logging.info("Received webhook data: %s", data)
    
    messenger = WhatsApp(token=os.getenv("TOKEN"),phone_number_id=os.getenv("ID"))
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

    safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

    convo = model.start_chat(history=[])
    convo.send_message(messenger.get_message(data))

    message = Message(instance=messenger, content=convo.last.text, to="918129412156") 
    message.send()
    return "OK", 200






if __name__ == "__main__":
    app.run(port=6869, debug=False)