from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import (
    Decimal,
    InvalidOperation,
)

from .models import (
    Asistencia,
    Alumno,
    DictadoMateria,
    Profesor,
    Nota,
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


@transaction.atomic
def registrar_notas(
    profesor,
    dictado,
    periodo,
    evaluacion,
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
            "para registrar notas "
            "en este dictado."
        )

    # -----------------------------------------
    # 3. Validar período
    # -----------------------------------------

    periodo = str(
        periodo or ""
    ).strip()

    if not periodo:

        raise ValidationError(
            "Debe indicar el período."
        )

    # -----------------------------------------
    # 4. Validar evaluación
    # -----------------------------------------

    evaluacion = str(
        evaluacion or ""
    ).strip()

    if not evaluacion:

        raise ValidationError(
            "Debe indicar el nombre "
            "de la evaluación."
        )

    # -----------------------------------------
    # 5. Validar fecha
    # -----------------------------------------

    if fecha > timezone.localdate():

        raise ValidationError(
            "No se puede registrar una nota "
            "con fecha futura."
        )

    # -----------------------------------------
    # 6. Debe existir al menos un registro
    # -----------------------------------------

    if not registros:

        raise ValidationError(
            "Debe registrar al menos una nota."
        )

    alumnos_usados = set()

    registros_validados = []

    # -----------------------------------------
    # 7. Validar cada alumno y calificación
    # -----------------------------------------

    for registro in registros:

        alumno = registro.get(
            "alumno"
        )

        calificacion = registro.get(
            "calificacion"
        )

        observaciones = str(
            registro.get(
                "observaciones",
                ""
            )
            or ""
        ).strip()

        # -------------------------------------
        # Alumno válido
        # -------------------------------------

        if not isinstance(
            alumno,
            Alumno
        ):

            raise ValidationError(
                "Uno de los alumnos "
                "indicados no es válido."
            )

        # -------------------------------------
        # Alumno no repetido
        # -------------------------------------

        if alumno.pk in alumnos_usados:

            raise ValidationError(
                "Un alumno no puede aparecer "
                "más de una vez en la misma "
                "carga de notas."
            )

        alumnos_usados.add(
            alumno.pk
        )

        # -------------------------------------
        # Alumno pertenece al curso
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
        # Convertir calificación a Decimal
        # -------------------------------------

        try:

            calificacion = Decimal(
                str(calificacion)
                .replace(",", ".")
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            raise ValidationError(
                (
                    f"La calificación de "
                    f"{alumno.apellido}, "
                    f"{alumno.nombre} "
                    "no es válida."
                )
            )

        # -------------------------------------
        # Nota entre 1 y 10
        # -------------------------------------

        if (
            calificacion < Decimal("1")
            or
            calificacion > Decimal("10")
        ):

            raise ValidationError(
                (
                    f"La calificación de "
                    f"{alumno.apellido}, "
                    f"{alumno.nombre} "
                    "debe estar entre 1 y 10."
                )
            )

        registros_validados.append(
            {
                "alumno": alumno,
                "calificacion": calificacion,
                "observaciones": observaciones,
            }
        )

    # -----------------------------------------
    # 8. Crear o actualizar notas
    # -----------------------------------------

    notas_guardadas = []

    for registro in registros_validados:

        alumno = registro[
            "alumno"
        ]

        nota = (
            Nota.objects
            .select_for_update()
            .filter(
                alumno=alumno,
                dictado=dictado,
                periodo__iexact=periodo,
                evaluacion__iexact=evaluacion,
            )
            .first()
        )

        if nota:

            nota.periodo = periodo

            nota.evaluacion = evaluacion

            nota.calificacion = (
                registro[
                    "calificacion"
                ]
            )

            nota.fecha = fecha

            nota.observaciones = (
                registro[
                    "observaciones"
                ]
            )

        else:

            nota = Nota(
                alumno=alumno,
                dictado=dictado,
                periodo=periodo,
                evaluacion=evaluacion,
                calificacion=(
                    registro[
                        "calificacion"
                    ]
                ),
                fecha=fecha,
                observaciones=(
                    registro[
                        "observaciones"
                    ]
                ),
            )

        nota.full_clean()

        nota.save()

        notas_guardadas.append(
            nota
        )

    return notas_guardadas