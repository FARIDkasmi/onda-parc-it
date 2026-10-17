import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Equipment

print("🔄 Régénération de tous les QR codes avec l'IP réseau de votre PC...")

equipments = Equipment.objects.all()
for eq in equipments:
    if eq.qr_code:
        eq.qr_code.delete(save=False)
        eq.qr_code = None
    eq.save()
    print(f"  [OK] QR Code régénéré pour : {eq.code_inventaire}")

print("\n✅ Tous les QR Codes ont été mis à jour !")