import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hashflag.settings")
from tweet_alert.models import Alert, Tweet

def digest_new_tweets():
    """
    Look through the tweet table for any tweets that were added since the last digestion. If the alert is instant,
    send the tweet using the mailer. Otherwise, add the tweet to the alert's digest.
    """

    for alert in Alert.objects.all():
        last_added = alert.last_added_date
        for tweet in Tweet.objects.filter(submit_time__gt=alert.last_added_date):
            if tweet.alert_matches(alert):
                alert.active_digest().tweets.add(tweet)
                last_added = max(last_added, tweet.submit_time)
                alert.active_digest().save()
        alert.last_added_date = last_added
        alert.save()

if __name__ == "__main__":
    while True:
        try:
            digest_new_tweets()
        except Exception, e:
            print >> sys.stderr, e.message