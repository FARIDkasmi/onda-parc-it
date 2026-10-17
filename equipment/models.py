import qrcode
import socket
from io import BytesIO
from django.core.files import File
from django.db import models

def get_local_ip():
    """Récupère automatiquement l'adresse IP locale de la machine (ex: 192.168.x.x)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


class Equipment(models.Model):
    CATEGORIE_CHOICES = [
        ('PC', 'Poste de travail / PC'),
        ('PRINTER', 'Imprimante / Scanner'),
        ('SERVER', 'Serveur'),
        ('NETWORK', 'Équipement Réseau (Switch/Router)'),
        ('FIDS', 'Écran d\'affichage FIDS'),
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
        # Toujours régénérer avec l'IP réseau actuelle si c'est un nouvel objet ou si le QR code est réinitialisé
        if not self.qr_code:
            server_ip = get_local_ip()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # Lien réseau utilisable par le téléphone
            qr_data = f"http://{server_ip}:8000/scan/{self.code_inventaire}/"
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