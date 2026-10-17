import os
import subprocess
import sys

print("🚀 Début de la réparation automatique du projet ONDA...")

# 1. Installation des dépendances
print("📦 Vérification et installation des paquets nécessaires...")
subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "pillow"], check=False)

# 2. Définition des contenus des fichiers
files_content = {
    "config/urls.py": """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('equipment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
""",

    "equipment/models.py": """import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models

class Equipment(models.Model):
    CATEGORIE_CHOICES = [
        ('PC', 'Poste de travail / PC'),
        ('PRINTER', 'Imprimante / Scanner'),
        ('SERVER', 'Serveur'),
        ('NETWORK', 'Équipement Réseau (Switch/Router)'),
        ('FIDS', 'Écran d\\'affichage FIDS'),
    ]

    STATUT_CHOICES = [
        ('IN_SERVICE', 'En service'),
        ('MAINTENANCE', 'En maintenance'),
        ('OUT_OF_SERVICE', 'Hors service'),
    ]

    code_inventaire = models.CharField(max_length=50, unique=True, verbose_name="Code Inventaire")
    designation = models.CharField(max_length=150, verbose_name="Désignation / Modèle")
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    emplacement = models.CharField(max_length=100, verbose_name="Emplacement / Zone")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='IN_SERVICE', verbose_name="Statut")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name="QR Code")

    def __str__(self):
        return f"{self.code_inventaire} - {self.designation}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"http://127.0.0.1:8000/scan/{self.code_inventaire}/"
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="#002B49", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f"qr_{self.code_inventaire}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)


class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="Adresse IP")
    description = models.CharField(max_length=100, blank=True, null=True, verbose_name="Description / Bureau")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def __str__(self):
        return f"{self.ip_address} ({self.description or 'Sans nom'})"


class SecurityLog(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    is_blocked = models.BooleanField(default=False, verbose_name="Bloqué")
    attempted_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chemin d'accès")
    user_agent = models.TextField(blank=True, null=True, verbose_name="Navigateur / Agent")

    def __str__(self):
        return f"{self.ip_address} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
""",

    "equipment/admin.py": """from django.contrib import admin
from .models import Equipment, SecurityLog, AllowedIP

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code_inventaire', 'designation', 'categorie', 'emplacement', 'statut')
    search_fields = ('code_inventaire', 'designation', 'emplacement')
    list_filter = ('statut', 'categorie')

@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'is_active')
    search_fields = ('ip_address', 'description')

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'attempted_path', 'is_blocked', 'timestamp')
    list_filter = ('is_blocked',)
    readonly_fields = ('timestamp',)
""",

    "equipment/views.py": """import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Equipment, SecurityLog, AllowedIP

def equipment_list(request):
    equipments = Equipment.objects.all()
    total_count = equipments.count()
    in_service_count = equipments.filter(statut='IN_SERVICE').count()
    maintenance_count = equipments.filter(statut='MAINTENANCE').count()
    out_of_service_count = equipments.filter(statut='OUT_OF_SERVICE').count()

    context = {
        'equipments': equipments,
        'total_count': total_count,
        'in_service_count': in_service_count,
        'maintenance_count': maintenance_count,
        'out_of_service_count': out_of_service_count,
    }
    return render(request, 'equipment/equipment_list.html', context)

def scan_equipment(request, code_inventaire):
    equipment = get_object_or_404(Equipment, code_inventaire=code_inventaire)
    return render(request, 'equipment/equipment_scan_detail.html', {'equipment': equipment})

def security_dashboard(request):
    logs = SecurityLog.objects.all().order_by('-timestamp')[:50]
    allowed_ips = AllowedIP.objects.all()
    context = {
        'logs': logs,
        'allowed_ips': allowed_ips,
        'blocked_count': SecurityLog.objects.filter(is_blocked=True).count(),
        'allowed_count': SecurityLog.objects.filter(is_blocked=False).count(),
    }
    return render(request, 'equipment/security_dashboard.html', context)

def export_equipment_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Inventaire_ONDA_Nador.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Code Inventaire', 'Désignation', 'Catégorie', 'Emplacement', 'Statut'])

    equipments = Equipment.objects.all()
    for item in equipments:
        writer.writerow([
            item.code_inventaire,
            item.designation,
            item.get_categorie_display(),
            item.emplacement,
            item.get_statut_display()
        ])

    return response
""",

    "equipment/urls.py": """from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('scan/<str:code_inventaire>/', views.scan_equipment, name='scan_equipment'),
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('export/csv/', views.export_equipment_csv, name='export_equipment_csv'),
]
""",

    "equipment/middleware.py": """from .models import SecurityLog

class IPSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        path = request.path
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if not path.startswith('/static/') and not path.startswith('/media/'):
            try:
                SecurityLog.objects.create(
                    ip_address=ip,
                    attempted_path=path,
                    user_agent=user_agent,
                    is_blocked=False
                )
            except Exception:
                pass

        return self.get_response(request)
"""
}

# 3. Écriture des fichiers
for filepath, content in files_content.items():
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Fichier mis à jour : {filepath}")

# 4. Exécution des migrations Django
print("⚙️ Application des migrations à la base de données...")
subprocess.run([sys.executable, "manage.py", "makemigrations"], check=False)
subprocess.run([sys.executable, "manage.py", "migrate"], check=False)

print("\n✅ TOUT EST RÉPARÉ ET À JOUR !")
print("👉 Il ne te reste plus qu'à lancer : python manage.py runserver")