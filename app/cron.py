# coding=utf-8
import random
from django.db.models import Sum
from django.utils.datetime_safe import datetime, time
from models import Rifa, Sorteo, SorteoHora, Venta, VentaDetalle, RifaLista, EstadoSistema, CronTabLog


def crear_sorteos():
    d = datetime.now()
    # print('Process run create sorteos %s ' % d)
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
    '''
    d = datetime.now()
    test = TestCronTab()
    test.hora = time(d.hour, d.minute, d.second)
    test.save()
    '''


def findSorteo(item, list):
    found = False
    for s in list:
        if s.sorteoHoras.hora_sorteo == item.hora_sorteo:
            found = True
    return found


def set_number_sorteo():
    d = datetime.now()
    print('sorteo en proceso %s ' % d)
    if 7 < d.hour < 23:
        try:
            if d.minute >= 55:
                hora = time(d.hour + 1, 0, 0)
            else:
                hora = time(d.hour, d.minute + 5, 0)

            # CronTabLog.objects.create(hora=d.time(), descripcion=hora)
            # init = time(7, 0, 0)
            # end = time(d.hour, d.minute, d.second)
            # n = 0
            sorteo = Sorteo.objects.get(fecha_sorteo=d.date(), sorteoHoras__hora_sorteo=hora)
            ventas = Venta.objects.filter(fecha=d.date(), estado='EN JUEGO')
            estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
            estado_sistema.estado = False
            estado_sistema.save()
            if sorteo.numero_ganador == 0:
                if len(ventas) != 0:
                    first_day = datetime.now().replace(day=1)
                    now = datetime.now()
                    total_venta_value = 0
                    total_ganancia_value = 0
                    total_venta = Venta.objects.filter(fecha__gte=first_day, fecha__lte=now)

                    for v in total_venta:
                        total_venta_value += v.total_apostado
                        if v.estado == 'GANADO' or v.estado == 'PAGADO':
                            total_ganancia_value += v.total_ganancia

                    # apuesta_unica = False
                    total_ganancia = total_venta_value - total_ganancia_value
                    porcentaje_ganancias = float(total_ganancia_value) / float(total_venta_value)
                    detalles = lista_ventas(ventas, sorteo)
                    list_elements = lista_items(detalles)
                    dict_valores = get_values_bet(list_elements)
                    direct_values = get_direct_bets(list_elements)
                    direct_values_no_bet = get_direct_no_bet(list_elements)
                    list_directs = get_directs_list(list_elements)
                    min_val_tuple = min_val(dict_valores)
                    n = get_number_winner(min_val_tuple, direct_values, list_directs, direct_values_no_bet,
                                          total_ganancia, porcentaje_ganancias)
                    CronTabLog.objects.create(hora=d.time(), descripcion='numero ganador con items en venta %s' % n)
                else:
                    n = random.randint(1, 36)
                    # print(n)
                    CronTabLog.objects.create(hora=d.time(), descripcion='numero ganador sin items en venta %s' % n)
                sorteo.numero_ganador = n
                sorteo.save()
                jugadas_ganadoras(ventas, sorteo)
                tikets_ganadores(ventas, sorteo)

                # new code
                estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
                if estado_sistema.estado is not True:
                    estado_sistema.estado = True
                    estado_sistema.save()
                    # new code
            else:
                # CronTabLog.objects.create(hora=d.time(), descripcion='este sorteo ya se jugó')
                # print('este sorteo ya se jugó')
                # new code
                estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
                if estado_sistema.estado is not True:
                    estado_sistema.estado = True
                    estado_sistema.save()
                    # new code
        except Exception as e:
            print (e.message)
            CronTabLog.objects.create(hora=d.time(), descripcion=e.message)
            estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
            if estado_sistema.estado is not True:
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
    # print('\n lista_items %s ' % list)
    return list


