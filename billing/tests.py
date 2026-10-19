from datetime import date, time
from decimal import Decimal
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils.datastructures import MultiValueDict
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import PerfilUsuario

from academic.models import (
    NivelEducativo,
    Curso,
    Alumno,
    Profesor,
    Horario,
)

from sports.models import (
    Deporte,
    GrupoDeportivo,
    InscripcionDeporte,
)

from services.models import (
    RutaTransporte,
    ContratacionTransporte,
    ServicioComedor,
    ContratacionComedor,
)

from .models import (
    CuotaMensual,
    Factura,
    Pago,
    ComprobantePago,
)

from .forms import (
    CuotaMensualForm,
    RegistrarPagoForm,
)

from .services import (
    generar_factura_alumno,
    registrar_pago,
    validar_pago,
    rechazar_pago,
    actualizar_facturas_vencidas,
)


class CuotaMensualTestCase(TestCase):

    def setUp(self):

        self.cuota_octubre = CuotaMensual.objects.create(
            mes=10,
            anio=2026,
            valor=55000,
            fecha_vencimiento=date(2026, 10, 10),
            estado=True
        )


    def test_no_permite_valor_cero(self):

        form = CuotaMensualForm(
            data={
                "mes": 11,
                "anio": 2026,
                "valor": 0,
                "fecha_vencimiento": "2026-11-10",
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "El valor de la cuota debe ser mayor a cero.",
            str(form.errors)
        )


    def test_no_permite_periodo_duplicado(self):

        form = CuotaMensualForm(
            data={
                "mes": 10,
                "anio": 2026,
                "valor": 60000,
                "fecha_vencimiento": "2026-10-15",
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "Ya existe una cuota registrada",
            str(form.non_field_errors())
        )


    def test_permite_periodo_diferente(self):

        form = CuotaMensualForm(
            data={
                "mes": 11,
                "anio": 2026,
                "valor": 60000,
                "fecha_vencimiento": "2026-11-10",
                "estado": True,
            }
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_permite_editar_misma_cuota(self):

        form = CuotaMensualForm(
            data={
                "mes": 10,
                "anio": 2026,
                "valor": 58000,
                "fecha_vencimiento": "2026-10-10",
                "estado": True,
            },
            instance=self.cuota_octubre
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_base_datos_impide_periodo_duplicado(self):

        with self.assertRaises(
            IntegrityError
        ):

            with transaction.atomic():

                CuotaMensual.objects.create(
                    mes=10,
                    anio=2026,
                    valor=70000,
                    fecha_vencimiento=date(
                        2026,
                        10,
                        20
                    ),
                    estado=True
                )

class GeneracionFacturaTestCase(TestCase):

    def setUp(self):

        # ---------------------------------------------
        # Nivel y curso
        # ---------------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Primario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="1°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # ---------------------------------------------
        # Alumno principal
        # ---------------------------------------------

        self.alumno = Alumno.objects.create(
            dni="45123456",
            legajo="ALU001",
            nombre="Lucía",
            apellido="Martínez",
            fecha_nacimiento=date(2015, 5, 10),
            domicilio="Calle 123",
            telefono="3624000000",
            correo="lucia@test.com",
            curso=self.curso,
            estado=True
        )

        # Alumno sin servicios opcionales

        self.alumno_sin_servicios = Alumno.objects.create(
            dni="45999999",
            legajo="ALU002",
            nombre="Juan",
            apellido="Pérez",
            fecha_nacimiento=date(2015, 7, 15),
            domicilio="Calle 456",
            telefono="3624111111",
            correo="juan@test.com",
            curso=self.curso,
            estado=True
        )

        # ---------------------------------------------
        # Cuota octubre 2026
        # ---------------------------------------------

        self.cuota = CuotaMensual.objects.create(
            mes=10,
            anio=2026,
            valor=55000,
            fecha_vencimiento=date(
                2026,
                10,
                10
            ),
            estado=True
        )

        # ---------------------------------------------
        # Profesor
        # ---------------------------------------------

        self.profesor = Profesor.objects.create(
            dni="30123456",
            legajo="PROF001",
            nombre="Carlos",
            apellido="Gómez",
            especialidad="Educación Física",
            correo="carlos@test.com",
            telefono="3624222222",
            estado=True
        )

        # ---------------------------------------------
        # Horarios
        # ---------------------------------------------

        self.horario_futbol = Horario.objects.create(
            dia_semana="LUNES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        self.horario_voley = Horario.objects.create(
            dia_semana="MARTES",
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0)
        )

        # ---------------------------------------------
        # Deportes
        # ---------------------------------------------

        self.futbol = Deporte.objects.create(
            nombre="Fútbol",
            descripcion="Fútbol escolar",
            valor_mensual=20000,
            estado=True
        )

        self.voley = Deporte.objects.create(
            nombre="Vóley",
            descripcion="Vóley escolar",
            valor_mensual=18000,
            estado=True
        )

        # ---------------------------------------------
        # Grupos
        # ---------------------------------------------

        self.grupo_futbol = GrupoDeportivo.objects.create(
            deporte=self.futbol,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_futbol,
            estado=True
        )

        self.grupo_voley = GrupoDeportivo.objects.create(
            deporte=self.voley,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_voley,
            estado=True
        )

        # ---------------------------------------------
        # Inscripciones deportivas
        # ---------------------------------------------

        inscripcion_futbol = (
            InscripcionDeporte.objects.create(
                alumno=self.alumno,
                grupo=self.grupo_futbol,
                estado=True
            )
        )

        inscripcion_voley = (
            InscripcionDeporte.objects.create(
                alumno=self.alumno,
                grupo=self.grupo_voley,
                estado=True
            )
        )

        # auto_now_add coloca la fecha actual.
        # La cambiamos para que el test sea siempre
        # independiente de la fecha en que se ejecute.

        InscripcionDeporte.objects.filter(
            pk=inscripcion_futbol.pk
        ).update(
            fecha_inscripcion=date(
                2026,
                10,
                1
            )
        )

        InscripcionDeporte.objects.filter(
            pk=inscripcion_voley.pk
        ).update(
            fecha_inscripcion=date(
                2026,
                10,
                1
            )
        )

        # ---------------------------------------------
        # Transporte
        # ---------------------------------------------

        self.ruta = RutaTransporte.objects.create(
            nombre="Zona Centro",
            descripcion="Recorrido zona centro",
            valor_mensual=30000,
            estado=True
        )

        ContratacionTransporte.objects.create(
            alumno=self.alumno,
            ruta=self.ruta,
            mes=10,
            anio=2026,
            estado=True
        )

        # ---------------------------------------------
        # Comedor
        # ---------------------------------------------

        self.comedor = ServicioComedor.objects.create(
            nombre="Comedor Escolar",
            descripcion="Servicio mensual",
            valor_mensual=25000,
            estado=True
        )

        ContratacionComedor.objects.create(
            alumno=self.alumno,
            servicio=self.comedor,
            mes=10,
            anio=2026,
            estado=True
        )


    def test_genera_factura_con_todos_los_conceptos(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        self.assertEqual(
            factura.detalles.count(),
            5
        )

        tipos = list(
            factura.detalles.values_list(
                "tipo_concepto",
                flat=True
            )
        )

        self.assertEqual(
            tipos.count("CUOTA"),
            1
        )

        self.assertEqual(
            tipos.count("DEPORTE"),
            2
        )

        self.assertEqual(
            tipos.count("TRANSPORTE"),
            1
        )

        self.assertEqual(
            tipos.count("COMEDOR"),
            1
        )

        self.assertEqual(
            factura.total,
            148000
        )


    def test_alumno_sin_servicios_genera_solo_cuota(self):

        factura = generar_factura_alumno(
            alumno=self.alumno_sin_servicios,
            mes=10,
            anio=2026
        )

        self.assertEqual(
            factura.detalles.count(),
            1
        )

        detalle = factura.detalles.first()

        self.assertEqual(
            detalle.tipo_concepto,
            "CUOTA"
        )

        self.assertEqual(
            factura.total,
            55000
        )


    def test_no_permite_factura_duplicada(self):

        generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        with self.assertRaises(
            ValidationError
        ):

            generar_factura_alumno(
                alumno=self.alumno,
                mes=10,
                anio=2026
            )

        self.assertEqual(
            Factura.objects.filter(
                alumno=self.alumno,
                mes=10,
                anio=2026
            ).count(),
            1
        )


    def test_factura_conserva_precios_historicos(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        total_original = factura.total

        # Cambiamos todos los valores originales

        self.cuota.valor = 99999
        self.cuota.save()

        self.futbol.valor_mensual = 99999
        self.futbol.save()

        self.voley.valor_mensual = 99999
        self.voley.save()

        self.ruta.valor_mensual = 99999
        self.ruta.save()

        self.comedor.valor_mensual = 99999
        self.comedor.save()

        factura.refresh_from_db()

        self.assertEqual(
            factura.total,
            total_original
        )

        self.assertEqual(
            factura.total,
            148000
        )


    def test_error_revierte_factura_completa(self):

        # Eliminamos la contratación válida
        # de transporte.

        ContratacionTransporte.objects.filter(
            alumno=self.alumno,
            mes=10,
            anio=2026
        ).delete()

        # Creamos una ruta con precio inválido.
        # Lo hacemos directamente desde el modelo
        # para simular un dato incorrecto en la BD.

        ruta_invalida = RutaTransporte.objects.create(
            nombre="Ruta inválida",
            descripcion="Prueba rollback",
            valor_mensual=0,
            estado=True
        )

        ContratacionTransporte.objects.create(
            alumno=self.alumno,
            ruta=ruta_invalida,
            mes=10,
            anio=2026,
            estado=True
        )

        with self.assertRaises(
            ValidationError
        ):

            generar_factura_alumno(
                alumno=self.alumno,
                mes=10,
                anio=2026
            )

        # Gracias a @transaction.atomic,
        # la factura creada parcialmente
        # también debe desaparecer.

        self.assertFalse(
            Factura.objects.filter(
                alumno=self.alumno,
                mes=10,
                anio=2026
            ).exists()
        )
    
    def test_pago_pendiente_no_reduce_deuda(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        pago = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-001"
        )

        factura.refresh_from_db()

        self.assertEqual(
            pago.estado,
            "PENDIENTE"
        )

        self.assertEqual(
            pago.monto,
            Decimal("55000.00")
        )

        self.assertEqual(
            pago.detalles_pago.count(),
            1
        )

        self.assertEqual(
            factura.total_pagado,
            Decimal("0.00")
        )

        self.assertEqual(
            factura.saldo,
            Decimal("148000.00")
        )

        self.assertEqual(
            factura.estado,
            "PENDIENTE"
        )


    def test_validar_pago_parcial_actualiza_factura(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        pago = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-002"
        )

        validar_pago(
            pago
        )

        pago.refresh_from_db()
        factura.refresh_from_db()

        self.assertEqual(
            pago.estado,
            "VALIDADO"
        )

        self.assertEqual(
            factura.total_pagado,
            Decimal("55000.00")
        )

        self.assertEqual(
            factura.saldo,
            Decimal("93000.00")
        )

        self.assertEqual(
            factura.estado,
            "PARCIAL"
        )


    def test_varios_pagos_completan_factura(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        pago1 = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-003-A"
        )

        validar_pago(
            pago1
        )

        otros_detalles = list(
            factura.detalles.exclude(
                pk=cuota.pk
            )
        )

        pago2 = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                16
            ),
            aplicaciones=[
                (
                    detalle,
                    detalle.importe
                )
                for detalle in otros_detalles
            ],
            numero_operacion="TEST-003-B"
        )

        validar_pago(
            pago2
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.pagos.filter(
                estado="VALIDADO"
            ).count(),
            2
        )

        self.assertEqual(
            factura.total_pagado,
            Decimal("148000.00")
        )

        self.assertEqual(
            factura.saldo,
            Decimal("0.00")
        )

        self.assertEqual(
            factura.estado,
            "PAGADA"
        )


    def test_pago_pendiente_reserva_el_concepto(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-004-A"
        )

        with self.assertRaises(
            ValidationError
        ):

            registrar_pago(
                factura=factura,
                fecha_transferencia=date(
                    2026,
                    10,
                    16
                ),
                aplicaciones=[
                    (
                        cuota,
                        cuota.importe
                    )
                ],
                numero_operacion="TEST-004-B"
            )

        self.assertEqual(
            Pago.objects.filter(
                factura=factura
            ).count(),
            1
        )


    def test_rechazar_pago_libera_concepto(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        pago1 = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-005-A"
        )

        rechazar_pago(
            pago1
        )

        pago1.refresh_from_db()
        factura.refresh_from_db()

        self.assertEqual(
            pago1.estado,
            "RECHAZADO"
        )

        self.assertEqual(
            factura.total_pagado,
            Decimal("0.00")
        )

        self.assertEqual(
            factura.estado,
            "PENDIENTE"
        )

        # El concepto debe volver a quedar
        # disponible para otra transferencia.

        pago2 = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                16
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="TEST-005-B"
        )

        self.assertEqual(
            pago2.estado,
            "PENDIENTE"
        )

        self.assertEqual(
            pago2.monto,
            Decimal("55000.00")
        )


    def test_no_permite_concepto_de_otra_factura(self):

        factura1 = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        factura2 = generar_factura_alumno(
            alumno=self.alumno_sin_servicios,
            mes=10,
            anio=2026
        )

        detalle_otra_factura = (
            factura2.detalles.first()
        )

        with self.assertRaises(
            ValidationError
        ):

            registrar_pago(
                factura=factura1,
                fecha_transferencia=date(
                    2026,
                    10,
                    15
                ),
                aplicaciones=[
                    (
                        detalle_otra_factura,
                        detalle_otra_factura.importe
                    )
                ],
                numero_operacion="TEST-006"
            )

        self.assertFalse(
            Pago.objects.filter(
                factura=factura1
            ).exists()
        )
    
    def test_pago_permite_varios_comprobantes(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        comprobante_pdf = SimpleUploadedFile(
            "transferencia.pdf",
            b"%PDF-1.4 comprobante de prueba",
            content_type="application/pdf"
        )

        comprobante_jpg = SimpleUploadedFile(
            "transferencia.jpg",
            b"imagen de prueba",
            content_type="image/jpeg"
        )

        with tempfile.TemporaryDirectory() as media_root:

            with override_settings(
                MEDIA_ROOT=media_root
            ):

                pago = registrar_pago(
                    factura=factura,
                    fecha_transferencia=date(
                        2026,
                        10,
                        15
                    ),
                    aplicaciones=[
                        (
                            cuota,
                            cuota.importe
                        )
                    ],
                    numero_operacion="COMP-001",
                    comprobantes=[
                        comprobante_pdf,
                        comprobante_jpg,
                    ]
                )

                self.assertEqual(
                    pago.comprobantes.count(),
                    2
                )

                self.assertEqual(
                    ComprobantePago.objects.filter(
                        pago__factura=factura
                    ).count(),
                    2
                )

                for comprobante in (
                    pago.comprobantes.all()
                ):

                    self.assertTrue(
                        comprobante.archivo.storage.exists(
                            comprobante.archivo.name
                        )
                    )
    
    def test_formulario_rechaza_comprobante_invalido(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        archivo_txt = SimpleUploadedFile(
            "archivo.txt",
            b"archivo no permitido",
            content_type="text/plain"
        )

        archivos = MultiValueDict({
            "comprobantes": [
                archivo_txt
            ]
        })

        form = RegistrarPagoForm(
            data={
                "fecha_transferencia": "2026-10-15",
                "numero_operacion": "COMP-002",
                "observaciones": "",
                (
                    f"concepto_"
                    f"{cuota.id_detalle}"
                ): str(
                    cuota.importe
                ),
            },
            files=archivos,
            factura=factura
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "comprobantes",
            form.errors
        )
    
    def test_comprobante_permanece_al_validar_pago(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        archivo = SimpleUploadedFile(
            "comprobante.png",
            b"imagen png de prueba",
            content_type="image/png"
        )

        with tempfile.TemporaryDirectory() as media_root:

            with override_settings(
                MEDIA_ROOT=media_root
            ):

                pago = registrar_pago(
                    factura=factura,
                    fecha_transferencia=date(
                        2026,
                        10,
                        15
                    ),
                    aplicaciones=[
                        (
                            cuota,
                            cuota.importe
                        )
                    ],
                    numero_operacion="COMP-003",
                    comprobantes=[
                        archivo
                    ]
                )

                self.assertEqual(
                    pago.comprobantes.count(),
                    1
                )

                validar_pago(
                    pago
                )

                pago.refresh_from_db()

                self.assertEqual(
                    pago.estado,
                    "VALIDADO"
                )

                self.assertEqual(
                    pago.comprobantes.count(),
                    1
                )

                comprobante = (
                    pago.comprobantes.first()
                )

                self.assertTrue(
                    comprobante.archivo.storage.exists(
                        comprobante.archivo.name
                    )
                )
    
    def test_factura_vencida_con_deuda(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        actualizar_facturas_vencidas(
            fecha_referencia=date(
                2026,
                10,
                11
            )
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.estado,
            "VENCIDA"
        )

        self.assertEqual(
            factura.total_pagado,
            Decimal("0.00")
        )

        self.assertEqual(
            factura.saldo,
            Decimal("148000.00")
        )


    def test_factura_vencida_con_pago_parcial_sigue_vencida(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        # Primero dejamos vencer la factura.

        actualizar_facturas_vencidas(
            fecha_referencia=date(
                2026,
                10,
                11
            )
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.estado,
            "VENCIDA"
        )

        # Después pagamos solamente la cuota.

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        pago = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                12
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                )
            ],
            numero_operacion="DEUDA-001"
        )

        validar_pago(
            pago
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.total_pagado,
            Decimal("55000.00")
        )

        self.assertEqual(
            factura.saldo,
            Decimal("93000.00")
        )

        # Aunque hubo un pago parcial,
        # sigue vencida porque conserva deuda.

        self.assertEqual(
            factura.estado,
            "VENCIDA"
        )


    def test_factura_pagada_no_pasa_a_vencida(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        detalles = list(
            factura.detalles.all()
        )

        pago = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                8
            ),
            aplicaciones=[
                (
                    detalle,
                    detalle.importe
                )
                for detalle in detalles
            ],
            numero_operacion="DEUDA-002"
        )

        validar_pago(
            pago
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.estado,
            "PAGADA"
        )

        self.assertEqual(
            factura.saldo,
            Decimal("0.00")
        )

        # Simulamos una fecha posterior
        # al vencimiento.

        actualizar_facturas_vencidas(
            fecha_referencia=date(
                2026,
                10,
                20
            )
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.estado,
            "PAGADA"
        )

        self.assertEqual(
            factura.saldo,
            Decimal("0.00")
        )


    def test_factura_no_vence_el_mismo_dia_del_vencimiento(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        # La cuota vence el 10/10.
        # Ese mismo día todavía NO debe
        # considerarse vencida.

        actualizar_facturas_vencidas(
            fecha_referencia=date(
                2026,
                10,
                10
            )
        )

        factura.refresh_from_db()

        self.assertEqual(
            factura.estado,
            "PENDIENTE"
        )

        self.assertEqual(
            factura.saldo,
            Decimal("148000.00")
        )
    
    def _login_admin(self):

        usuario = User.objects.create_user(
            username="admin_reportes",
            password="admin123"
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN
        )

        self.client.force_login(
            usuario
        )
    
    def test_reporte_general_calcula_ingresos_y_deuda(self):

        self._login_admin()

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        # Evitamos que durante el test
        # pase automáticamente a VENCIDA.

        factura.fecha_vencimiento = date(
            2026,
            12,
            31
        )

        factura.save(
            update_fields=[
                "fecha_vencimiento"
            ]
        )

        cuota = factura.detalles.get(
            tipo_concepto="CUOTA"
        )

        futbol = factura.detalles.get(
            grupo_deportivo=self.grupo_futbol
        )

        voley = factura.detalles.get(
            grupo_deportivo=self.grupo_voley
        )

        # Cuota + fútbol validados
        pago_validado = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    cuota,
                    cuota.importe
                ),
                (
                    futbol,
                    futbol.importe
                ),
            ],
            numero_operacion="REP-001"
        )

        validar_pago(
            pago_validado
        )

        # Vóley queda solamente PENDIENTE.
        registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                16
            ),
            aplicaciones=[
                (
                    voley,
                    voley.importe
                )
            ],
            numero_operacion="REP-002"
        )

        # Creamos otra factura para asegurarnos
        # de que el filtro por alumno funcione.

        generar_factura_alumno(
            alumno=self.alumno_sin_servicios,
            mes=10,
            anio=2026
        )

        response = self.client.get(
            reverse(
                "reporte_pagos"
            ),
            {
                "mes": 10,
                "anio": 2026,
                "alumno": self.alumno.pk,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context[
                "total_facturado"
            ],
            Decimal("148000.00")
        )

        self.assertEqual(
            response.context[
                "total_pagado"
            ],
            Decimal("75000.00")
        )

        self.assertEqual(
            response.context[
                "total_deuda"
            ],
            Decimal("73000.00")
        )

        self.assertEqual(
            response.context[
                "total_cuotas"
            ],
            Decimal("55000.00")
        )

        self.assertEqual(
            response.context[
                "total_deportes"
            ],
            Decimal("20000.00")
        )

        # El vóley pendiente NO debe
        # considerarse ingreso.

        self.assertEqual(
            response.context[
                "cantidad_parciales"
            ],
            1
        )

        self.assertEqual(
            response.context[
                "facturas"
            ].count(),
            1
        )
    
    def test_reporte_deportes_solo_suma_pagos_validados(self):

        self._login_admin()

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        futbol = factura.detalles.get(
            grupo_deportivo=self.grupo_futbol
        )

        voley = factura.detalles.get(
            grupo_deportivo=self.grupo_voley
        )

        pago_futbol = registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    futbol,
                    futbol.importe
                )
            ],
            numero_operacion="DEP-001"
        )

        validar_pago(
            pago_futbol
        )

        # Este queda pendiente y no
        # debe aparecer como ingreso.

        registrar_pago(
            factura=factura,
            fecha_transferencia=date(
                2026,
                10,
                16
            ),
            aplicaciones=[
                (
                    voley,
                    voley.importe
                )
            ],
            numero_operacion="DEP-002"
        )

        response = self.client.get(
            reverse(
                "reporte_deportes"
            ),
            {
                "mes": 10,
                "anio": 2026,
                "deporte": self.futbol.pk,
                "nivel": self.nivel.pk,
                "profesor": self.profesor.pk,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context[
                "total_cobrado"
            ],
            Decimal("20000.00")
        )

        reporte = list(
            response.context[
                "reporte"
            ]
        )

        self.assertEqual(
            len(reporte),
            1
        )

        fila = reporte[0]

        self.assertEqual(
            fila["total_cobrado"],
            Decimal("20000.00")
        )

        self.assertEqual(
            fila["cantidad_alumnos"],
            1
        )

        self.assertEqual(
            fila["cantidad_pagos"],
            1
        )
    
    def test_reporte_transporte_agrupa_por_ruta(self):

        self._login_admin()

        # El alumno principal ya posee
        # Zona Centro en setUp.

        ContratacionTransporte.objects.create(
            alumno=self.alumno_sin_servicios,
            ruta=self.ruta,
            mes=10,
            anio=2026,
            estado=True
        )

        factura1 = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        factura2 = generar_factura_alumno(
            alumno=self.alumno_sin_servicios,
            mes=10,
            anio=2026
        )

        transporte1 = (
            factura1.detalles.get(
                tipo_concepto="TRANSPORTE"
            )
        )

        transporte2 = (
            factura2.detalles.get(
                tipo_concepto="TRANSPORTE"
            )
        )

        pago1 = registrar_pago(
            factura=factura1,
            fecha_transferencia=date(
                2026,
                10,
                15
            ),
            aplicaciones=[
                (
                    transporte1,
                    transporte1.importe
                )
            ],
            numero_operacion="TRANS-001"
        )

        validar_pago(
            pago1
        )

        pago2 = registrar_pago(
            factura=factura2,
            fecha_transferencia=date(
                2026,
                10,
                16
            ),
            aplicaciones=[
                (
                    transporte2,
                    transporte2.importe
                )
            ],
            numero_operacion="TRANS-002"
        )

        validar_pago(
            pago2
        )

        response = self.client.get(
            reverse(
                "reporte_transporte"
            ),
            {
                "mes": 10,
                "anio": 2026,
                "ruta": self.ruta.pk,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context[
                "total_cobrado"
            ],
            Decimal("60000.00")
        )

        reporte = list(
            response.context[
                "reporte"
            ]
        )

        self.assertEqual(
            len(reporte),
            1
        )

        fila = reporte[0]

        self.assertEqual(
            fila["total_cobrado"],
            Decimal("60000.00")
        )

        self.assertEqual(
            fila["cantidad_alumnos"],
            2
        )

        self.assertEqual(
            fila["cantidad_pagos"],
            2
        )
    
    def test_reportes_requieren_usuario_admin(self):

        usuario = User.objects.create_user(
            username="usuario_no_admin",
            password="123456"
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ALUMNO
        )

        self.client.force_login(
            usuario
        )

        urls = [
            reverse(
                "reporte_pagos"
            ),
            reverse(
                "reporte_deportes"
            ),
            reverse(
                "reporte_transporte"
            ),
        ]

        for url in urls:

            response = self.client.get(
                url
            )

            self.assertEqual(
                response.status_code,
                302
            )