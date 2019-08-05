from tweet_alert.models import Tweet, Keyword, Digest, Alert, EmailUser
from django.contrib import admin

admin.site.register(Keyword)
admin.site.register(Digest)
admin.site.register(Alert)
admin.site.register(EmailUser)

class TweetAdmin(admin.ModelAdmin):
    fields = ["text", "submit_time", "twitter_user", "full_name", "url"]
    list_display = ['text', 'submit_time', "screen_name", "full_name", "url"]

admin.site.register(Tweet, TweetAdmin)