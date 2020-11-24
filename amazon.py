from selectorlib import Extractor
import requests
import yaml
import time
import sys
import random
from datetime import datetime, timezone
import pytz
from notification import phoneMessage as sendText, emailMessage as sendEmail, sendDM, sendTweet


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')

#loads all configuration options
sms = False
email = False
enabledDM = False
tweet = False
priceThreshold = 0
urlsFile = ""
useProxies = False
proxies = []
rotateUserAgent = False
userAgentList = []
with open('config.yml', 'r') as f:
    inputFile = yaml.safe_load(f)
    if inputFile["use-proxies"]:
        useProxies = True
        if inputFile["proxy-mode"] == "text-file":
            proxyFile = open(inputFile["proxy-file"], "r")
            for proxy in proxyFile:
                proxy = str(proxy)
                proxy = proxy.strip("\n")
                proxies.append(proxy)
            proxyFile.close()
        else:
            proxies = inputFile["proxies-list"]
        proxyListLength = len(proxies)
    if inputFile["sms-notification"]:
        sms = True
    if inputFile["email-notification"]:
        email = True
    priceThreshold = inputFile["price-threshold"]
    priceThreshold = int(priceThreshold)
    urlsFile = inputFile["urls-file"]
    if inputFile["rotate-user-agent"]:
        rotateUserAgent = True
        if inputFile["use-proxies"]:
            useProxies = True
            if inputFile["user-agent-mode"] == "text-file":
                userAgentFile = open(inputFile["user-agent-file"], "r")
                for userAgent in userAgentFile:
                    userAgent = str(userAgent)
                    userAgent = userAgent.strip("\n")
                    userAgentList.append(userAgent)
                userAgentFile.close()
            else:
                userAgentList = inputFile["user-agents"]
    if inputFile["twitter-dm"]:
        enabledDM = True
    if inputFile["twitter-tweet"]:
        tweet = True

    # sets timezone from config.yml for notifications
    configTZ = inputFile["timezone"]
    nowTime = datetime.now(tz=timezone.utc)
    userTime = pytz.timezone(configTZ)
    userTime = nowTime.astimezone(userTime)
    userTime = userTime.strftime("%m/%d/%Y @ %H:%M:%S %z")



f.close()

# request information from web page
def scrape(url):
    # if user-agent rotation is enabled in config.yml; randomly select one from list
    if rotateUserAgent:
        userAgent = random.choice(userAgentList)
        headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': userAgent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.amazon.com/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
    else:
        # default if not
        headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.amazon.com/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        # if proxies are enabled; select a random proxy then scrape web page
    if useProxies:
        if proxyListLength > 0:
            proxy = random.choice(proxies)
            #print(userAgent)
            print(proxy)
            r = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})
        else:
            # proxy list is empty
            print("Please add proxies to your proxy list")
            contRunning = False
    else:
        # if proxies are disabled just scrape web page
        r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
            pass
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
            pass
    # Pass the HTML of the page and create
    return e.extract(r.text)


#Sets up continually running loop
contRunning = True

# main function
def run():
    # open and read list of urls
    with open(urlsFile,'r') as urllist:
        for url in urllist.read().splitlines():
            #print(url)
            data = scrape(url)
            dataList = data.values()
            substring = "$"
            name = ""
            for item in dataList:
                # no information was retrieved from the data point
                if isinstance(item, type(None)):
                    pass
                # the name of the product was retrieved
                elif item.find(substring) == -1:
                    name = str(item)
                else:
                    # the price of a product was found
                    # remove punctuation and special chars
                    item = item.lstrip("$")
                    item = item.replace(',' , '')
                    item = float(item)

                    # determine whether or not the product is being scalped; set in config.yml
                    if item <= priceThreshold:

                        # stop loop from continuing
                        global contRunning
                        contRunning = False

                        # if sms is enabled; send sms
                        if sms:
                            confirmText = sendText(str(name + " is in stock on " + userTime + " " + url))
                            if confirmText == 1:
                                print("Sent text(s).")
                            else:
                                print("Failed to send text message. Check the logs.")

                        # if email is enabled; send email
                        if email:
                            confirmEmail = sendEmail(str(name + " is in stock on " + userTime + " " + url))
                            if confirmEmail == 1:
                                print("Sent email(s).")
                            else:
                                print("Failed to send email.")

                        # if twitter status update is enabled; tweet
                        if tweet:
                            confirmTweet = sendTweet(str(name + " is in stock on " + userTime + " " + url))
                            if confirmTweet == 1:
                                print("Sent tweet.")
                            else:
                                print("Failed to send tweet.")

                        # if twitter direct messages are enabled; send dm
                        if enabledDM:
                            confirmDM = sendDM(str(name + " is in stock on " + userTime + " " + url))
                            if confirmDM == 1:
                                print("Sent DM(s).")
                            else:
                                print("Failed to send DM.")

                        #send link to console
                        print("Stock found at " + url)

                        #exit loop
                        return None

    #close list of urls
    urllist.close()

# continually runs program until terminated
while contRunning == True:
    try:
        run()
    # catch keyboard interrupt and close program more gracefully
    except KeyboardInterrupt:
        print("Terminating...")
        time.sleep(1)
        contRunning = False
        time.sleep(2)
        sys.exit(0)


# forked from scrapehero and heavily modified by decampc <3
