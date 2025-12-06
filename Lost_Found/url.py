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

    path('claim-item/<int:item_id>/', views.claim_item, name='claim_item'),
    path('claim-confirm/<int:item_id>/', views.claim_confirmation, name='claim_confirmation'),
    path('mark-found/<int:item_id>/', views.mark_as_found, name='mark_found'),
    path('found-confirm/<int:item_id>/', views.found_confirmation, name='found_confirmation'),
 

    
# ============= Admin Urls  =========

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]