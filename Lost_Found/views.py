from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from .forms import *
from .models import Item, Student, User


# ================= HOME & AUTH ==================
import random

def index(request):
 
    all_items = list(Item.objects.all())
    
    # Calculate statistics
    total_reports = len(all_items)
    found_items_count = len([item for item in all_items if item.status == 'found'])
    returned_items_count = len([item for item in all_items if item.status == 'returned'])
    
    # Get 4 random items (or all if less than 4)
    if len(all_items) >= 4:
        latest_items = random.sample(all_items, 4)
    elif all_items:
        latest_items = all_items
    else:
        latest_items = []
    
    context = {
        'total_reports': total_reports,
        'found_items_count': found_items_count,
        'returned_items_count': returned_items_count,
        'latest_items': latest_items,
    }
    
    return render(request, "Lost_Found/homePages/index.html", context)

def about(request):
    return render(request, "Lost_Found/homePages/about.html")

def my_logout(request):
    logout(request)
    return redirect('index')


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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Please provide both matric number/email and password.')
            return render(request, "Lost_Found/homePages/my-login.html")
        user = authenticate(request, username=username, password=password)
        
        print(f"👤 DEBUG: Authentication result: {user}")
        
        if user:
            login(request, user)
            print(f"✅ DEBUG: Login successful for: {user.username}")
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            if not user.is_verified:
                messages.warning(request, 'Please verify your email address to access all features.')
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            else:  
                return redirect('std-board')
        else:
            print("❌ DEBUG: Authentication failed")
        
        messages.error(request, 'Invalid matric number/email or password.')
    
    return render(request, "Lost_Found/homePages/my-login.html")




 # ================= STUDENT DASHBOARD ==================
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('my_login')

    user = request.user
    
    active_reports = Item.objects.filter(reported_by=user, status__in=['lost', 'found']).count()
    items_found = Item.objects.filter(reported_by=user, status='found').count()
    pending_claims = Item.objects.filter(reported_by=user, status='found', claimed_by__isnull=True).count()
    resolved_cases = Item.objects.filter(reported_by=user, status='returned').count()
    
    recently_found = Item.objects.filter(
        status='found',
        reported_by__student__isnull=False
    ).exclude(reported_by=user).order_by('-date_reported')[:4]
    
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


# ================= LOST ITEMS ==================
@login_required
def lost_item(request):
    lost_items = Item.objects.filter(status='lost').order_by('-date_reported')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        lost_items = lost_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_lost__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        lost_items = lost_items.filter(category=category_filter)

    # Date filter
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        lost_items = lost_items.filter(date_occurred__gte=timezone.now() - timedelta(days=1))
    elif date_filter == 'week':
        lost_items = lost_items.filter(date_occurred__gte=timezone.now() - timedelta(days=7))

    # Pagination
    paginator = Paginator(lost_items, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'lost_items': page_obj,
        'categories': Item.CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_date': date_filter,
        'total_items': lost_items.count(),
    }

    return render(request, 'Lost_Found/studentPage/lost-item.html', context)


# ================= REPORT ITEM ==================
@login_required
def report_item(request):
    form = ItemReportForm()
    
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()
            messages.success(request, f'Item "{item.title}" has been reported successfully!')
            return redirect('std-board')
    
    return render(request, 'Lost_Found/studentPage/report-item.html', {'form': form})


# ================= FOUND ITEMS ==================
@login_required
def found_item(request):
    found_items = Item.objects.filter(status='found').order_by('-date_reported')

    search_query = request.GET.get('search', '')
    if search_query:
        found_items = found_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_found__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        found_items = found_items.filter(category=category_filter)

    # Claim filter
    claim_filter = request.GET.get('claim', '')
    if claim_filter == 'unclaimed':
        found_items = found_items.filter(claimed_by__isnull=True)
    elif claim_filter == 'claimed':
        found_items = found_items.filter(claimed_by__isnull=False)

    # Date filter
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        found_items = found_items.filter(date_occurred__gte=timezone.now() - timedelta(days=1))
    elif date_filter == 'week':
        found_items = found_items.filter(date_occurred__gte=timezone.now() - timedelta(days=7))

    # Pagination
    paginator = Paginator(found_items, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'found_items': page_obj,
        'categories': Item.CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_date': date_filter,
        'selected_claim': claim_filter,
        'total_items': found_items.count(),
    }
    
    return render(request, 'Lost_Found/studentPage/found-item.html', context)



# ================= CLAIM ITEM ==================
@login_required
def claim_item(request, item_id):

    try:
        item = Item.objects.get(id=item_id)
        if item.status != 'found':
            messages.error(request, 'Only found items can be claimed.')
            return redirect('found-item')
        
        if item.claimed_by:
            messages.error(request, 'This item has already been claimed.')
            return redirect('found-item')
        
        if item.reported_by == request.user:
            messages.error(request, 'You cannot claim your own found item.')
            return redirect('found-item')
        
        item.claimed_by = request.user
        item.date_claimed = timezone.now()
        item.save()
        
        messages.success(
            request, 
            f'You have successfully claimed "{item.title}". '
            f'The finder ({item.reported_by.get_full_name() or item.reported_by.username}) will contact you.'
        )
        
        # Redirect back to found items or referer
        redirect_url = request.META.get('HTTP_REFERER', 'found-item')
        return redirect(redirect_url)
        
    except Item.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('found-item')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('found-item')

