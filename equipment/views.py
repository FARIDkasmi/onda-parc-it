import csv
import qrcode
import io
import base64
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Equipment

def equipment_list(request):
    """Affiche la liste complète des équipements."""
    equipments = Equipment.objects.all()
    
    # Statistiques pour le tableau de bord
    total_count = equipments.count()
    in_service_count = equipments.filter(statut='IN_SERVICE').count() if hasattr(Equipment, 'statut') else 0
    maintenance_count = equipments.filter(statut='MAINTENANCE').count() if hasattr(Equipment, 'statut') else 0
    out_service_count = equipments.filter(statut='HORS_SERVICE').count() if hasattr(Equipment, 'statut') else 0

    return render(request, 'equipment/equipment_list.html', {
        'equipments': equipments,
        'total_count': total_count,
        'in_service_count': in_service_count,
        'maintenance_count': maintenance_count,
        'out_service_count': out_service_count,
    })

def export_equipment_csv(request):
    """Exporte la liste des équipements au format CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inventaire_onda.csv"'
    
    response.write('\ufeff')  # BOM UTF-8 pour Excel
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Code Inventaire', 'Désignation', 'Catégorie', 'Emplacement', 'Statut'])

    for item in Equipment.objects.all():
        code = getattr(item, 'code_inventaire', f'ONDA-{item.pk:03d}')
        nom = getattr(item, 'designation', getattr(item, 'nom', 'Équipement'))
        cat = getattr(item, 'categorie', 'Général')
        emp = getattr(item, 'emplacement', 'N/A')
        statut = getattr(item, 'statut', 'En service')
        
        writer.writerow([item.pk, code, nom, cat, emp, statut])

    return response

def security_dashboard(request):
    """Affiche le tableau de bord de sécurité IP."""
    return render(request, 'equipment/security_dashboard.html')

def detail_equipment(request, pk):
    """Affiche la fiche d'un équipement avec QR Code dynamique."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    scan_path = reverse('scan_equipment', kwargs={'pk': equipment.pk})
    scan_url = request.build_absolute_uri(scan_path)

    qr = qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#003366", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'equipment/equipment_detail.html', {
        'equipment': equipment,
        'scan_url': scan_url,
        'qr_code_base64': qr_base64,
    })

def scan_equipment(request, pk):
    """Page de scan mobile protégée par code PIN."""
    equipment = get_object_or_404(Equipment, pk=pk)

    if not request.session.get('pin_authenticated'):
        error_message = None
        if request.method == 'POST':
            entered_pin = request.POST.get('pin', '').strip()
            if entered_pin == '1234':
                request.session['pin_authenticated'] = True
                return redirect('scan_equipment', pk=pk)
            else:
                error_message = "Code PIN incorrect. Accès refusé."

        return render(request, 'equipment/pin_lock.html', {
            'equipment': equipment,
            'error': error_message
        })

    return render(request, 'equipment/equipment_scan_detail.html', {'equipment': equipment})

def lock_session(request):
    """Réinitialise la session PIN."""
    request.session.pop('pin_authenticated', None)
    return redirect('equipment_list')