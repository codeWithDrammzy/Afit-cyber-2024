from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Student, Item

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('AFIT Information', {'fields': ('user_type', 'phone_number', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('AFIT Information', {'fields': ('user_type', 'phone_number', 'is_verified')}),
    )
    ordering = ('-date_joined',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric_no', 'user_full_name', 'department', 'level', 'email')
    list_filter = ('department', 'level')
    search_fields = ('matric_no', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('matric_no',)
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Full Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    email.admin_order_field = 'user__email'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'reported_by', 'date_reported', 'is_verified')
    list_filter = ('category', 'status', 'is_verified', 'date_reported')
    search_fields = ('title', 'description', 'reported_by__username')
    readonly_fields = ('date_reported',)
    date_hierarchy = 'date_reported'
    ordering = ('-date_reported',)
    
    fieldsets = (
        ('Item Details', {
            'fields': ('title', 'description', 'category', 'status')
        }),
        ('Location Information', {
            'fields': ('location_found', 'location_lost')
        }),
        ('Date & Time', {
            'fields': ('date_occurred', 'date_reported')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Reporting Information', {
            'fields': ('reported_by',)
        }),
        ('Claim Information', {
            'fields': ('claimed_by', 'date_claimed')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by')
        }),
    )