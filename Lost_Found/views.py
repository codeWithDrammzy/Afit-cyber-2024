from django.shortcuts import render

def index(request):
    return render(request ,"Lost_Found/homePages/index.html")

def register_page(request):
    return render(request ,"Lost_Found/homePages/register.html")

def my_login(request):
    return render(request ,"Lost_Found/homePages/my-login.html")



# Create your views here.
