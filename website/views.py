from django.contrib import messages
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from django.http import FileResponse

from .forms import (
    SolicitudInscripcionForm,
    ConsultaContactoForm,
    OpinionForm,
    NoticiaForm,
    ImagenGaleriaForm,
    PostulacionEmpleoForm,
)

from .models import (
    SolicitudInscripcion,
    ConsultaContacto,
    Opinion,
    Noticia,
    ImagenGaleria,
    PostulacionEmpleo,
)


def home(request):

    imagenes_carrusel = (
        ImagenGaleria.objects
        .filter(
            publicada=True
        )
        .order_by(
            "orden",
            "-fecha_carga"
        )[:3]
    )


    ultimas_noticias = (
        Noticia.objects
        .filter(
            publicada=True
        )
        .order_by(
            "-fecha_publicacion"
        )[:3]
    )


    ultimas_opiniones = (
        Opinion.objects
        .filter(
            estado=Opinion.Estado.APROBADA
        )
        .order_by(
            "-fecha_opinion"
        )[:3]
    )


    return render(
        request,
        "website/home.html",
        {
            "imagenes_carrusel": (
                imagenes_carrusel
            ),
            "ultimas_noticias": (
                ultimas_noticias
            ),
            "ultimas_opiniones": (
                ultimas_opiniones
            ),
        }
    )

def quienes_somos(request):

    return render(
        request,
        "website/quienes_somos.html"
    )


def niveles(request):

    return render(
        request,
        "website/niveles.html"
    )


def bienestar(request):

    return render(
        request,
        "website/bienestar.html"
    )


def galeria(request):

    imagenes = (
        ImagenGaleria.objects.filter(
            publicada=True
        )
    )


    return render(
        request,
        "website/galeria.html",
        {
            "imagenes": imagenes,
        }
    )


def noticias(request):

    noticias_publicadas = (
        Noticia.objects.filter(
            publicada=True
        )
    )


    return render(
        request,
        "website/noticias.html",
        {
            "noticias": (
                noticias_publicadas
            ),
        }
    )

def noticia_detalle(
    request,
    id_noticia
):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia,
        publicada=True
    )


    return render(
        request,
        "website/noticia_detalle.html",
        {
            "noticia": noticia,
        }
    )

def contacto(request):

    if request.method == "POST":

        form = ConsultaContactoForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    "Tu consulta fue enviada "
                    "correctamente. "
                    "Nos pondremos en contacto "
                    "a la brevedad."
                )
            )

            return redirect(
                "contacto"
            )

    else:

        form = ConsultaContactoForm()


    return render(
        request,
        "website/contacto.html",
        {
            "form": form,
        }
    )


def inscripcion(request):

    if request.method == "POST":

        form = SolicitudInscripcionForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    "Tu solicitud fue enviada "
                    "correctamente. "
                    "La institución la revisará "
                    "y se comunicará con vos."
                )
            )

            return redirect(
                "inscripcion"
            )

    else:

        form = SolicitudInscripcionForm()


    return render(
        request,
        "website/inscripcion.html",
        {
            "form": form,
        }
    )


def empleo(request):

    if request.method == "POST":

        form = PostulacionEmpleoForm(
            request.POST,
            request.FILES
        )


        if form.is_valid():

            form.save()


            messages.success(
                request,
                (
                    "Tu postulación fue enviada "
                    "correctamente. "
                    "Gracias por tu interés "
                    "en formar parte de "
                    "Educar Para Transformar."
                )
            )


            return redirect(
                "empleo"
            )

    else:

        form = (
            PostulacionEmpleoForm()
        )


    return render(
        request,
        "website/empleo.html",
        {
            "form": form,
        }
    )
    
def opiniones(request):

    if request.method == "POST":

        form = OpinionForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    "Gracias por compartir "
                    "tu opinión. "
                    "Será publicada una vez "
                    "que sea revisada."
                )
            )

            return redirect(
                "opiniones"
            )

    else:

        form = OpinionForm()


    opiniones_publicadas = (
        Opinion.objects.filter(
            estado=(
                Opinion
                .Estado
                .APROBADA
            )
        )
    )


    return render(
        request,
        "website/opiniones.html",
        {
            "form": form,
            "opiniones": (
                opiniones_publicadas
            ),
        }
    )
    
