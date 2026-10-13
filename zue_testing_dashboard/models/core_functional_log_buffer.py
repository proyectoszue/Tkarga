# -*- coding: utf-8 -*-
# Core: buffer en memoria del log funcional por sesión.

SESSION_CTX_KEY = "zue_testing_dashboard_session_id"
TEST_PARAMS_CTX_KEY = "zue_testing_dashboard_test_params"
TRACE_SEPARATOR = "\n---TRACE---\n"

_BUFFERS = {}


def isControlledConstraintErrorValue(error):
    """Evalua si una excepcion corresponde a una restriccion SQL o validacion esperada."""
    message = str(error).lower()
    keywords = (
        "unique",
        "uniqueviolation",
        "ya existe",
        "llave duplicada",
        "duplicate",
        "constraint",
        "restriccion",
        "restricción",
        "unicidad",
        "violates",
        "duplicad",
        "verificar",
        "_uniq",
    )
    if any(keyword in message for keyword in keywords):
        return True

    from odoo.exceptions import UserError, ValidationError

    if isinstance(error, (ValidationError, UserError)):
        return any(keyword in message for keyword in keywords)

    try:
        from psycopg2 import IntegrityError
        from psycopg2.errors import UniqueViolation

        if isinstance(error, (IntegrityError, UniqueViolation)):
            return True
    except ImportError:
        pass

    current_error = error
    while current_error is not None:
        if current_error.__class__.__name__ in ("IntegrityError", "UniqueViolation"):
            return True
        if getattr(current_error, "pgcode", None) == "23505":
            return True
        current_error = getattr(current_error, "__cause__", None) or getattr(current_error, "__context__", None)
    return False


def resetFunctionalLogBuffer(session_id):
    """Limpia e inicia el buffer de pasos de la sesión."""
    if session_id is not None:
        _BUFFERS[int(session_id)] = []


def appendFunctionalLogStep(session_id, description):
    """Agrega un paso al buffer de la sesión."""
    if session_id is None:
        return
    session_key = int(session_id)
    _BUFFERS.setdefault(session_key, []).append(str(description))


def getFunctionalLogText(session_id):
    """Devuelve el log numerado listo para mostrar."""
    if session_id is None:
        return ""
    steps = _BUFFERS.get(int(session_id), [])
    return "\n".join(
        "%s. %s" % (index, step)
        for index, step in enumerate(steps, start=1)
    )


def clearFunctionalLogBuffer(session_id):
    """Elimina el buffer de la sesión."""
    if session_id is not None:
        _BUFFERS.pop(int(session_id), None)
