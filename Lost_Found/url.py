from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Add this line
    path('register/', views.register_page, name='register'),
    path('my-login/', views.my_login, name='my_login'),
    path('logout', views.my_logout, name='logout'),

    
# ============= Student Urls =========

    path('std-board/', views.student_dashboard, name='std-board'),
    path('lost-item/', views.lost_item, name='lost-item'),
    path('found-item/', views.found_item, name='found-item'),
    path('report-item/', views.report_item, name='report-item'),
    path('my-report/', views.my_report, name='my-report'),


    
# ============= Admin Urls  =========

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]