#Solicitudes    
@admin_required
def solicitud_inscripcion_lista(
    request
):

    estado = (
        request.GET.get(
            "estado",
            ""
        )
        .strip()
        .upper()
    )


    solicitudes = (
        SolicitudInscripcion.objects
        .select_related(
            "nivel_solicitado"
        )
    )


    estados_validos = {
        valor
        for valor, etiqueta
        in SolicitudInscripcion
        .Estado
        .choices
    }


    if estado in estados_validos:

        solicitudes = (
            solicitudes.filter(
                estado=estado
            )
        )

    else:

        estado = ""


    pendientes = (
        SolicitudInscripcion.objects
        .filter(
            estado=(
                SolicitudInscripcion
                .Estado
                .PENDIENTE
            )
        )
        .count()
    )


    return render(
        request,
        (
            "website/"
            "solicitudes_lista.html"
        ),
        {
            "solicitudes": solicitudes,
            "estado_seleccionado": estado,
            "pendientes": pendientes,
        }
    )


@admin_required
def solicitud_inscripcion_detalle(
    request,
    id_solicitud
):

    solicitud = get_object_or_404(
        SolicitudInscripcion.objects
        .select_related(
            "nivel_solicitado"
        ),
        id_solicitud=id_solicitud
    )


    return render(
        request,
        (
            "website/"
            "solicitud_detalle.html"
        ),
        {
            "solicitud": solicitud,
        }
    )


@admin_required
@require_POST
def solicitud_inscripcion_aprobar(
    request,
    id_solicitud
):

    solicitud = get_object_or_404(
        SolicitudInscripcion,
        id_solicitud=id_solicitud
    )


    if (
        solicitud.estado
        != SolicitudInscripcion
        .Estado
        .PENDIENTE
    ):

        messages.info(
            request,
            (
                "La solicitud ya fue "
                "revisada anteriormente."
            )
        )

        return redirect(
            "solicitud_inscripcion_detalle",
            id_solicitud=id_solicitud
        )


    solicitud.estado = (
        SolicitudInscripcion
        .Estado
        .APROBADA
    )

    solicitud.fecha_revision = (
        timezone.now()
    )

    solicitud.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        (
            "La solicitud fue aprobada "
            "correctamente."
        )
    )


    return redirect(
        "solicitud_inscripcion_detalle",
        id_solicitud=id_solicitud
    )


@admin_required
@require_POST
def solicitud_inscripcion_rechazar(
    request,
    id_solicitud
):

    solicitud = get_object_or_404(
        SolicitudInscripcion,
        id_solicitud=id_solicitud
    )


    if (
        solicitud.estado
        != SolicitudInscripcion
        .Estado
        .PENDIENTE
    ):

        messages.info(
            request,
            (
                "La solicitud ya fue "
                "revisada anteriormente."
            )
        )

        return redirect(
            "solicitud_inscripcion_detalle",
            id_solicitud=id_solicitud
        )


    solicitud.estado = (
        SolicitudInscripcion
        .Estado
        .RECHAZADA
    )

    solicitud.fecha_revision = (
        timezone.now()
    )

    solicitud.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        (
            "La solicitud fue rechazada."
        )
    )


    return redirect(
        "solicitud_inscripcion_detalle",
        id_solicitud=id_solicitud
    )

#CONSULTAS

@admin_required
def consulta_contacto_lista(
    request
):

    estado = (
        request.GET.get(
            "estado",
            ""
        )
        .strip()
        .upper()
    )


    consultas = (
        ConsultaContacto.objects.all()
    )


    estados_validos = {
        valor
        for valor, etiqueta
        in ConsultaContacto
        .Estado
        .choices
    }


    if estado in estados_validos:

        consultas = (
            consultas.filter(
                estado=estado
            )
        )

    else:

        estado = ""


    pendientes = (
        ConsultaContacto.objects
        .filter(
            estado=(
                ConsultaContacto
                .Estado
                .PENDIENTE
            )
        )
        .count()
    )


    return render(
        request,
        "website/consultas_lista.html",
        {
            "consultas": consultas,
            "estado_seleccionado": estado,
            "pendientes": pendientes,
        }
    )


@admin_required
def consulta_contacto_detalle(
    request,
    id_consulta
):

    consulta = get_object_or_404(
        ConsultaContacto,
        id_consulta=id_consulta
    )


    return render(
        request,
        "website/consulta_detalle.html",
        {
            "consulta": consulta,
        }
    )


@admin_required
@require_POST
def consulta_contacto_responder(
    request,
    id_consulta
):

    consulta = get_object_or_404(
        ConsultaContacto,
        id_consulta=id_consulta
    )


    if (
        consulta.estado
        == ConsultaContacto
        .Estado
        .RESPONDIDA
    ):

        messages.info(
            request,
            (
                "La consulta ya estaba "
                "marcada como respondida."
            )
        )

        return redirect(
            "consulta_contacto_detalle",
            id_consulta=id_consulta
        )


    consulta.estado = (
        ConsultaContacto
        .Estado
        .RESPONDIDA
    )

    consulta.fecha_respuesta = (
        timezone.now()
    )

    consulta.save(
        update_fields=[
            "estado",
            "fecha_respuesta",
        ]
    )


    messages.success(
        request,
        (
            "La consulta fue marcada "
            "como respondida."
        )
    )


    return redirect(
        "consulta_contacto_detalle",
        id_consulta=id_consulta
    )
    
