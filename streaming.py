__author__ = 'Stephen'

import os
import tweepy
import sys
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hashflag.settings")
from tweet_alert.models import Keyword, Tweet

# Obtained from dev.twitter.com
CONSUMER_KEY = 'wdmOg4OVR4otYRrzuPqIMA'
CONSUMER_SECRET = 'IqhhCNXxEaF0tj1WE3pcJrrbxCDG422RlY53T18Y7U'

ACCESS_TOKEN = '370966704-hQZOS9fdKohUEIMOm3X6LXc0Lf2FqPjahybRQ0zo'
ACCESS_TOKEN_SECRET = 'PyztovwGFn2wqRIOFltMRcKvSYkenRpAPLc4KDVs'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

class KeywordStreamListener(tweepy.StreamListener):
    """
    Listen for tweets that contain keywords from the Keyword bank, and save the tweets to the database.

    This listener is intended to run indefinitely, but may need to stop periodically in order to change the
    set of keywords it listens to.
    """

    def on_status(self, status):
        """
        Add the status to the database, and timestamp it with the current local time on the server.
        """

        try:
            Tweet.create_from_tweepy(status)
        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

# Create a streaming API and set a timeout value of 60 seconds.
streaming_api = tweepy.streaming.Stream(auth, KeywordStreamListener(), timeout=60)

if __name__ == "__main__":
    keywords = [unicode(keyword) for keyword in Keyword.objects.all()]
    print >> sys.stderr, 'Tracking keywords: %s' % ', '.join(keywords)

    streaming_api.filter(follow=None, track=keywords)