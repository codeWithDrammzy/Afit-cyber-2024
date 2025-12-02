from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    
    # Simple 11-digit phone number without country code
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        help_text="11-digit Nigerian phone number (e.g., 08012345678)"
    )
    
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def clean(self):
        """Clean and validate phone number"""
        super().clean()
        
        if self.phone_number:
            # Remove any non-digit characters
            phone_digits = ''.join(filter(str.isdigit, self.phone_number))
            
            # Validate exactly 11 digits
            if len(phone_digits) != 11:
                raise ValidationError({
                    'phone_number': 'Phone number must be exactly 11 digits.'
                })
            
            # Validate starts with 0
            if not phone_digits.startswith('0'):
                raise ValidationError({
                    'phone_number': 'Phone number must start with 0.'
                })
            
            # Update with cleaned value
            self.phone_number = phone_digits

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    matric_no = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
        ],
        help_text="Matric number must be exactly 10 characters (e.g., U25CYS2001)"
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.CharField(max_length=50, choices=(
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
    ))
    
    class Meta:
        ordering = ['department__name', 'level']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.matric_no}"
    
    def clean(self):
        """Validate matric number format based on department"""
        super().clean()
        
        if not self.matric_no or len(self.matric_no) != 10:
            raise ValidationError({
                'matric_no': 'Matric number must be exactly 10 characters.'
            })
        
        # Convert to uppercase for consistency
        self.matric_no = self.matric_no.upper()
        
        # Validate matric number format: U25CYS2001
        # Format: U + Year (2 digits) + Department Code (3 letters) + Number (4 digits)
        if not self.matric_no.startswith('U'):
            raise ValidationError({
                'matric_no': 'Matric number must start with "U".'
            })
        
        if not self.matric_no[1:3].isdigit():
            raise ValidationError({
                'matric_no': 'Characters 2-3 must be year digits.'
            })
        
        department_code = self.matric_no[3:6]
        if not department_code.isalpha() or not department_code.isupper():
            raise ValidationError({
                'matric_no': 'Characters 4-6 must be uppercase department code letters.'
            })
        
        if not self.matric_no[6:].isdigit():
            raise ValidationError({
                'matric_no': 'Characters 7-10 must be numeric.'
            })
        
        # Validate department code matches selected department
        if self.department and department_code != self.department.code:
            raise ValidationError({
                'matric_no': f'Matric number department code "{department_code}" does not match selected department "{self.department.name}" (code: {self.department.code}).'
            })

class Item(models.Model):
    STATUS_CHOICES = (
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    )
    
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('documents', 'Documents'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('books', 'Books'),
        ('others', 'Others'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    location_found = models.CharField(max_length=200, blank=True)
    location_lost = models.CharField(max_length=200, blank=True)
    date_reported = models.DateTimeField(auto_now_add=True)
    date_occurred = models.DateTimeField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    
    # If item is found and claimed
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_items')
    date_claimed = models.DateTimeField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_items')
    
    class Meta:
        ordering = ['-date_reported']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"