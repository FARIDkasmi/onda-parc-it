from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('scan/<str:code_inventaire>/', views.scan_equipment, name='scan_equipment'),
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('export/csv/', views.export_equipment_csv, name='export_equipment_csv'),
]
