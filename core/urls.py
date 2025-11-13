from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view_custom, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/new/', views.complaint_create, name='complaint_create'),
    path('complaints/<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),
    path('complaints/<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    path('complaints/bulk-delete/', views.complaint_bulk_delete, name='complaint_bulk_delete'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<str:loja_cod>/', views.store_complaints, name='store_complaints'),
    path('users/', views.user_list, name='user_list'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('settings/', views.settings_view, name='settings'),
    path('export/complaints/csv/', views.export_complaints_csv, name='export_complaints_csv'),
    path('export/complaints/xlsx/', views.export_complaints_xlsx, name='export_complaints_xlsx'),
    path('export/stores/csv/', views.export_stores_csv, name='export_stores_csv'),
    path('export/stores/xlsx/', views.export_stores_xlsx, name='export_stores_xlsx'),
    path('export/users/csv/', views.export_users_csv, name='export_users_csv'),
    path('export/users/xlsx/', views.export_users_xlsx, name='export_users_xlsx'),
]


