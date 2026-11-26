
# ============================================================
# PANELMSE - height_progression.py
#
# OBJETIVO:
# Generar y validar la progresion de alturas de un muro.
#
# TIPOS DE PERFIL:
# 1. Ascendente.
# 2. Descendente.
# 3. Planicie.
#
# MODOS:
# ESTRICTO: salto maximo de un paso.
# FLEXIBLE: salto maximo de dos pasos.
#
# El ultimo paso puede ser menor al paso establecido.
#
# Las alturas se manejan en milimetros.
# ============================================================

from decimal import Decimal, InvalidOperation


# ============================================================
# CONVERTIR METROS A MILIMETROS
# ============================================================

def convertir_altura_mm(valor, nombre):

    try:
        medida_m = Decimal(
            str(valor).strip().replace(",", ".")
        )

    except (InvalidOperation, ValueError):
        raise ValueError(
            f"La {nombre} debe ser un numero valido."
        )

    if not medida_m.is_finite() or medida_m <= 0:
        raise ValueError(
            f"La {nombre} debe ser mayor que cero."
        )

    medida_mm = medida_m * Decimal("1000")

    if medida_mm != medida_mm.to_integral_value():

        raise ValueError(
            f"La {nombre} debe tener precision maxima "
            "de un milimetro."
        )

    return int(medida_mm)


# ============================================================
# GENERAR NIVELES DE ALTURA PERMITIDOS
# ============================================================

def generar_niveles_altura(
    altura_inicial_m,
    altura_final_m,
    paso_altura_m=0.05
):

    altura_inicial = convertir_altura_mm(
        altura_inicial_m,
        "altura inicial"
    )

    altura_final = convertir_altura_mm(
        altura_final_m,
        "altura final"
    )

    paso_altura = convertir_altura_mm(
        paso_altura_m,
        "paso de altura"
    )

    niveles = [altura_inicial]

    # --------------------------------------------------------
    # MURO ASCENDENTE
    # --------------------------------------------------------

    if altura_final > altura_inicial:

        altura_actual = altura_inicial

        while altura_final - altura_actual > paso_altura:

            altura_actual += paso_altura

            niveles.append(altura_actual)

        # Agregar el nivel final, incluso si el ultimo
        # incremento es menor que el paso establecido.
        if altura_actual != altura_final:

            niveles.append(altura_final)

    # --------------------------------------------------------
    # MURO DESCENDENTE
    # --------------------------------------------------------

    elif altura_final < altura_inicial:

        altura_actual = altura_inicial

        while altura_actual - altura_final > paso_altura:

            altura_actual -= paso_altura

            niveles.append(altura_actual)

        # Agregar el nivel final, incluso si el ultimo
        # decremento es menor que el paso establecido.
        if altura_actual != altura_final:

            niveles.append(altura_final)

    # --------------------------------------------------------
    # PLANICIE
    # --------------------------------------------------------

    # Si ambas alturas son iguales, el unico nivel
    # permitido es la altura inicial.

    return niveles


# ============================================================
# VALIDAR UNA SECUENCIA DE ALTURAS
# ============================================================