#OPINIONES

@admin_required
def opinion_lista(
    request
):

    estado = (
        request.GET.get(
            "estado",
            ""
        )
        .strip()
        .upper()
    )


    opiniones = (
        Opinion.objects.all()
    )


    estados_validos = {
        valor
        for valor, etiqueta
        in Opinion
        .Estado
        .choices
    }


    if estado in estados_validos:

        opiniones = (
            opiniones.filter(
                estado=estado
            )
        )

    else:

        estado = ""


    pendientes = (
        Opinion.objects.filter(
            estado=(
                Opinion
                .Estado
                .PENDIENTE
            )
        )
        .count()
    )


    return render(
        request,
        "website/opiniones_lista.html",
        {
            "opiniones": opiniones,
            "estado_seleccionado": estado,
            "pendientes": pendientes,
        }
    )


@admin_required
def opinion_detalle(
    request,
    id_opinion
):

    opinion = get_object_or_404(
        Opinion,
        id_opinion=id_opinion
    )


    return render(
        request,
        "website/opinion_detalle.html",
        {
            "opinion": opinion,
        }
    )


@admin_required
@require_POST
def opinion_aprobar(
    request,
    id_opinion
):

    opinion = get_object_or_404(
        Opinion,
        id_opinion=id_opinion
    )


    if (
        opinion.estado
        != Opinion.Estado.PENDIENTE
    ):

        messages.info(
            request,
            (
                "La opinión ya fue "
                "revisada anteriormente."
            )
        )

        return redirect(
            "opinion_detalle",
            id_opinion=id_opinion
        )


    opinion.estado = (
        Opinion.Estado.APROBADA
    )

    opinion.fecha_revision = (
        timezone.now()
    )

    opinion.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        (
            "La opinión fue aprobada "
            "y ya puede verse "
            "en la página pública."
        )
    )


    return redirect(
        "opinion_detalle",
        id_opinion=id_opinion
    )


@admin_required
@require_POST
def opinion_rechazar(
    request,
    id_opinion
):

    opinion = get_object_or_404(
        Opinion,
        id_opinion=id_opinion
    )


    if (
        opinion.estado
        != Opinion.Estado.PENDIENTE
    ):

        messages.info(
            request,
            (
                "La opinión ya fue "
                "revisada anteriormente."
            )
        )

        return redirect(
            "opinion_detalle",
            id_opinion=id_opinion
        )


    opinion.estado = (
        Opinion.Estado.RECHAZADA
    )

    opinion.fecha_revision = (
        timezone.now()
    )

    opinion.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        "La opinión fue rechazada."
    )


    return redirect(
        "opinion_detalle",
        id_opinion=id_opinion
    )

@admin_required
def noticia_admin_lista(
    request
):

    noticias = (
        Noticia.objects.all()
    )


    return render(
        request,
        "website/noticias_admin_lista.html",
        {
            "noticias": noticias,
        }
    )


@admin_required
def noticia_admin_crear(
    request
):

    if request.method == "POST":

        form = NoticiaForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La noticia fue creada correctamente."
            )

            return redirect(
                "noticia_admin_lista"
            )

    else:

        form = NoticiaForm()


    return render(
        request,
        "website/noticia_admin_form.html",
        {
            "form": form,
            "titulo": "Nueva noticia",
        }
    )


@admin_required
def noticia_admin_editar(
    request,
    id_noticia
):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia
    )


    if request.method == "POST":

        form = NoticiaForm(
            request.POST,
            request.FILES,
            instance=noticia
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La noticia fue actualizada."
            )

            return redirect(
                "noticia_admin_lista"
            )

    else:

        form = NoticiaForm(
            instance=noticia
        )


    return render(
        request,
        "website/noticia_admin_form.html",
        {
            "form": form,
            "titulo": "Editar noticia",
            "noticia": noticia,
        }
    )


@admin_required
@require_POST
def noticia_admin_publicacion(
    request,
    id_noticia
):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia
    )


    noticia.publicada = (
        not noticia.publicada
    )

    noticia.save(
        update_fields=[
            "publicada"
        ]
    )


    if noticia.publicada:

        mensaje = (
            "La noticia fue publicada."
        )

    else:

        mensaje = (
            "La noticia fue ocultada."
        )


    messages.success(
        request,
        mensaje
    )


    return redirect(
        "noticia_admin_lista"
    )