def get_values_bet(elements):
    valores = []
    # for i = 0
    for i in range(0, 8):
        sum_val = 0
        numero = ''
        for element in elements:
            if element.tipo_apuesta == i:
                sum_val = sum_val + element.valor_apuesta
                numero = element.numeros
        if sum_val > 0:
            data = {
                'tipo': i,
                'numero': numero,
                'total_apostado': sum_val
            }
            valores.append(data)
    print ('\n get_values_bet %s' % valores)
    '''
        sum_val = 0
        for element in list_elements:
            if item.id == element.detalle_rifa.id:
                sum_val = sum_val + element.valor_apuesta
        valores.append((int(item.id), int(sum_val)))
    '''
    return valores


def get_direct_bets(elements):
    valores = []
    # for i = 0
    for i in range(0, 37):
        sum_val = 0
        numero = ''
        for element in elements:
            if element.tipo_apuesta == 0:
                if i == int(element.numeros):
                    sum_val = sum_val + element.valor_apuesta
                    numero = element.numeros
        if sum_val > 0:
            data = {
                'numero': numero,
                'total_apostado': sum_val
            }
            valores.append(data)
    # print('\n get_direct_bets %s' % valores)
    return valores


def get_direct_no_bet(elements):
    valores = []
    # for i = 0
    for i in range(0, 37):
        sum_val = 0
        for element in elements:
            if element.tipo_apuesta == 0:
                if i == int(element.numeros):
                    sum_val = sum_val + element.valor_apuesta
        if sum_val == 0:
            valores.append(i)
    return valores


def get_directs_list(elements):
    valores = []
    # for i = 0
    for i in range(0, 37):
        sum_val = 0
        numero = ''
        for element in elements:
            if element.tipo_apuesta == 0:
                if i == int(element.numeros):
                    sum_val = sum_val + element.valor_apuesta
                    numero = element.numeros
        if sum_val > 0:
            valores.append(int(numero))
    print('\n get_directs_list %s' % valores)
    return valores


