from twilio.rest import Client
import yaml
import logging


def getTwilioAuth():
    account = ""
    token = ""
    phoneSend = ""
    with open('config.yml', 'r') as f:
        inputFile = yaml.safe_load(f)
        toPhoneValue = inputFile["Number to notify"]
        fromPhoneValue = inputFile["Number to send notification"]
        countryCode = inputFile["country-code"]
        account = inputFile["API Account SID"]
        token = inputFile["API Account Token"]



        countryCode = str(countryCode)
        phoneNotify = []
        for i in toPhoneValue:
            i = str(i)
            i = i.strip("-")
            phoneNotify.append(str(countryCode+i))

        if len(fromPhoneValue) > 1:
            print("You can only send from one number at a time, check the config.yml. Using first number in list...")
            fromPhoneValue = str(fromPhoneValue[0])
            fromPhoneValue = fromPhoneValue.strip("-")

            phoneSend = str(countryCode+str(fromPhoneValue))
        else:
            fromPhoneValue = str(fromPhoneValue[0])
            fromPhoneValue = fromPhoneValue.strip("-")

            phoneSend = str(countryCode+str(fromPhoneValue))

    client = Client(account, token)
    logging.basicConfig(filename='./log.txt')
    client.http_client.logger.setLevel(logging.INFO)

    f.close()

    return client, phoneNotify, phoneSend
    
# created by decampc using Twilio's API <3
