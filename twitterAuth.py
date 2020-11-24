import tweepy
import yaml


def getTwitterAuth():
    with open("config.yml", "r") as f:
        inputFile = yaml.safe_load(f)
        dmUserList = []
        consumer_token = inputFile["twitter-oauth-handler"]["consumer-token"]
        consumer_secret = inputFile["twitter-oauth-handler"]["consumer-secret"]
        auth_token = inputFile["twitter-oauth-handler"]["auth-token"]
        auth_secret = inputFile["twitter-oauth-handler"]["auth-secret"]
        for i in inputFile["dm-list"]:
            dmUserList.append(i)
    f.close()
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(auth_token, auth_secret)

    api = tweepy.API(auth)

    return api, dmUserList

# created by decampc using witter's API <3