def get_number_winner(betMin, directs, list_directs, list_direct_no_bet, total_ganancia, porcentaje_ganancia):
    # print ('\n getNumberWinner %s' % betMin)
    winner = 0
    if betMin.get('tipo') == 0:
        # min_val = 0
        min_val_tuple = directs[0]
        for val in directs:
            if val.get('total_apostado') != 0:
                if val.get('total_apostado') < min_val_tuple.get('total_apostado'):
                    min_val_tuple = val

        excedente = total_ganancia / (betMin.get('total_apostado') * 34)

        if total_ganancia < 0:
            if len(list_direct_no_bet) > 0:
                length = len(list_direct_no_bet) - 1
                pos = random.randint(0, length)
                winner = list_direct_no_bet[pos]
        elif excedente >= 2 and total_ganancia > 0:
            winner = int(min_val_tuple.get('numero'))
        else:
            if len(list_direct_no_bet) > 0:
                length = len(list_direct_no_bet) - 1
                pos = random.randint(0, length)
                winner = list_direct_no_bet[pos]
            else:
                winner = int(min_val_tuple.get('numero'))

        '''
        if total_ganancia <= 0:
            if len(list_direct_no_bet) > 0:
                length = len(list_direct_no_bet) - 1
                pos = random.randint(0, length)
                winner = list_direct_no_bet[pos]
        else:
            if ganancia * 34 > total_ganancia:
                if len(list_direct_no_bet) > 0:
                    length = len(list_direct_no_bet) - 1
                    pos = random.randint(0, length)
                    winner = list_direct_no_bet[pos]
                else:
                    winner = int(min_val_tuple.get('numero'))
            else:
                winner = int(min_val_tuple.get('numero'))
        '''

    elif betMin.get('tipo') == 1:
        list_pair = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
        other = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
        list_result_pair = (set(list_pair) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 2)

        if excedente > 4 and total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_pair)
            elif len(list_result_pair) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(other)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]

        '''
        if excedente > 1.5:
            if len(list_directs) == 0:
                winner = random.choice(list_pair)
            elif len(list_result_pair) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_pair)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(list_odd) - 1
            pos = random.randint(0, length)
            winner = list_odd[pos]
        '''

    elif betMin.get('tipo') == 2:
        list_pair = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
        list_odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
        list_result_odd = (set(list_odd) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 2)

        if total_ganancia < 0:
            winner = 0
        elif excedente > 3 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_odd)
            elif len(list_result_odd) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_odd)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(list_pair) - 1
            pos = random.randint(0, length)
            winner = list_pair[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 2 >= total_ganancia:
            length = len(list_pair) - 1
            pos = random.randint(0, length)
            winner = list_pair[pos]
        else:
            if len(list_directs) > 0:
                if len(list_result_odd) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_odd)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_odd)
        '''

    elif betMin.get('tipo') == 3:
        list_p_middle = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        list_s_middle = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        list_result_p_middle = (set(list_p_middle) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 2)

        if excedente > 3 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_p_middle)
            elif len(list_result_p_middle) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_p_middle)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(list_s_middle) - 1
            pos = random.randint(0, length)
            winner = list_s_middle[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 2 >= total_ganancia:
            length = len(list_s_middle) - 1
            pos = random.randint(0, length)
            winner = list_s_middle[pos]
        else:
            if len(list_directs) > 0:
                if len(list_result_p_middle) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_p_middle)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_p_middle)
        '''

    elif betMin.get('tipo') == 4:
        list_p_middle = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        list_s_middle = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        list_result_s_middle = (set(list_s_middle) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 2)

        if excedente > 4 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_p_middle)
            elif len(list_result_s_middle) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_s_middle)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(list_p_middle) - 1
            pos = random.randint(0, length)
            winner = list_p_middle[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 2 >= total_ganancia:
            length = len(list_p_middle) - 1
            pos = random.randint(0, length)
            winner = list_p_middle[pos]
        else:
            if len(list_directs) > 0:
                if len(list_result_s_middle) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_s_middle)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_s_middle)
        '''

    elif betMin.get('tipo') == 5:
        list_pd = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        other = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        list_result_pd = (set(list_pd) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 3)

        if excedente > 6 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_pd)
            elif len(list_result_pd) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_pd)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 3 >= total_ganancia:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]
        else:
            if len(list_directs) > 0:
                list_result_pd = (set(list_pd) - set(list_directs))
                if len(list_result_pd) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_pd)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_pd)
        '''

    elif betMin.get('tipo') == 6:
        list_sd = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        other = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        list_result_sd = (set(list_sd) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 3)

        if excedente > 6 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_sd)
            elif len(list_result_sd) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_sd)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 3 >= total_ganancia:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]
        else:
            if len(list_directs) > 0:
                if len(list_result_sd) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_sd)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_sd)
        '''

    elif betMin.get('tipo') == 7:
        list_td = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        other = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        list_result_td = (set(list_td) - set(list_directs))

        excedente = total_ganancia / (betMin.get('total_apostado') * 3)

        if excedente > 6 or total_ganancia > 0 and porcentaje_ganancia > 0.1:
            if len(list_directs) == 0:
                winner = random.choice(list_td)
            elif len(list_result_td) == 0:
                winner = 0
            else:
                search = True
                while search:
                    winner = random.choice(list_td)
                    search = search_in_directs(winner, list_directs)
        else:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]

        '''
        if apuesta_unica or total_ganancia <= 0 or betMin.get('total_apostado') * 3 >= total_ganancia:
            length = len(other) - 1
            pos = random.randint(0, length)
            winner = other[pos]
        else:
            if len(list_directs) > 0:
                if len(list_result_td) == 0:
                    winner = 0
                else:
                    search = True
                    while search:
                        winner = random.choice(list_td)
                        print('\n Pair %s ' % winner)
                        search = search_in_directs(winner, list_directs)
            else:
                winner = random.choice(list_td)
        '''

    return winner


def jugadas_ganadoras(venta, sorteo):
    for v in venta:
        sum_ganancia = 0
        sum_items = 0
        sum_ganadores = 0
        if v.estado == 'EN JUEGO':
            items = VentaDetalle.objects.filter(venta__id=v.id)
            if len(items) != 0:
                for dt in items:
                    if dt.sorteo == sorteo:
                        sum_items += 1
                        # if dt.detalle_rifa.posicion == sorteo.numero_ganador and dt.sorteo.id == sorteo.id:
                        if dt.sorteo.id == sorteo.id:
                            if checkType(dt.tipo_apuesta, sorteo.numero_ganador, dt.numeros):
                                dt.estado = 'GANADO'
                                sum_ganancia = sum_ganancia + dt.ganancia
                                sum_ganadores += 1
                            else:
                                dt.estado = 'PERDIDO'
                        dt.save()

                v.total_ganancia = v.total_ganancia + sum_ganancia
                v.save()
            '''
            if len(items) == sum_items:
                if sum_ganadores >= 1:
                    v.total_ganancia = sum_ganancia
                    v.save()
                else:
                    v.total_ganancia = sum_ganancia
                    v.save()
            '''


def tikets_ganadores(ventas, sorteo):
    # d = datetime.now()
    # hora = time(d.hour, d.minute + 5, 0)
    for v in ventas:
        if v.estado == 'EN JUEGO':
            # ventasDetalles = VentaDetalle.objects.filter(venta=v)
            estados_pendientes = VentaDetalle.objects.filter(venta=v, estado='EN JUEGO')
            if len(estados_pendientes) == 0:
                estados_ganados = VentaDetalle.objects.filter(venta=v, estado='GANADO')
                if len(estados_ganados) > 0:
                    v.estado = 'GANADO'
                else:
                    estados_perdidos = VentaDetalle.objects.filter(venta=v, estado='PERDIDO')
                    if len(estados_perdidos) > 0:
                        v.estado = 'PERDIDO'
                v.save()
        '''
        for item in ventasDetalles:
            if item.sorteo == sorteo and item.estado == 'GANADO':
                sum_items += 1
                sum_ganadores += 1
        if sum_items == len(ventasDetalles):
            if sum_ganadores > 0:
                v.estado = 'GANADO'
            elif sum_ganadores == 0:
                v.estado = 'PERDIDO'
            v.save()
        else:
            print('Todavia hay items en juegos %s' % v.id)
        '''


def min_val(valores):
    min_val_tuple = valores[0]
    for val in valores:
        if val.get('total_apostado') != 0:
            if val.get('total_apostado') < min_val_tuple.get('total_apostado'):
                min_val_tuple = val
    '''
    for key, value in valores.items():
        if value < min_val_tuple:
            min_val_tuple = {key, value}
    for val in valores:
    if val.get('total_apostado') != 0:
        if min_val_tuple.get('total_apostado') < val.get('total_apostado'):
            min_val_tuple = val
    min_val_tuple = ()
    valor_venta = sum_venta(valores)
    while_continue = True
    while while_continue:
        n = random.randint(0, 35)
        val = valores[n]
        if val[1] * 34 < valor_venta:
            min_val_tuple = val
            while_continue = False

    '''
    print('\n minVal %s' % min_val_tuple)
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


def checkType(type, numero, numeros_apostados):
    if type == 0:
        if numero == int(numeros_apostados):
            return True
        else:
            return False
    elif type == 1:
        if numero % 2 == 0 and numero != 0:
            return True
    elif type == 2:
        if numero % 2 != 0 and numero != 0:
            return True
    elif type == 3:
        list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        if numero in list:
            return True
    elif type == 4:
        list = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        if numero in list:
            return True
    elif type == 5:
        list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if numero in list:
            return True
    elif type == 6:
        list = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        if numero in list:
            return True
    elif type == 7:
        list = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        if numero in list:
            return True
    else:
        return False


def search_in_directs(numero, list_get):
    if numero in list_get:
        return True
    else:
        return False


def set_tikets_caducados():
    pass