@admin_required
def galeria_admin_lista(
    request
):

    imagenes = (
        ImagenGaleria.objects.all()
    )


    return render(
        request,
        "website/galeria_admin_lista.html",
        {
            "imagenes": imagenes,
        }
    )


@admin_required
def galeria_admin_crear(
    request
):

    if request.method == "POST":

        form = ImagenGaleriaForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    "La imagen fue agregada "
                    "a la galería."
                )
            )

            return redirect(
                "galeria_admin_lista"
            )

    else:

        form = ImagenGaleriaForm()


    return render(
        request,
        "website/galeria_admin_form.html",
        {
            "form": form,
            "titulo": "Nueva imagen",
        }
    )


@admin_required
def galeria_admin_editar(
    request,
    id_imagen
):

    imagen = get_object_or_404(
        ImagenGaleria,
        id_imagen=id_imagen
    )


    if request.method == "POST":

        form = ImagenGaleriaForm(
            request.POST,
            request.FILES,
            instance=imagen
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La imagen fue actualizada."
            )

            return redirect(
                "galeria_admin_lista"
            )

    else:

        form = ImagenGaleriaForm(
            instance=imagen
        )


    return render(
        request,
        "website/galeria_admin_form.html",
        {
            "form": form,
            "titulo": "Editar imagen",
            "imagen": imagen,
        }
    )


@admin_required
@require_POST
def galeria_admin_publicacion(
    request,
    id_imagen
):

    imagen = get_object_or_404(
        ImagenGaleria,
        id_imagen=id_imagen
    )


    imagen.publicada = (
        not imagen.publicada
    )

    imagen.save(
        update_fields=[
            "publicada"
        ]
    )


    messages.success(
        request,
        (
            "El estado de la imagen "
            "fue actualizado."
        )
    )


    return redirect(
        "galeria_admin_lista"
    )

#EMPLEO
@admin_required
def empleo_admin_lista(
    request
):

    estado = (
        request.GET.get(
            "estado",
            ""
        )
        .strip()
        .upper()
    )


    postulaciones = (
        PostulacionEmpleo.objects.all()
    )


    estados_validos = {
        valor
        for valor, etiqueta
        in PostulacionEmpleo
        .Estado
        .choices
    }


    if estado in estados_validos:

        postulaciones = (
            postulaciones.filter(
                estado=estado
            )
        )

    else:

        estado = ""


    pendientes = (
        PostulacionEmpleo.objects
        .filter(
            estado=(
                PostulacionEmpleo
                .Estado
                .PENDIENTE
            )
        )
        .count()
    )


    return render(
        request,
        (
            "website/"
            "empleo_admin_lista.html"
        ),
        {
            "postulaciones": postulaciones,
            "estado_seleccionado": estado,
            "pendientes": pendientes,
        }
    )


@admin_required
def empleo_admin_detalle(
    request,
    id_postulacion
):

    postulacion = get_object_or_404(
        PostulacionEmpleo,
        id_postulacion=id_postulacion
    )


    return render(
        request,
        (
            "website/"
            "empleo_admin_detalle.html"
        ),
        {
            "postulacion": postulacion,
        }
    )


@admin_required
@require_POST
def empleo_admin_revisar(
    request,
    id_postulacion
):

    postulacion = get_object_or_404(
        PostulacionEmpleo,
        id_postulacion=id_postulacion
    )


    postulacion.estado = (
        PostulacionEmpleo
        .Estado
        .REVISADA
    )

    postulacion.fecha_revision = (
        timezone.now()
    )

    postulacion.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        (
            "La postulación fue marcada "
            "como revisada."
        )
    )


    return redirect(
        "empleo_admin_detalle",
        id_postulacion=id_postulacion
    )


@admin_required
@require_POST
def empleo_admin_descartar(
    request,
    id_postulacion
):

    postulacion = get_object_or_404(
        PostulacionEmpleo,
        id_postulacion=id_postulacion
    )


    postulacion.estado = (
        PostulacionEmpleo
        .Estado
        .DESCARTADA
    )

    postulacion.fecha_revision = (
        timezone.now()
    )

    postulacion.save(
        update_fields=[
            "estado",
            "fecha_revision",
        ]
    )


    messages.success(
        request,
        (
            "La postulación fue descartada."
        )
    )


    return redirect(
        "empleo_admin_detalle",
        id_postulacion=id_postulacion
    )

@admin_required
def empleo_admin_descargar_cv(
    request,
    id_postulacion
):

    postulacion = get_object_or_404(
        PostulacionEmpleo,
        id_postulacion=id_postulacion
    )


    archivo = (
        postulacion.cv.open(
            "rb"
        )
    )


    nombre_archivo = (
        postulacion.cv.name
        .split("/")[-1]
    )


    return FileResponse(
        archivo,
        as_attachment=True,
        filename=nombre_archivo
    )
