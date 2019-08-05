#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hashflag.settings")

from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from tweet_alert.models import Digest, Tweet

import sys
import datetime

FROM_EMAIL = "noreply@hashflag-alert.com"
# Add tweets from the API instead of from the Tweet database.
USE_API = True

# In case I can't get cron jobs for streaming+digestion set up properly, use twitter api search as a backup.
import tweepy

def render_and_send(to_email, tweets, context, plain_template, rich_template):
    """
    Render the rich and plain text email templates using the
    """

    plaintext = get_template(plain_template)
    htmly = get_template(rich_template)

    context["digest_tweets"] = tweets
    context["num_tweets"] = len(tweets)

    subject = "HashFlag %s Tweet Digest"
    from_email, to = FROM_EMAIL, to_email
    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, ["stephen.tsimidis@gmail.com"])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_digests():
    for digest in Digest.objects.filter(sent=False, end_date__lt=datetime.datetime.now()):
        alert = digest.alert
        user = alert.user
        frequency = alert.get_frequency_display()
        track_string = map(lambda k: k.keyword, alert.keywords.all())
        if not user.spam_protected:
            for tweet in tweepy.api.search(track_string):
                try:
                    db_tweet = Tweet.create_from_tweepy(tweet)
                    digest.tweets.add(db_tweet)
                except Exception, e:
                    print >> sys.stderr, "Encountered Exception", e

            tweets = digest.tweets.all()
            d = Context({
                "frequency": frequency.lower(),
                "keywords": track_string
            })

            render_and_send(user.email, tweets, d, "email/digest-plaintext.txt", "email/digest.html")

            digest.sent = True
            digest.save()

            # Create the new current digest for the alert.
            new_digest = Digest(alert=alert, start_date=datetime.datetime.now())
            new_digest.snap_time()
            new_digest.save()
        else:
            try:
                alert.delete()
                digest.delete()
            except Exception, e:
                print >> sys.stderr, "Encountered Exception", e

if __name__ == "__main__":
    send_digests()