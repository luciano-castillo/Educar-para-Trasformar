from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Asistencia,
    Alumno,
    DictadoMateria,
    Profesor,
)


@transaction.atomic
def registrar_asistencias(
    profesor,
    dictado,
    fecha,
    registros
):

    # -----------------------------------------
    # 1. Validar profesor
    # -----------------------------------------

    if not isinstance(
        profesor,
        Profesor
    ):

        raise ValidationError(
            "El profesor indicado no es válido."
        )

    # -----------------------------------------
    # 2. Validar dictado
    # -----------------------------------------

    if not isinstance(
        dictado,
        DictadoMateria
    ):

        raise ValidationError(
            "El dictado indicado no es válido."
        )

    if dictado.profesor_id != profesor.id_profesor:

        raise ValidationError(
            "El profesor no tiene permiso "
            "para registrar asistencia "
            "en este dictado."
        )

    # -----------------------------------------
    # 3. Validar fecha
    # -----------------------------------------

    if fecha > timezone.localdate():

        raise ValidationError(
            "No se puede registrar asistencia "
            "para una fecha futura."
        )

    # -----------------------------------------
    # 4. Debe existir al menos un registro
    # -----------------------------------------

    if not registros:

        raise ValidationError(
            "Debe registrar al menos "
            "una asistencia."
        )

    # -----------------------------------------
    # 5. Validar alumnos repetidos
    # -----------------------------------------

    alumnos_usados = set()

    estados_validos = {
        valor
        for valor, etiqueta
        in Asistencia.ESTADOS
    }

    registros_validados = []

    for registro in registros:

        alumno = registro.get(
            "alumno"
        )

        estado = registro.get(
            "estado"
        )

        observaciones = registro.get(
            "observaciones",
            ""
        )

        if not isinstance(
            alumno,
            Alumno
        ):

            raise ValidationError(
                "Uno de los alumnos "
                "indicados no es válido."
            )

        if alumno.pk in alumnos_usados:

            raise ValidationError(
                "Un alumno no puede aparecer "
                "más de una vez en la misma "
                "carga de asistencia."
            )

        alumnos_usados.add(
            alumno.pk
        )

        # -------------------------------------
        # Alumno debe pertenecer al curso
        # -------------------------------------

        if (
            alumno.curso_id
            != dictado.curso_id
        ):

            raise ValidationError(
                (
                    f"El alumno "
                    f"{alumno.apellido}, "
                    f"{alumno.nombre} "
                    "no pertenece al curso "
                    "del dictado."
                )
            )

        # -------------------------------------
        # Alumno activo
        # -------------------------------------

        if not alumno.estado:

            raise ValidationError(
                (
                    f"El alumno "
                    f"{alumno.apellido}, "
                    f"{alumno.nombre} "
                    "se encuentra inactivo."
                )
            )

        # -------------------------------------
        # Estado válido
        # -------------------------------------

        if estado not in estados_validos:

            raise ValidationError(
                "Uno de los estados de "
                "asistencia no es válido."
            )

        registros_validados.append(
            {
                "alumno": alumno,
                "estado": estado,
                "observaciones": observaciones,
            }
        )

    # -----------------------------------------
    # 6. Crear o actualizar asistencias
    # -----------------------------------------

    asistencias_guardadas = []

    for registro in registros_validados:

        alumno = registro[
            "alumno"
        ]

        asistencia = (
            Asistencia.objects
            .select_for_update()
            .filter(
                alumno=alumno,
                dictado=dictado,
                fecha=fecha
            )
            .first()
        )

        if asistencia:

            asistencia.estado = (
                registro["estado"]
            )

            asistencia.observaciones = (
                registro["observaciones"]
            )

        else:

            asistencia = Asistencia(
                alumno=alumno,
                dictado=dictado,
                fecha=fecha,
                estado=registro[
                    "estado"
                ],
                observaciones=registro[
                    "observaciones"
                ],
            )

        asistencia.full_clean()

        asistencia.save()

        asistencias_guardadas.append(
            asistencia
        )

    return asistencias_guardadas