from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "quienes-somos/",
        views.quienes_somos,
        name="quienes_somos"
    ),

    path(
        "niveles/",
        views.niveles,
        name="niveles"
    ),
    #Bienestar
    path(
        "bienestar/",
        views.bienestar,
        name="bienestar"
    ),
    #Galeria
    path(
        "galeria/",
        views.galeria,
        name="galeria"
    ),
    
    path(
        "gestion/galeria/",
        views.galeria_admin_lista,
        name="galeria_admin_lista"
    ),

    path(
        "gestion/galeria/nueva/",
        views.galeria_admin_crear,
        name="galeria_admin_crear"
    ),

    path(
        "gestion/galeria/<int:id_imagen>/editar/",
        views.galeria_admin_editar,
        name="galeria_admin_editar"
    ),

    path(
        "gestion/galeria/<int:id_imagen>/publicacion/",
        views.galeria_admin_publicacion,
        name="galeria_admin_publicacion"
    ),
    #Noticias
    path(
        "noticias/",
        views.noticias,
        name="noticias"
    ),
    path(
        "noticias/<int:id_noticia>/",
        views.noticia_detalle,
        name="noticia_detalle"
    ),
    path(
        "gestion/noticias/",
        views.noticia_admin_lista,
        name="noticia_admin_lista"
    ),

    path(
        "gestion/noticias/nueva/",
        views.noticia_admin_crear,
        name="noticia_admin_crear"
    ),

    path(
        "gestion/noticias/<int:id_noticia>/editar/",
        views.noticia_admin_editar,
        name="noticia_admin_editar"
    ),

    path(
        "gestion/noticias/<int:id_noticia>/publicacion/",
        views.noticia_admin_publicacion,
        name="noticia_admin_publicacion"
    ),



    #Contacto
    path(
        "contacto/",
        views.contacto,
        name="contacto"
    ),

    #Inscripcion y solicitudes
    path(
        "inscripcion/",
        views.inscripcion,
        name="inscripcion"
    ),
    path(
        "gestion/solicitudes/",
        views.solicitud_inscripcion_lista,
        name="solicitud_inscripcion_lista"
    ),

    path(
        (
            "gestion/solicitudes/"
            "<int:id_solicitud>/"
        ),
        views.solicitud_inscripcion_detalle,
        name="solicitud_inscripcion_detalle"
    ),

    path(
        (
            "gestion/solicitudes/"
            "<int:id_solicitud>/aprobar/"
        ),
        views.solicitud_inscripcion_aprobar,
        name="solicitud_inscripcion_aprobar"
    ),

    path(
        (
            "gestion/solicitudes/"
            "<int:id_solicitud>/rechazar/"
        ),
        views.solicitud_inscripcion_rechazar,
        name="solicitud_inscripcion_rechazar"
    ),
    #Consultas
    path(
        "gestion/consultas/",
        views.consulta_contacto_lista,
        name="consulta_contacto_lista"
    ),

    path(
        (
            "gestion/consultas/"
            "<int:id_consulta>/"
        ),
        views.consulta_contacto_detalle,
        name="consulta_contacto_detalle"
    ),

    path(
        (
            "gestion/consultas/"
            "<int:id_consulta>/responder/"
        ),
        views.consulta_contacto_responder,
        name="consulta_contacto_responder"
    ),
    #Opiniones
    path(
        "opiniones/",
        views.opiniones,
        name="opiniones"
    ),
    path(
        "gestion/opiniones/",
        views.opinion_lista,
        name="opinion_lista"
    ),

    path(
        (
            "gestion/opiniones/"
            "<int:id_opinion>/"
        ),
        views.opinion_detalle,
        name="opinion_detalle"
    ),

    path(
        (
            "gestion/opiniones/"
            "<int:id_opinion>/aprobar/"
        ),
        views.opinion_aprobar,
        name="opinion_aprobar"
    ),

    path(
        (
            "gestion/opiniones/"
            "<int:id_opinion>/rechazar/"
        ),
        views.opinion_rechazar,
        name="opinion_rechazar"
    ),

    #Empleo
    path(
        "empleo/",
        views.empleo,
        name="empleo"
    ),
    
    path(
        "gestion/empleo/",
        views.empleo_admin_lista,
        name="empleo_admin_lista"
    ),

    path(
        (
            "gestion/empleo/"
            "<int:id_postulacion>/"
        ),
        views.empleo_admin_detalle,
        name="empleo_admin_detalle"
    ),

    path(
        (
            "gestion/empleo/"
            "<int:id_postulacion>/revisar/"
        ),
        views.empleo_admin_revisar,
        name="empleo_admin_revisar"
    ),

    path(
        (
            "gestion/empleo/"
            "<int:id_postulacion>/descartar/"
        ),
        views.empleo_admin_descartar,
        name="empleo_admin_descartar"
    ),

    path(
        (
            "gestion/empleo/"
            "<int:id_postulacion>/cv/"
        ),
        views.empleo_admin_descargar_cv,
        name="empleo_admin_descargar_cv"
    ),

]