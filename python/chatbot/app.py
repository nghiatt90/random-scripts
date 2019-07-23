import os
import sys
import json
import random
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if messaging_event['message'].get('quick_reply'):  # quick reply
                        send_message(sender_id, messaging_event['message']['quick_reply']['payload'])
                        next_question(sender_id)
                    else:
                        if message_text.lower() == 'start':
                            next_question(sender_id)
                        else:
                            send_message(sender_id, 'Hello there! Please type "Start" to start an English quiz')

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def next_question(recipient_id):
    questions = [
        (
            "How would you complete the following sentence: Please don't call this evening because:",
            [
                "I'll be watching TV.",
                "I'll have watched TV.",
                "I will watch TV.",
                "I will have been watching TV.",
            ],
            0
        ),
        (
            "Which of the following is correct?",
            [
                "I haven't finished my homework yet.",
                "I didn't finish my homework yet.",
                "I hasn't finished my homework yet.",
                "I don't have finished my homework yet.",
            ],
            0
        ),
        (
            "How would you respond to the question, 'Did you enjoy the movie'?",
            [
                "Yes, it was so a nice movie.",
                "Yes, it was so nice a movie.",
                "Yes, it was such a nice movie.",
                "Yes, it was a such nice movie.",
            ],
            2
        ),
        (
            "Which of the following sentences is the wrong sentence?",
            [
                "You'll win if you play well.",
                "If you ask her, she'll help.",
                "If she comes to the party, she'll enjoy it.",
                "You'll pass if you will work hard.",
            ],
            3
        ),
        (
            "Which sentence is correct?",
            [
                "They looked loving at each other.",
                "I get always very tired after work.",
                "I always get tired after work.",
                "They looked like at each other.",
            ],
            2
        ),
    ]

    (text, options, answer) = random.choice(questions)
    send_multiple_choice(recipient_id, text, options, answer)


def send_multiple_choice(recipient_id, message_text, options, answer):

    log('sending multiple choice question to {recipient}'.format(recipient=recipient_id))

    message_text += '\n'
    for no, line in enumerate(options):
        message_text += '\n{}. {}'.format(no+1, line)

    params = {'access_token': os.environ['PAGE_ACCESS_TOKEN']}
    headers = {'Content-Type': 'application/json'}
    buttons = [{'content_type': 'text', 'title': str(ans+1), 'payload': 'Correct!' if ans == answer else 'Wrong answer'}
               for ans in range(len(options))]

    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'messaging_type': 'RESPONSE',
        'message': {
            'text': message_text,
            'quick_replies': buttons
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
