import tweepy

auth = tweepy.OAuthHandler('I2gLDk0g799rdU6QtRksFRP8j', 'XoM2NATrzWtcvdifRMJDOpwxU4hIsG3Esa9H3tDMNgK0fkWXHc')
auth.set_access_token('1198115742522232832-sfLSM3E2JivKrmMbTzZtd5XJHJ4gCi', 'un5e8N8lpjIe0Jk2ZBSuMGqdXPLGBcJ4OpS7hSrJkTXXp')

api = tweepy.API(auth)

tweet = tweepy.API.update_status("this is a test")
