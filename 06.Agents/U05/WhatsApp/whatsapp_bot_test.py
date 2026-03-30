from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

from pyngrok import ngrok, conf
from threading import Thread

# CONFIGURATION

# Tell pyngrok where ngrok is installed (IMPORTANT)
conf.get_default().ngrok_path = "C:\\ngrok\\ngrok.exe"

# Create Flask app
app = Flask(__name__)


# WEBHOOK ENDPOINT (Twilio will call this)

@app.post("/webhook")
def webhook():
    """
    This endpoint receives incoming WhatsApp messages from Twilio.
    """

    # Get message text sent by user
    incoming_text = request.values.get("Body", "").strip()

    # Create Twilio response object
    resp = MessagingResponse()

    # Simple echo response (you can replace this with your AI logic later)
    if incoming_text:
        resp.message(f"You said: {incoming_text}")
    else:
        resp.message("Message received.")

    # Return response as XML (required by Twilio)
    return Response(str(resp), mimetype="application/xml")


# RUN FLASK SERVER

def run_flask():
    """
    Run Flask server locally on port 5000.
    """
    app.run(host="0.0.0.0", port=5000)


# MAIN ENTRY POINT

if __name__ == "__main__":

    # Start Flask in a background thread
    Thread(target=run_flask, daemon=True).start()

    # Create ngrok tunnel to expose local server
    tunnel = ngrok.connect(5000)

    # Get public URL
    public_url = tunnel.public_url

    print("\n🌍 Public URL (use this in Twilio):")
    print(public_url + "/webhook")

    print("\n🤖 Server is running... Press Enter to stop.\n")

    # Keep script alive
    input()