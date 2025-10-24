from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Admin de Servicios:
    - Búsqueda por nombre y descripción
    - Filtros por activo y rangos de precio
    - Acciones para activar/desactivar
    """

    list_display = ("name", "price", "duration_minutes", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)
    list_editable = ("is_active",)  # alterna rápido
    fields = ("name", "description", "price", "duration_minutes", "is_active")
    actions = ["activar_servicios", "desactivar_servicios"]

    @admin.action(description="Activar servicios seleccionados")
    def activar_servicios(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} servicio(s) activado(s).")

    @admin.action(description="Desactivar servicios seleccionados")
    def desactivar_servicios(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} servicio(s) desactivado(s).")
