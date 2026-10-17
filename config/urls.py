from django.contrib import admin
from django.urls import path
from equipment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Routes d'inventaire
    path('', views.equipment_list, name='equipment_list'),
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('export/csv/', views.export_equipment_csv, name='export_equipment_csv'),
    
    # Sécurité & Dashboard
    path('security/', views.security_dashboard, name='security_dashboard'),
    
    # Fiche Équipement & Scan QR
    path('equipment/<int:pk>/', views.detail_equipment, name='detail_equipment'),
    path('scan/<int:pk>/', views.scan_equipment, name='scan_equipment'),
    path('lock/', views.lock_session, name='lock_session'),
]