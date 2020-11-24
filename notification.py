import os
import yaml
from twilioAuth import getTwilioAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twitterAuth import getTwitterAuth

def phoneMessage(messageInput):
    client, phoneNotify, phoneSend = getTwilioAuth()

    messageInput = str(messageInput)

    for i in phoneNotify:
        try:
            sentMessage = client.messages.create(
            to=i,
            from_=phoneSend,
            body=messageInput
        )
        except:
            return 0
    return 1
def emailMessage(messageInput):
    SGApiKey = ""
    emailToList = []
    emailTo = ""
    emailFrom = ""
    multiple = True

    with open('config.yml', 'r') as f:
        inputFile = yaml.safe_load(f)
        if len(inputFile["email-to"]) > 1:
            for i in inputFile["email-to"]:
                emailToList.append(i)
            print(emailToList)
        else:
            emailTo = inputFile["email-to"]
            multiple = False
        if not(inputFile["hide-api"]):
            SGApiKey = inputFile["sg-api-key"]
        emailFrom = inputFile["email-from"]

    if multiple:
        message = Mail(
        from_email=emailFrom,
        to_emails=emailToList,
        subject='Watched product is available.',
        plain_text_content=messageInput,
        is_multiple=True
        )
        try:
            if not(inputFile["hide-api"]):
                sg = SendGridAPIClient(SGApiKey)
            else:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)

            f.close()
            return 1
        except Exception as e:
            print(e.message)
            f.close()
            return 0
    else:
        message = Mail(
        from_email=emailFrom,
        to_emails=emailTo,
        subject='Watched product is available.',
        plain_text_content=messageInput,
        is_multiple=False
        )
        try:
            if not(inputFile["hide-api"]):
                sg = SendGridAPIClient(SGApiKey)
            else:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)

            f.close()
            return 1
        except Exception as e:
            print(e.message)

            f.close()
            return 0
def sendDM(message):
    api, dmUserList = getTwitterAuth()

    try:
        for user in dmUserList:
            user = str("@"+user)
            user = api.get_user(user).id_str
            try:
                sendDirectMessage = api.send_direct_message(user, message)
            except tweepy.TweepError as e:
                print(e)
                pass
        return 1
    except tweepy.TweepError as e:
        print(e)
        return 0

def sendTweet(message):
    api, dmUserList = getTwitterAuth()
    try:
        api.update_status(message)
        return 1
    except tweepy.TweepError as e:
        print(e)
        return 0

# created by decampc using Twilio, SendGrid, and Twitter's APIs <3
