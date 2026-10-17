import qrcode
import io
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Equipment

def detail_equipment(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # Génération dynamique de l'URL pour le QR code
    scan_path = reverse('scan_equipment', kwargs={'code': equipment.code})
    scan_url = request.build_absolute_uri(scan_path)

    qr = qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#003366", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'equipment_detail.html', {
        'equipment': equipment,
        'scan_url': scan_url,
        'qr_code_base64': qr_base64,
    })

def scan_equipment(request, code):
    equipment = get_object_or_404(Equipment, code=code)

    if request.session.get('pin_authenticated') != True:
        error_message = None
        if request.method == 'POST':
            entered_pin = request.POST.get('pin', '').strip()
            if entered_pin == '1234':
                request.session['pin_authenticated'] = True
                return redirect('scan_equipment', code=code)
            else:
                error_message = "Code PIN incorrect. Accès refusé."

        return render(request, 'pin_lock.html', {
            'equipment': equipment,
            'error': error_message
        })

    return render(request, 'scan_detail.html', {'equipment': equipment})

def lock_session(request):
    if 'pin_authenticated' in request.session:
        del request.session['pin_authenticated']
    return redirect('admin:index')