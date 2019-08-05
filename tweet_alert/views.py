from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from tweet_alert.models import Keyword, Alert, EmailUser, Digest
from tweet_alert.forms import AlertForm, RegistrationForm

#from recaptcha_client import captcha
import datetime
import tweepy

RECAPTCHA_PRIVATE_KEY = "<>"

def alert_success(request):
    return render_to_response("alert-success.html", {}, context_instance=RequestContext(request))

def create_alert(request):
    """
    Create a new alert from POST data, then either redirect to the success page or to an
    error page explaining what failed.
    """

    response_data = {}
    response_data["trends"] = Keyword.objects.all()[:10] # placeholder data
    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            track_keywords = request.POST["track"]
            email = request.POST["email"]
            #register_member = request.POST["register-member"]
            use_digests =  request.POST["message-setting"] == "digest" # instant or digest
            if use_digests:
                daily = request.POST["frequency"] == "daily" # daily or hourly
                digest_all = request.POST["digest-size"] == "all" # all or last-x
            else:
                daily = False
                digest_all = None
            try:
                digest_size_amount = int(request.POST["digest-size-input"]) if digest_all else 0
            except:
                digest_size_amount = 0

            # Failsafes in case user's javascript was disabled.
            if not track_keywords and not request.POST["keyword"]:
                response_data["keyword_errors"] = "You must enter at least one keyword."
            else:
                user, is_new_user = EmailUser.objects.get_or_create(username=email, email=email)
                if is_new_user:
                    # Don't want the user to try logging in before registering.
                    user.set_unusable_password()
                    user.save()
                if user.spam_protected:
                    return HttpResponseRedirect(reverse("tweet_alert.views.error"))

                alert = Alert(frequency=("I" if not use_digests else ("D" if daily else "H")),
                    last_added_date=datetime.datetime.now(),
                    user=user)
                alert.save()

                if use_digests:
                    digest = Digest(start_date=datetime.datetime.now(), sent=False, alert=alert)
                    digest.snap_time()
                    digest.save()

                if not track_keywords:
                    keyword, is_new_keyword = Keyword.objects.get_or_create(keyword=request.POST["keyword"].strip())
                    alert.keywords.add(keyword)
                else:
                    for word in track_keywords.split(","):
                        keyword, is_new_keyword = Keyword.objects.get_or_create(keyword=word.strip())
                        alert.keywords.add(keyword)
                return HttpResponseRedirect(reverse("tweet_alert.views.alert_success"))
    else:
        form = AlertForm()
    response_data["form"] = form
    return render_to_response("base-home.html", response_data, context_instance=RequestContext(request))

def login(request):
    return render_to_response("registration/login.html", {}, context_instance=RequestContext(request))

def register(request):
    password_errors = []
    if request.user.is_authenticated():
        HttpResponseRedirect(reverse("tweet_alert.views.create_alert"))
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = request.POST["password"]
            password_confirm = request.POST["password-confirm"]

            if password == password_confirm :
                if len(password) > 6 and not (password.isdigit() or password.isalpha()):
                    user, is_new = EmailUser.objects.get_or_create(username=email)
                    if not is_new and user.has_usable_password():
                        password_errors.append("You already have an account. Forgot your password? Click <a href='#'>here</a>.")
                    else:
                        user.email = email
                        user.set_password(password)
                        user.save()
                        return HttpResponseRedirect(reverse("django.contrib.auth.views.login"))
                else:
                    password_errors.append("Your password must be at least six characters long with at least one alpha and one numeric character")
            else:
                password_errors.append("The passwords do not match.")
    else:
        form = RegistrationForm()

    return render_to_response("registration/register.html", {"form": form, "password_errors": password_errors},
        context_instance=RequestContext(request))

def settings(request):
    if request.user.is_authenticated():
        return render_to_response("registration/settings.html", {}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse("tweet_alert.views.create_alert"))

def example(request):
    return render_to_response("example-home.html", {}, context_instance=RequestContext(request))

def error(request):
    return HttpResponse("An error occurred")

def digest(request, digest_id):
    """
    Render the digest email to the browser.
    """

    digest = Digest.objects.get(pk=digest_id)
    alert = digest.alert
    user = alert.user
    frequency = alert.get_frequency_display().lower()
    keywords = ", ".join(map(str, alert.keywords.all()))

    if user.spam_protected:
        return HttpResponse("User has requested spam protection and will not be sent this digest.")

    return render_to_response("email/digest.html", {
        "user_email": user.email,
        "frequency": frequency,
        "digest_tweets": digest.tweets.order_by("-submit_time")[:20], # placeholder for number of tweets per digest
        "num_tweets": 20,
        "keyword_string": keywords
     }, context_instance=RequestContext(request))