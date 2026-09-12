"""Fechas en la hora de la floristeria, no en la del servidor.

El servidor de Vercel corre en UTC, cinco horas por delante de Colombia. Sin
esto, todo lo que pasara despues de las 7 de la tarde contaba como del dia
siguiente: las ventas de la noche desaparecian de "Ventas de hoy" y el
calendario del checkout dejaba de ofrecer el dia en curso.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app

ZONA_POR_DEFECTO = "America/Bogota"


def zona():
    nombre = current_app.config.get("TIMEZONE", ZONA_POR_DEFECTO) if current_app else ZONA_POR_DEFECTO
    try:
        return ZoneInfo(nombre)
    except Exception:  # noqa: BLE001 - zona mal escrita o sin base de datos de zonas
        return ZoneInfo(ZONA_POR_DEFECTO)


def ahora():
    """Momento actual en la hora local de la tienda."""
    return datetime.now(zona())


def hoy():
    """Fecha de hoy segun la hora local de la tienda."""
    return ahora().date()


def inicio_del_dia(fecha=None):
    """Medianoche local, expresada en UTC para comparar contra la base de datos.

    Las fechas se guardan en UTC, asi que el corte del dia local hay que
    traducirlo antes de filtrar.
    """
    fecha = fecha or hoy()
    local = datetime(fecha.year, fecha.month, fecha.day, tzinfo=zona())
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def inicio_del_mes():
    """Medianoche local del primer dia del mes, en UTC."""
    h = hoy()
    return inicio_del_dia(h.replace(day=1))
