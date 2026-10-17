from django.contrib import admin
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
