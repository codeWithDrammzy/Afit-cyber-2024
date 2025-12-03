from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import *
from .models import *


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

# @login_required
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('my_login')
    
    # Get current user
    user = request.user
    
    # Calculate stats
    active_reports = Item.objects.filter(reported_by=user, status__in=['lost', 'found']).count()
    
    # Items found by current user (found items they reported)
    items_found = Item.objects.filter(reported_by=user, status='found').count()
    
    # Pending claims (items reported by user that are found and not yet claimed)
    pending_claims = Item.objects.filter(
        reported_by=user, 
        status='found',
        claimed_by__isnull=True
    ).count()
    
    # Resolved cases (items that have been claimed or returned)
    resolved_cases = Item.objects.filter(
        reported_by=user,
        status__in=['returned']
    ).count()
    
    # Recently found items (found by others, not by current user)
    recently_found = Item.objects.filter(
        status='found',
        reported_by__student__isnull=False  # Only items reported by students
    ).exclude(reported_by=user).order_by('-date_reported')[:4]
    
    # User's recent items
    user_recent_items = Item.objects.filter(reported_by=user).order_by('-date_reported')[:5]
    
    context = {
        'user': user,
        'active_reports': active_reports,
        'items_found': items_found,
        'pending_claims': pending_claims,
        'resolved_cases': resolved_cases,
        'recently_found_items': recently_found,
        'user_recent_items': user_recent_items,
    }
    
    return render(request, "Lost_Found/studentPage/std-board.html", context)

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Item
from django.core.paginator import Paginator


@login_required
def lost_item(request):
    # Get all lost items, ordered by most recent
    lost_items = Item.objects.filter(status='lost').order_by('-date_reported')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        lost_items = lost_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_lost__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        lost_items = lost_items.filter(category=category_filter)
    
    # Filter by date (last 24 hours)
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        from django.utils import timezone
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        lost_items = lost_items.filter(date_occurred__gte=yesterday)
    elif date_filter == 'week':
        from django.utils import timezone
        from datetime import timedelta
        last_week = timezone.now() - timedelta(days=7)
        lost_items = lost_items.filter(date_occurred__gte=last_week)
    
    # Pagination
    paginator = Paginator(lost_items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique categories for filter
    categories = Item.CATEGORY_CHOICES
    
    context = {
        'lost_items': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_date': date_filter,
        'total_items': lost_items.count(),
    }
    
    return render(request, 'Lost_Found/studentPage/lost-item.html', context)


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemReportForm

def report_item(request):
    form = ItemReportForm()
    
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user  # Same as product.farmer = request.user.farmermodel
            item.save()
            messages.success(request, f'Item "{item.title}" has been reported successfully!')
            return redirect('std-board')  # Change to your desired redirect
    
    context = {
        'form': form,
    }
    return render(request, 'Lost_Found/studentPage/report-item.html', context)


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Item
from django.core.paginator import Paginator

@login_required
def found_item(request):
    # Get all found items, ordered by most recent
    found_items = Item.objects.filter(status='found').order_by('-date_reported')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        found_items = found_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_found__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        found_items = found_items.filter(category=category_filter)
    
    # Filter by claim status
    claim_filter = request.GET.get('claim', '')
    if claim_filter == 'unclaimed':
        found_items = found_items.filter(claimed_by__isnull=True)
    elif claim_filter == 'claimed':
        found_items = found_items.filter(claimed_by__isnull=False)
    
    # Filter by date (last 24 hours)
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        from django.utils import timezone
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        found_items = found_items.filter(date_occurred__gte=yesterday)
    elif date_filter == 'week':
        from django.utils import timezone
        from datetime import timedelta
        last_week = timezone.now() - timedelta(days=7)
        found_items = found_items.filter(date_occurred__gte=last_week)
    
    # Pagination
    paginator = Paginator(found_items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique categories for filter
    categories = Item.CATEGORY_CHOICES
    
    context = {
        'found_items': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_date': date_filter,
        'selected_claim': claim_filter,
        'total_items': found_items.count(),
    }
    
    return render(request, 'Lost_Found/studentPage/found-item.html', context)

def my_report(request):
    return render(request , 'Lost_Found/studentPage/my-report.html')


# ============= Admin Dashbard =========
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.user_type != 'admin':
        return redirect('my_login')
    return render(request, "Lost_Found/admin_dashboard.html")