from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

import sys

class EmailUser(User):
    """
    A user who is identified by his or her email address.
    """

    # Allow users to block this email from being sent alerts from this site.
    spam_protected = models.BooleanField(default=False)

class Keyword(models.Model):
    """
    Keywords used to track tweets.
    """

    keyword = models.CharField(max_length=40)

    def __unicode__(self):
        return self.keyword

class Tweet(models.Model):
    """
    A tweet status that consists of a status message, twitter user, and a set of keywords.
    """

    text = models.TextField(max_length=240)
    twitter_user = models.CharField(max_length=70)
    submit_time = models.DateTimeField()
    full_name = models.CharField(max_length=70)
    url = models.URLField()

    def __unicode__(self):
        return self.text

    def screen_name(self):
        """
        Return the screen name representation for this Tweet's associated screen name.
        """

        return "@%s" % self.twitter_user

    def alert_matches(self, alert):
        """
        Return whether the text in this tweet matches the keywords in the alert. Follow the same format as
        the twitter stream api: spaces within a keyword act as logical AND, different keyword entries as OR,
        and hashtags (#) are ignored.
        """

        res = False
        for keyword_entry in alert.keywords.all():
            all_match = True
            for keyword in map(lambda word: word.strip().lower().lstrip("#"),
                               keyword_entry.keyword.split()):
                if not (keyword in self.text.lower()):
                    all_match = False
            res = res or all_match
            if res:
                break
        return res

    @staticmethod
    def create_from_tweepy(tweepy_status):
        """
        Convert a tweepy twitter status object into a database tweet, and return the database version.
        """

        tweet = Tweet(
            text=tweepy_status.text,
            twitter_user=tweepy_status.from_user,
            submit_time=datetime.now(),
            full_name=tweepy_status.from_user,
            #full_name=tweepy_status.author.name
        )
        tweet.url = 'http://twitter.com/%s/status/%s' % (tweet.twitter_user, tweepy_status.id_str)
        tweet.save()
        return tweet

class Alert(models.Model):
    """
    An alert that tracks a set of keywords and sends users a periodic digest of tweets, or the tweets themselves,
    that are relevant to its set of keywords.
    """

    keywords = models.ManyToManyField(Keyword)
    FREQUENCY_CHOICES = (
        ("I", "Instant"),
        ("D", "Daily"),
        ("H", "Hourly")
    )
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    last_added_date = models.DateTimeField()
    user = models.ForeignKey(EmailUser)

    def __unicode__(self):
        return self.get_frequency_display() + ": " +  ", ".join([unicode(keyword) for keyword in self.keywords.all()])

    def active_digest(self):
        """
        Return the currently active digest being used with this alert, or None if the alert delivers instantly.
        """
        if self.frequency != "I":
            return self.digest_set.get(sent=False)
        else:
            return None

    def is_daily(self):
        """
        Return whether this alert represents one that sends a daily digest.
        """

        return self.frequency == "D"

    def is_hourly(self):
        """
        Return whether this alert represents one that sends an hourly digest.
        """

        return self.frequency == "H"

    def is_instant(self):
        """
        Return whether this alert represents one that sends tweets instantly as they come in.
        """

        return self.frequency == "I"

class Digest(models.Model):
    """
    A digest that accumulates tweets to be sent either daily or hourly. Does not apply to alerts that deliver
    tweets instantly.
    """

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tweets = models.ManyToManyField(Tweet, null=True, blank=True)
    sent = models.BooleanField(default=False)
    alert = models.ForeignKey(Alert, null=True)

    def __unicode__(self):
        return "%s: %s; closes %s" % ("SENT" if self.sent else "UNSENT", unicode(self.alert), self.end_date)

    def snap_time(self):
        """
        Snap the start and end dates to the nearest whole hour or day.
        """

        if self.alert.is_daily():
            # Set delivery to next day.
            self.start_date = datetime(self.start_date.year, self.start_date.month, self.start_date.day)
            self.end_date = self.start_date + timedelta(days=1)
        elif self.alert.is_hourly():
            # Set delivery to next hour.
            self.start_date = datetime(self.start_date.year, self.start_date.month, self.start_date.day,
                self.start_date.hour)
            self.end_date = self.start_date + timedelta(hours=1)

    def expired_digests(cls):
        """
        Return a QuerySet of all unsent digests that are now past their end date.
        """

        return cls.objects.filter(send=False, end_date__lt=datetime.now())