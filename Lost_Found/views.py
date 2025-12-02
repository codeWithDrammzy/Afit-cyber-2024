from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import User, Student


# =========== Homes & Authentification ============
def index(request):
    return render(request, "Lost_Found/homePages/index.html")

def register_page(request):
    form = StudentRegistrationForm()
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    phone_number=form.cleaned_data['phone_number'],
                    user_type='student'
                )
                
                # Create student profile
                Student.objects.create(
                    user=user,
                    matric_no=form.cleaned_data['matric_no'],
                    department=form.cleaned_data['department'],
                    level=form.cleaned_data['level']
                )
                
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('my_login')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, "Lost_Found/homePages/register.html", {'form': form})

def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('admin_dashboard')  # You'll need to create this view
            else:
                return redirect('std-board')  # You'll need to create this view
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, "Lost_Found/homePages/my-login.html")

def my_logout(request):
    logout(request)
    return redirect('index')


# ============= Student Dashbard =========

def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('my_login')
    return render(request, "Lost_Found/studentPage/std-board.html")


def lost_item(request):
    return render(request , 'Lost_Found/studentPage/lost-item.html')

def report_item(request):
    return render(request , 'Lost_Found/studentPage/report-item.html')


def found_item(request):
    return render(request , 'Lost_Found/studentPage/found-item.html')

def my_report(request):
    return render(request , 'Lost_Found/studentPage/my-report.html')


# ============= Admin Dashbard =========
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.user_type != 'admin':
        return redirect('my_login')
    return render(request, "Lost_Found/admin_dashboard.html")