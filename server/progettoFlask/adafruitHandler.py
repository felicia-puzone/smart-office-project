from Adafruit_IO import Client, Feed
ADAFRUIT_IO_USERNAME = "Billy9658"
ADAFRUIT_IO_KEY = "aio_UDiM62dm7xBddVlfSG7Y1drWle6E"
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_USERNAME)
#username=Billy9658
#password=FeedProgettoIOT
#password swagger=SwaggerProgettoIOT2022

#TODO testing
def sendDataToAdafruitFeed(feedName,value):
    feed = aio.feeds(feedName)
    if feed:
        aio.create_data(feedName,value)
        return True
    else:
        feed = Feed(name=feedName)
        result = aio.create_feed(feed)
        if result:
            aio.create_data(feedName, value)
            return True
    return False