from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, DealerReview, CarModel, CarMake
from .restapis import get_dealers_from_cf,get_dealer_reviews_from_cf,post_request,get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from operator import truediv
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

#index
# def index(request):
#     context = {}
#     return render(request, 'djangoapp/index.html', context)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/registration.html', context)
    else:
        return render(request, 'djangoapp/registration.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/461b4d00-9de7-4d69-900d-ba2051d41283/default/get-dealership"
        dealerships = get_dealers_from_cf(url)
        context = {}
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/461b4d00-9de7-4d69-900d-ba2051d41283/default/get-review"
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/461b4d00-9de7-4d69-900d-ba2051d41283/default/get-dealership"
        reviews = get_dealer_reviews_from_cf(url, id = dealer_id)
        dealer_detail = get_dealer_by_id_from_cf(dealer_url,dealer_id)
        context = {
            "reviews": reviews,
            "dealer_id": dealer_id,
            "dealer": dealer_detail
        }
        print(context)
        return render(request, 'djangoapp/dealer_details.html', context)
        

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    if request.user.is_authenticated:
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/461b4d00-9de7-4d69-900d-ba2051d41283/default/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        context["dealer"] = dealer
        if request.method == "GET":
            cars = CarModel.objects.all()
            context["cars"] = cars
            print(context)
            return render(request, 'djangoapp/add_review.html', context)
        
        if request.method == "POST":
            if request.user.is_authenticated:
                username = request.user.username
                print(request.POST)
                form = request.POST 
                payload = dict()
                car_id = form.get("car")
                car = CarModel.objects.get(pk=car_id)
                print(car)
                payload["name"] = username
                payload["dealership"] = dealer_id
                payload["id"] = dealer_id
                payload["review"] = form.get("review")
                payload["purchase"] = False
                if "purchasecheck" in request.POST:
                    if request.POST["purchasecheck"] == 'on':
                        payload["purchase"] = True
                payload["purchase_date"] = form.get("purchase_date")
                payload["car_make"] = car.make.name
                payload["car_model"] = car.name
                payload["car_year"] = int(car.year)
                new_payload = {}
                new_payload["review"] = payload
                review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/461b4d00-9de7-4d69-900d-ba2051d41283/default/post-review"
                # review_post_url = "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/e9636849-8371-4d0c-b18b-9205c9c37441/actions/dealership-package/post-review"
                post_request(review_post_url, new_payload, id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    else:
        return redirect("/djangoapp/login")