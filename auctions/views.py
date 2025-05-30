from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Listing, Category, Bid, Comment


def index(request):
    if len(Listing.objects.all().filter(active=True))==0:
        return render(request, "auctions/error.html")
    else:
        return render(request, "auctions/index.html", {
                "listings" : Listing.objects.all().filter(active=True)
        })
        

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Listing form
class NewListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'style': 'width:70%', 'class': 'form-control', 'placeholder':'Enter the name of the product',
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width:70%', 'class': 'form-control', 
        'placeholder':'Enter the product specifications like size, condition, instructions for use, and restrictions'
    }))
    price = forms.DecimalField(min_value=1.00, widget=forms.NumberInput(attrs={
        'style': 'width:70%', 'class': 'form-control', 'placeholder':'This price will be the starting bid'
    }))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), 
            widget=forms.Select(attrs={
            'style': 'width:70%', 'class': 'form-control',
    }))
    imgURL = forms.CharField(widget=forms.TextInput(attrs={
        'style': 'width:70%', 'class': 'form-control', 'placeholder':'Enter url of the product image'
    }))

# Bid form 
class BidForm(forms.Form):
    bid = forms.DecimalField(min_value=1.00, widget=forms.NumberInput(attrs={
        'style': 'width:70%', 'class': 'form-control', 'placeholder':'Make sure bid is greater than price'
    }))

# Comment form
class CommentForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'style': 'width:70%', 'class': 'form-control', 'placeholder':'Enter the main points in 5 to 10 words',
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width:70%', 'class': 'form-control', 
        'placeholder':'Enter your product review or any other comments'
    }))


# Create a new Listing
def create_listing(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            imageURL = form.cleaned_data["imgURL"]
            user = request.user
            start_bid = Bid(price=price, user=user)
            start_bid.save()
            newListing = Listing(title=title, description=description, seller=user,
                price=price, category=category, imageURL=imageURL, latest_bid=start_bid )
            newListing.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return render(request, "auctions/create_listing.html",{
            "form" : form,
            "message" : "error"
            })
    else:
        return render(request, "auctions/create_listing.html",{
            "form" : NewListingForm()
        })
    

# Listing page
def listing_page(request, id):
    listing = Listing.objects.all().get(pk=id)
    user_is_seller = False
    if request.user.is_authenticated:
        if(listing.seller == request.user):
            user_is_seller = True
    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "bid_form" : BidForm(),
        "user_is_seller" : user_is_seller,
        "user" : request.user,
        "comment_form" : CommentForm(),
    })


# Place bid
def place_bid(request, id):
    listing = Listing.objects.all().get(pk=id)
    if not request.user.is_authenticated:
        return render(request, "auctions/listing_page.html", {
                "listing": listing,
                "bid_form" : BidForm(),
                "message" : "not sign in"
        })
    else:
        if request.method=="POST":
            form = BidForm(request.POST)
            if form.is_valid():
                placed_bid = form.cleaned_data["bid"]
                if placed_bid>listing.price:
                    curr_bid = Bid(price=placed_bid, user=request.user)
                    curr_bid.save()
                    listing.price = placed_bid
                    listing.latest_bid = curr_bid
                    listing.save()
                    return render(request, "auctions/listing_page.html", {
                        "listing": listing,
                        "bid_form" : form,
                        "message" : "success",
                    })
                else:
                    return render(request, "auctions/listing_page.html", {
                        "listing": listing,
                        "bid_form" : form,
                        "message" : "fail"
                    })
            else:
                return render(request, "auctions/listing_page.html", {
                "listing": listing,
                "bid_form" : form,
                "message" : "fail"
                })
        else:
            return HttpResponseRedirect(reverse(index))
    
# List of Categories
def all_categories(request):
    return render(request, "auctions/all_categories.html", {
        "categories" : Category.objects.all()
    })

def category_list(request, id):
    category = Category.objects.all().get(pk=id)
    if len(category.listings.all())==0:
        return render(request, "auctions/error.html")
    else:
        return render(request, "auctions/index.html", {
            "listings" : category.listings.all()
        })
    
# Close auction
def close_auction(request, id):
    if request.method=="POST":
        listing = Listing.objects.all().get(pk=id)
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse(listing_page))
    else:
        return HttpResponseRedirect(reverse(listing_page))
    
# Make comment
def add_comment(request, id):
    if request.user.is_authenticated:
        if request.method=="POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                content = form.cleaned_data["content"]
                com = Comment(title=title, content=content, 
                    listing=Listing.objects.all().get(pk=id), user=request.user)
                com.save()
                return HttpResponseRedirect(reverse(listing_page, args=(id,)))
            else:
                return HttpResponseRedirect(reverse(listing_page, args=(id,)))
        else:
            return HttpResponseRedirect(reverse(listing_page, args=(id,)))
    else:
        return HttpResponseRedirect(reverse(listing_page, args=(id,)))