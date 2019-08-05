from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import tweet_alert

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hashflag.views.home', name='home'),
    # url(r'^hashflag/', include('hashflag.foo.urls')),
    url(r'^$', 'tweet_alert.views.create_alert'),
    url(r'^create/$', 'tweet_alert.views.create_alert'),
    url(r'^success/$', 'tweet_alert.views.alert_success'),
    url(r'^digests/(?P<digest_id>\d+)/$', 'tweet_alert.views.digest'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}),
    url(r'^register/$', 'tweet_alert.views.register'),
    url(r'^settings/$', 'tweet_alert.views.settings'),
    url(r'^example/$', 'tweet_alert.views.example'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