def validar_secuencia_alturas(
    alturas_mm,
    altura_inicial_m,
    altura_final_m,
    paso_altura_m=0.05,
    modo_flexible=False
):

    niveles = generar_niveles_altura(
        altura_inicial_m,
        altura_final_m,
        paso_altura_m
    )

    altura_inicial = convertir_altura_mm(
        altura_inicial_m,
        "altura inicial"
    )

    altura_final = convertir_altura_mm(
        altura_final_m,
        "altura final"
    )

    paso_altura = convertir_altura_mm(
        paso_altura_m,
        "paso de altura"
    )

    errores = []
    alturas_validadas = []

    # Determinar la direccion del muro.
    if altura_final > altura_inicial:
        direccion = 1

    elif altura_final < altura_inicial:
        direccion = -1

    else:
        direccion = 0

    # Determinar el salto maximo permitido.
    multiplicador = 2 if modo_flexible else 1

    salto_maximo = paso_altura * multiplicador

    # --------------------------------------------------------
    # COMPROBAR QUE EXISTAN ALTURAS
    # --------------------------------------------------------

    if not alturas_mm:

        return {
            "valida": False,
            "errores": [
                "No hay alturas para comprobar."
            ],
            "niveles_permitidos_mm": niveles,
            "ultima_altura_mm": None,
            "alcanza_altura_final": False,
            "advertencia": (
                "No hay paneles asignados para comprobar "
                "la progresion."
            )
        }

    # --------------------------------------------------------
    # VALIDAR CADA ALTURA
    # --------------------------------------------------------

    for indice, altura in enumerate(alturas_mm):

        try:

            valor = Decimal(str(altura).strip())

            if (
                not valor.is_finite()
                or valor != valor.to_integral_value()
            ):
                raise ValueError

            altura = int(valor)

        except (InvalidOperation, ValueError, TypeError):

            errores.append(
                f"La altura de la posicion {indice + 1} "
                "no es un numero entero en milimetros."
            )

            alturas_validadas.append(None)

            continue

        alturas_validadas.append(altura)

        # Comprobar que pertenezca a los niveles permitidos.
        if altura not in niveles:

            errores.append(
                f"La altura de la posicion {indice + 1} "
                f"({altura} mm) no cumple el paso de altura."
            )

        # La primera posicion debe comenzar con
        # la altura inicial.
        if indice == 0 and altura != altura_inicial:

            errores.append(
                "La primera posicion debe comenzar "
                "con la altura inicial."
            )

    # --------------------------------------------------------
    # VALIDAR LA DIRECCION DE LA PROGRESION
    # --------------------------------------------------------

    for indice in range(1, len(alturas_validadas)):

        altura_anterior = alturas_validadas[indice - 1]
        altura_actual = alturas_validadas[indice]

        # Evitar comparaciones cuando existe un dato invalido.
        if altura_anterior is None or altura_actual is None:
            continue

        diferencia = altura_actual - altura_anterior

        # ----------------------------------------------------
        # MURO ASCENDENTE
        # ----------------------------------------------------

        if direccion == 1:

            if diferencia < 0:

                errores.append(
                    f"La altura disminuye entre las posiciones "
                    f"{indice} y {indice + 1}, pero el muro "
                    "debe ser ascendente."
                )

            elif diferencia > salto_maximo:

                errores.append(
                    f"El incremento entre las posiciones "
                    f"{indice} y {indice + 1} supera el "
                    f"maximo permitido de {salto_maximo} mm."
                )

        # ----------------------------------------------------
        # MURO DESCENDENTE
        # ----------------------------------------------------

        elif direccion == -1:

            if diferencia > 0:

                errores.append(
                    f"La altura aumenta entre las posiciones "
                    f"{indice} y {indice + 1}, pero el muro "
                    "debe ser descendente."
                )

            elif abs(diferencia) > salto_maximo:

                errores.append(
                    f"El decremento entre las posiciones "
                    f"{indice} y {indice + 1} supera el "
                    f"maximo permitido de {salto_maximo} mm."
                )

        # ----------------------------------------------------
        # PLANICIE
        # ----------------------------------------------------

        else:

            if diferencia != 0:

                errores.append(
                    "Todas las posiciones deben mantener "
                    "la misma altura porque el muro "
                    "es una planicie."
                )

    # --------------------------------------------------------
    # COMPROBAR SI SE ALCANZO LA ALTURA FINAL
    # --------------------------------------------------------

    ultima_altura = (
        alturas_validadas[-1]
        if alturas_validadas
        else None
    )

    alcanza_altura_final = (
        ultima_altura is not None
        and ultima_altura == altura_final
    )

    advertencia = None

    if ultima_altura is not None and not alcanza_altura_final:

        advertencia = (
            "La progresion de alturas es incompleta. "
            "No se alcanza la altura final establecida. "
            "Debe revisarse la disponibilidad del inventario."
        )

    elif ultima_altura is None:

        advertencia = (
            "No fue posible determinar la ultima altura."
        )

    return {
        "valida": len(errores) == 0,
        "errores": errores,
        "niveles_permitidos_mm": niveles,
        "ultima_altura_mm": ultima_altura,
        "alcanza_altura_final": alcanza_altura_final,
        "advertencia": advertencia
    }
