# coding=utf-8
from __future__ import print_function
import random
import threading

from background_task import background
from django.utils.datetime_safe import datetime, time
from models import Sorteo, Rifa, SorteoHora, Venta, VentaDetalle, RifaLista, EstadoSistema


@background(schedule=5)
def crear_sorteos():
    print('create process')
    threadProcessCrearSorteo()


@background(schedule=5)
def set_number_sorteo():
    threadProcessNumeroSorteo()


def threadProcessCrearSorteo():
    threading.Timer(60.0, threadProcessCrearSorteo).start()
    d = datetime.now()
    print('Process run create sorteos %s ' % d)
    rifas = Rifa.objects.all()
    for rifa in rifas:
        sorteos = Sorteo.objects.filter(rifa__id=rifa.id, fecha_sorteo=d.date())
        horasSorteo = SorteoHora.objects.filter(rifa__id=rifa.id)
        date = d.date()
        if len(horasSorteo) > len(sorteos):
            for sh in horasSorteo:
                if findSorteo(sh, sorteos) is False:
                    sorteoSave = Sorteo.objects.create(
                        rifa=rifa,
                        fecha_sorteo=date,
                        sorteoHoras=sh,
                        numero_ganador=0
                    )
                    sorteoSave.save()
                    print('Sorteo creado satisfatoriamente %s' % sh.hora_sorteo)
        else:
            print('ya existen sorteos')


def findSorteo(item, list):
    found = False
    for s in list:
        if s.sorteoHoras.hora_sorteo == item.hora_sorteo:
            found = True
    return found


def threadProcessNumeroSorteo():
    threading.Timer(60.0, threadProcessNumeroSorteo).start()
    d = datetime.now()
    print('Process run numero % s ' % d)
    if 8 < d.hour < 19:
        try:
            if d.time().minute >= 55:
                hora = time(d.hour + 1, 0, 0)
            else:
                hora = time(d.hour, d.minute + 5, 0)

            init = time(7, 0, 0)
            end = time(d.hour, d.minute, d.second)
            sorteo = Sorteo.objects.get(fecha_sorteo=d.date(), sorteoHoras__hora_sorteo=hora)
            ventas = Venta.objects.filter(fecha=d.date(), time__gte=init, time__lte=end)
            estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
            estado_sistema.estado = False
            estado_sistema.save()
            n = 0
            if sorteo.numero_ganador == 0:
                if len(ventas) != 0:
                    detalles = lista_ventas(ventas, sorteo)
                    list_elements = lista_items(detalles)
                    rifa_detalles = RifaLista.objects.filter(rifa__id=sorteo.rifa.id)
                    valores = []
                    for item in rifa_detalles:
                        sum_val = 0
                        for element in list_elements:
                            if item.id == element.detalle_rifa.id:
                                sum_val = sum_val + element.valor_apuesta
                        valores.append((int(item.id), int(sum_val)))

                    min_val_tuple = minVal(valores)
                    win = RifaLista.objects.get(id=min_val_tuple[0])
                    n = win.posicion
                    print('numero ganador con items en venta %s' % n)
                else:
                    n = random.randint(1, 36)
                    print('numero ganado sin items en venta %s' % n)

                sorteo.numero_ganador = n
                sorteo.save()
                jugadasGanadoras(ventas, sorteo)

            else:
                print('este sorteo ya se jugó')
        except Exception as e:
            print(e)
            estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
            estado_sistema.estado = True
            estado_sistema.save()
    else:
        print(d)


def lista_ventas(ventas, sorteo):
    list = []
    for venta in ventas:
        items = VentaDetalle.objects.filter(venta__id=venta.id, sorteo__id=sorteo.id)
        if len(items) != 0:
            list.append(items)
    return list


def lista_items(detalles):
    list = []
    for dtl in detalles:
        for dt in dtl:
            list.append(dt)
    return list


def jugadasGanadoras(venta, sorteo):
    for v in venta:
        sum_ganancia = 0
        sum_items = 0
        sum_ganadores = 0
        items = VentaDetalle.objects.filter(venta__id=v.id)
        if len(items) != 0:
            for dt in items:
                if dt.sorteo == sorteo:
                    sum_items += 1
                    if dt.detalle_rifa.posicion == sorteo.numero_ganador and dt.sorteo.id == sorteo.id:
                        dt.estado = 'GANADO'
                        sum_ganancia = sum_ganancia + (dt.valor_apuesta * 34)
                        sum_ganadores += 1
                    else:
                        dt.estado = 'PERDIDO'
                    dt.save()
            if len(items) == sum_items:
                if sum_ganadores >= 1:
                    v.estado = 'GANADO'
                    v.total_ganancia = sum_ganancia
                    v.save()
                else:
                    v.estado = 'PERDIDO'
                    v.total_ganancia = sum_ganancia
                    v.save()


def tiketsGanadores(ventas, sorteo):
    d = datetime.now()
    hora = time(d.hour, d.minute + 5, 0)
    for v in ventas:
        sum_ganadores = 0
        sum_items = 0
        ventasDetalles = VentaDetalle.objects.filter(venta=v)
        for item in ventasDetalles:
            if item.sorteo == sorteo:
                sum_items += 1
                if item.estado == 'GANADO':
                    sum_ganadores += 1

        if len(ventasDetalles) == sum_items:
            if sum_ganadores > 0:
                v.estado = 'GANADO'
            elif sum_ganadores == 0:
                v.estado = 'PERDIDO'
            v.save()
        else:
            print('Todavia hay items en juegos %s' % v.id)


def minVal(valores):
    min_val_tuple = ()
    valor_venta = sum_venta(valores)
    while_continue = True
    while while_continue:
        n = random.randint(0, 35)
        val = valores[n]
        if val[1] * 37 < valor_venta:
            min_val_tuple = val
            while_continue = False

    '''
    for val in valores:
        val_multiply = val[1]*37
        if val_multiply < valor_venta:
            min_val_tuple = val
    '''
    return min_val_tuple


def get_posiciones_apostadas(valores):
    lista_pos = []
    for val in valores:
        lista_pos.append(val[0])
    return lista_pos


def sum_venta(valores):
    sum_all = 0
    for val in valores:
        sum_all = sum_all + val[1]

    return sum_all


def checkState(venta, sorteo):
    detalle_list = VentaDetalle.objects.filter(venta__id=venta.id, sorteo__id=sorteo.id)
    count_items = 0

    for detalle in detalle_list:
        if detalle.sorteo != 0:
            count_items = count_items + 1

    if count_items == len(count_items):
        pass
        # venta.estado =
