"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from tweet_alert.models import Tweet, Alert, Keyword, EmailUser
from datetime import datetime

class TweetTest(TestCase):
    def setUp(self):
        self.user = EmailUser.objects.create(username="admin")
        self.keyword = Keyword.objects.create(keyword="travel")
        self.alert = Alert.objects.create(frequency="I", last_added_date=datetime.now(), user=self.user)

        self.alert.keywords.add(self.keyword)
        self.alert.save()

    def test_matches_alert_match_one(self):
        """
        Test that an alert with one keyword matches a tweet that contains that keyword.
        """

        tweet = Tweet(text="If a gnome can travel, so can I.", twitter_user="schmoe", submit_time=datetime.now(),
            full_name="Joe Schmoe", url="")
        tweet.save()

        result = tweet.alert_matches(self.alert)

        self.assertTrue(result, "Expected tweet to match alert, but it did not.")

    def test_matches_alert_match_one(self):
        """
        Test that an alert with one keyword does not match a tweet that does not contain that keyword
        """

        tweet = Tweet(text="It's a vacation", twitter_user="schmoe", submit_time=datetime.now(),
            full_name="Joe Schmoe", url="")
        tweet.save()

        result = tweet.alert_matches(self.alert)

        self.assertFalse(result, "Expected tweet not to match alert, but it did.")