@login_required
def claim_confirmation(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        if item.status != 'found':
            messages.error(request, 'Only found items can be claimed.')
            return redirect('found-item')
        if item.claimed_by:
            messages.error(request, 'This item has already been claimed.')
            return redirect('found-item')
        if item.reported_by == request.user:
            messages.error(request, 'You cannot claim your own found item.')
            return redirect('found-item')
        
        context = {
            'item': item,
            'finder': item.reported_by,
        }
        return render(request, 'Lost_Found/studentPage/claim-confirmation.html', context)
    except Item.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('found-item')

@login_required
def my_report(request):
    # Get all items reported by the current user
    user_items = Item.objects.filter(reported_by=request.user)
    
    # Get counts for stats
    myReports = user_items.count()
    
    # Get counts by status (adjust field names based on your model)
    # Assuming you have a 'status' field with choices 'lost', 'found', 'claimed'
    lost_count = user_items.filter(status='lost').count()
    found_count = user_items.filter(status='found').count()
    claimed_count = user_items.filter(status='claimed').count()
    
    # If your model doesn't have status, but has item_type instead:
    # lost_count = user_items.filter(item_type='lost').count()
    # found_count = user_items.filter(item_type='found').count()
    # claimed_count = user_items.filter(claimed_by__isnull=False).count()
    
    # Get all items for display, ordered by most recent
    items = user_items.order_by('-date_reported')
    
    # Get category choices from Item model
    # First, check what your category field is called
    category_choices = []
    
    try:
        # Try to get CATEGORY_CHOICES from the Item model
        if hasattr(Item, 'CATEGORY_CHOICES'):
            category_choices = Item.CATEGORY_CHOICES
        elif hasattr(Item, 'CATEGORIES'):
            category_choices = Item.CATEGORIES
        elif hasattr(Item, 'category'):  # Get choices from field
            category_field = Item._meta.get_field('category')
            if hasattr(category_field, 'choices') and category_field.choices:
                category_choices = category_field.choices
    except:
        # Fallback categories if not defined
        category_choices = [
            ('electronics', 'Electronics'),
            ('documents', 'Documents'),
            ('clothing', 'Clothing'),
            ('accessories', 'Accessories'),
            ('books', 'Books'),
            ('other', 'Other'),
        ]
    
    context = {
        'myReports': myReports,
        'lost_count': lost_count,
        'found_count': found_count,
        'claimed_count': claimed_count,
        'items': items,
        'categories': category_choices,
    }
    return render(request, 'Lost_Found/studentPage/my-report.html', context)

# ================= MARK ITEM AS FOUND ==================
@login_required
def mark_as_found(request, item_id):
   
    try:
        item = Item.objects.get(id=item_id)
        if item.status != 'lost':
            messages.error(request, 'Only lost items can be marked as found.')
            return redirect('lost-item')
        
        if item.reported_by == request.user:
            messages.error(request, 'You cannot mark your own lost item as found.')
            return redirect('lost-item')
        item.status = 'found'
        item.location_found = request.POST.get('found_location', 'Not specified')
        item.save()
        

        messages.success(
            request, 
            f'You have marked "{item.title}" as found! '
            f'The owner ({item.reported_by.get_full_name() or item.reported_by.username}) has been notified.'
        )
        
        redirect_url = request.META.get('HTTP_REFERER', 'lost-item')
        return redirect(redirect_url)
        
    except Item.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('lost-item')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('lost-item')


# views.py - Add this view
@login_required
def found_confirmation(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        
        # Check if item is lost
        if item.status != 'lost':
            messages.error(request, 'Only lost items can be marked as found.')
            return redirect('lost-item')
        
        if item.reported_by == request.user:
            messages.error(request, 'You cannot mark your own lost item as found.')
            return redirect('lost-item')
        
        if request.method == 'POST':
            # Handle form submission
            found_location = request.POST.get('found_location', '')
            
            if not found_location:
                messages.error(request, 'Please provide where you found the item.')
                return redirect('found_confirmation', item_id=item_id)
            
            # Update item
            item.status = 'found'
            item.location_found = found_location
            item.save()
            
            messages.success(
                request, 
                f'You have marked "{item.title}" as found! '
                f'The owner has been notified.'
            )
            return redirect('lost-item')
        
        context = {
            'item': item,
            'owner': item.reported_by,
        }
        
        return render(request, 'Lost_Found/studentPage/found-confirmation.html', context)
        
    except Item.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('lost-item')

# ================= ADMIN DASHBOARD ==================
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.user_type != 'admin':
        return redirect('my_login')
    return render(request, "Lost_Found/admin_dashboard.html")
