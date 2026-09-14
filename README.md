# Educar Para Transformar

Sistema web de gestión educativa desarrollado como Trabajo Práctico Integrador
de la materia Metodología de Sistemas II.

## Tecnologías

- Python
- Django
- PostgreSQL
- HTML
- CSS
- Git / GitHub

## Arquitectura

La aplicación utiliza una arquitectura web basada en Django.

- Presentación: HTML + CSS
- Lógica de negocio: Django
- Persistencia: PostgreSQL
- Acceso a datos: Django ORM

## Módulos

### Accounts

Gestiona:

- usuarios;
- autenticación;
- perfiles;
- roles;
- permisos.

Roles disponibles:

- Administrador
- Docente
- Alumno
- Padre/Tutor

### Academic

Actualmente implementa:

- niveles educativos;
- cursos;
- alumnos.

## Funcionalidades implementadas

### Gestión de alumnos

- Alta de alumno.
- Listado de alumnos.
- Modificación de alumno.
- Baja lógica mediante estado inactivo.
- Validación de DNI único.
- Validación de legajo único.

### Alumno autenticado

El alumno puede:

- consultar sus propios datos;
- consultar su curso;
- consultar su nivel educativo;
- modificar correo;
- modificar teléfono;
- modificar domicilio.

El alumno no puede modificar:

- DNI;
- legajo;
- nombre;
- apellido;
- fecha de nacimiento;
- curso;
- estado.

## Seguridad

El sistema utiliza autenticación de Django.

Cada usuario posee un PerfilUsuario que determina su rol.

La selección visual de perfil durante el ingreso no concede permisos.
El backend valida que el rol seleccionado coincida con el rol real del usuario.

El CRUD administrativo de alumnos está protegido para usuarios con rol Administrador.

## Base de datos

El proyecto utiliza PostgreSQL.

Las credenciales de conexión se almacenan en un archivo `.env`, excluido del repositorio mediante `.gitignore`.

## Ejecutar el proyecto

Crear y activar el entorno virtual:

```bash
py -m venv .venv
```
Instalar dependencias:

```bash
pip install -r requirements.txt
```
