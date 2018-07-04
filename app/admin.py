# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from models import Grupo, Persona, Taquilla, Administrador, Rifa, RifaLista, Sorteo, Venta, VentaDetalle, EstadoSistema, \
    SorteoHora, Permisos, PermisoUsuario, CronTabLog


class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fecha', 'time', 'get_taquilla', 'serial_cobro', 'get_estado_display', 'total_apostado', 'total_ganancia',
        'fecha_pago', 'get_pagador')

    list_filter = ('id', 'serial_cobro')

    def get_taquilla(self, obj):
        return obj.taquilla.usuario.username

    get_taquilla.short_description = 'Taquilla'

    def get_pagador(self, obj):
        pagador = ' '
        if obj.usuarioPagador:
            pagador = obj.usuarioPagador.username

        return pagador

    get_pagador.short_description = 'Pagador'
    get_pagador.empty_value_display = 'Pagador Desconocido'


class VentaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_venta', 'numeros', 'tipo_apuesta', 'get_sorteo', 'valor_apuesta', 'get_estado_display')

    def get_venta(self, obj):
        return obj.venta.id

    def get_sorteo(self, obj):
        return '%s %s' % (obj.sorteo.rifa.nombre_rifa, obj.sorteo.sorteoHoras.hora_sorteo)


class RifaListaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'posicion', 'image', 'nombre_imagen', 'get_rifa')

    list_filter = ('id', 'posicion')

    def get_rifa(self, obj):
        return obj.rifa.nombre_rifa

    get_rifa.short_description = 'Rifa'


class CronTabLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'hora', 'descripcion')

    list_filter = ('id', 'hora')


admin.site.register(Persona)
admin.site.register(Taquilla)
admin.site.register(Grupo)
admin.site.register(Administrador)
admin.site.register(Rifa)
admin.site.register(RifaLista, RifaListaAdmin)
admin.site.register(Sorteo)
admin.site.register(Venta, VentaAdmin)
admin.site.register(VentaDetalle, VentaDetalleAdmin)
admin.site.register(EstadoSistema)
admin.site.register(SorteoHora)
admin.site.register(Permisos)
admin.site.register(PermisoUsuario)
admin.site.register(CronTabLog, CronTabLogAdmin)
