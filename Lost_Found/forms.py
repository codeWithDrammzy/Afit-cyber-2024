from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils import timezone

class StudentRegistrationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        label="AFIT Email",
        help_text="Use your AFIT email address (name@afit.edu.ng)",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'name@afit.edu.ng'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your last name'
        })
    )
    phone_number = forms.CharField(
        max_length=11,
        required=False,
        label="Phone Number",
        help_text="11 digits only (e.g., 08012345678)",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '08012345678',
            'pattern': '\d{11}',
            'title': '11 digits only'
        })
    )
    matric_no = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        label="Matriculation Number",
        help_text="Exactly 10 characters (e.g., U25CYS2001)",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'U25CYS2001',
            'pattern': 'U\d{2}[A-Z]{3}\d{4}',
            'title': 'Format: U + Year(2 digits) + Dept Code(3 letters) + Number(4 digits)'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        empty_label="Select Department",
        label="Department",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        })
    )
    level = forms.ChoiceField(
        choices=(
            ('', 'Select Level'),
            ('100', '100 Level'),
            ('200', '200 Level'),
            ('300', '300 Level'),
            ('400', '400 Level'),
            ('500', '500 Level'),
        ),
        label="Level",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'matric_no', 'department', 'level', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update fields with proper attributes
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter username',
            'maxlength': '150'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Confirm password'
        })
        
        # Remove default help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Set initial values for placeholders
        for field in self.fields:
            if 'placeholder' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['placeholder'] = f'Enter {self.fields[field].label}'
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        
        if phone_number:
            # Remove any non-digit characters
            phone_digits = ''.join(filter(str.isdigit, phone_number))
            
            # Ensure exactly 11 digits
            if len(phone_digits) != 11:
                raise forms.ValidationError('Phone number must be exactly 11 digits.')
            
            # Ensure it starts with 0
            if not phone_digits.startswith('0'):
                raise forms.ValidationError('Phone number must start with 0.')
            
            return phone_digits
        
        return phone_number
    
    def clean_matric_no(self):
        matric_no = self.cleaned_data.get('matric_no', '').strip().upper()
        
        if not matric_no:
            raise forms.ValidationError('Matric number is required.')
        
        # Validate length exactly 10
        if len(matric_no) != 10:
            raise forms.ValidationError('Matric number must be exactly 10 characters.')
        
        # Validate format: U25CYS2001
        if not matric_no.startswith('U'):
            raise forms.ValidationError('Matric number must start with "U".')
        
        # Validate year digits
        if not matric_no[1:3].isdigit():
            raise forms.ValidationError('Characters 2-3 must be year digits (e.g., 25 for 2025).')
        
        # Validate department code (3 uppercase letters)
        department_code = matric_no[3:6]
        if not department_code.isalpha() or not department_code.isupper():
            raise forms.ValidationError('Characters 4-6 must be uppercase department code letters (e.g., CYS for Cyber Security).')
        
        # Validate serial number (4 digits)
        if not matric_no[6:].isdigit():
            raise forms.ValidationError('Characters 7-10 must be numeric.')
        
        return matric_no
    
    def clean(self):
        cleaned_data = super().clean()
        matric_no = cleaned_data.get('matric_no')
        department = cleaned_data.get('department')
        
        # Validate department code matches selected department
        if matric_no and department:
            department_code = matric_no[3:6]
            if department.code.upper() != department_code:
                raise forms.ValidationError(
                    f'Matric number department code "{department_code}" does not match selected department "{department.name}" (code: {department.code}).'
                )
        
        return cleaned_data




# forms.py
from django import forms
from .models import Item
from django.utils import timezone

class ItemReportForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'title', 
            'description', 
            'category', 
            'status',
            'location_found', 
            'location_lost', 
            'date_occurred',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_occurred': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial date to now
        self.fields['date_occurred'].initial = timezone.now()
    class Meta:
        model = Item
        fields = [
            'title', 
            'description', 
            'category', 
            'status',
            'location_found', 
            'location_lost', 
            'date_occurred',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_occurred': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial date to now
        self.fields['date_occurred'].initial = timezone.now()