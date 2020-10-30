from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Court, MapStyle, MapAPIKey, Signup
from tablib import Dataset
from .resources import CourtResource
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.template import loader
from rest_framework import viewsets, permissions
from .serializers import UserSerializer, GroupSerializer, CourtSerializer, MapStyleSerializer, MapAPIKeySerializer
from .forms import EmailSignupForm
import requests, json

# Create your views here.
def email_list_signup(request):
    form = EmailSignupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = Signup.objects.filter(email=form.instance.email)
            if email_signup_qs.exists():
                messages.info(request, "You are already subscribed!")
            else:
                form.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def simple_upload(request):
    if request.method == 'POST':
        court_resource = CourtResource()
        dataset = Dataset()
        new_persons = request.FILES['myfile']

        imported_data = dataset.load(new_persons.read())
        result = court_resource.import_data(dataset, dry_run=True)  # Test the data import

        if not result.has_errors():
            court_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'core/simple_upload.html')

def home(request):
    form = EmailSignupForm(request.POST or None)
    if request.method == "POST" or None:
        email = request.POST["email"]
        # check if email already exists in database, if
        if form.is_valid():
            new_signup = Signup()
            new_signup.email = email
            new_signup.save()            
    context = {
        'form': form
    }
    return render(request, 'courts/home/index.html', context)

@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",

    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# Loader.io Verification
def loaderio(request):
    return HttpResponse("loaderio-bfdc71f8924d72801af8766b33d8a6a4", content_type="text/plain")


def detail(request):
    """
    Courts Page
    """
    style = MapStyle.objects.get(active=True)  # get map that is currently active
    mapbox_key = MapAPIKey.objects.get(
        active=True)  # get first api_key; only should be one, can be changed later if rotating api keys etc.

    t = loader.get_template('courts/map/index.html')

    c = {'map_style': style, 'api_key': mapbox_key.api_key, }  # page data
    return HttpResponse(t.render(c))

# Error 500 page
def handler500(request):
    return render(request, '500/index.html', status=500)


# API METHODS
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class MapStyleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = MapStyle.objects.all()
    serializer_class = MapStyleSerializer


class ActiveMapStyleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = MapStyle.objects.filter(active=True)  # get map that is currently active
    serializer_class = MapStyleSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourtViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Court.objects.all()
    serializer_class = CourtSerializer


class MapAPIKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = MapAPIKey.objects.all()
    serializer_class = MapAPIKeySerializer

def anomaly(request):
    """
    Page to view anomaly / db statistical data
    """
    state_count = Court.objects.filter(state="unknown").count()
    country_count = Court.objects.filter(country="unknown").count()
    road_count = Court.objects.filter(road="unknown").count()
    total_basketball = Court.objects.filter(category="Basketball").count() # total courts
    total_tennis = Court.objects.filter(category="Tennis").count()  # total courts
    total_soccer = Court.objects.filter(category="Soccer").count()  # total courts
    total_users = User.objects.all().count() # total amount of users

    t = loader.get_template('anomaly/index.html')
    c = {'state_count': state_count, 'country_count': country_count, 'total_basketball': total_basketball, 'total_soccer': total_soccer, 'total_tennis': total_tennis, 'road_count': road_count, 'users_count': total_users}
    return HttpResponse(t.render(c))
