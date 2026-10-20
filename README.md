# Educar Para Transformar

Sistema web de gestión educativa desarrollado como Trabajo Práctico Integrador de la materia **Metodología de Sistemas II**.

El proyecto permite administrar información académica, deportiva, servicios complementarios y aspectos económicos de una institución educativa.

La aplicación cuenta con distintos perfiles de usuario y restringe las funcionalidades disponibles según el rol autenticado.

---

## Tecnologías utilizadas

- Python 3
- Django 5.2
- PostgreSQL
- HTML
- CSS
- Django ORM
- Git
- GitHub
- GitHub Actions
- python-dotenv
- psycopg

---

## Arquitectura

El sistema utiliza una arquitectura web basada en Django.

### Presentación

Interfaz desarrollada mediante:

- Django Templates
- HTML
- CSS

### Lógica de negocio

La lógica principal se implementa mediante:

- Views
- Forms
- Models
- Services

Para operaciones que requieren reglas de negocio adicionales se utilizan servicios específicos, por ejemplo:

- generación de facturas;
- registro y validación de pagos;
- registro de asistencias;
- registro de notas.

### Persistencia

La aplicación utiliza:

- PostgreSQL como sistema gestor de base de datos;
- Django ORM para el acceso y manipulación de los datos.

---

# Módulos

## Accounts

Gestiona la autenticación, perfiles y permisos del sistema.

Cada usuario posee un `PerfilUsuario` asociado.

Roles disponibles:

- Administrador
- Docente
- Alumno
- Padre / Tutor

La aplicación valida el rol real del usuario desde el backend.

La selección visual del perfil durante el inicio de sesión no concede permisos por sí sola.

---

## Academic

Gestiona la información académica de la institución.

Incluye:

- niveles educativos;
- cursos;
- alumnos;
- profesores;
- materias;
- horarios;
- asignación de materias a profesores y cursos;
- tutores;
- asociación entre tutores y alumnos;
- asistencia;
- notas.

### Gestión de alumnos

El administrador puede:

- registrar alumnos;
- listar alumnos;
- modificar alumnos;
- realizar baja lógica;
- asignar cursos.

Se valida la unicidad de:

- DNI;
- legajo.

### Gestión de profesores

El administrador puede:

- registrar profesores;
- modificar profesores;
- listar profesores;
- desactivar profesores;
- asignarlos a materias, cursos y horarios.

### Dictado de materias

Una materia puede asignarse a:

- un profesor;
- un curso;
- un horario.

Esta relación se administra mediante `DictadoMateria`.

---

# Asistencia

Los docentes pueden registrar la asistencia de los alumnos pertenecientes a sus materias y cursos asignados.

Estados disponibles:

- Presente
- Ausente
- Tarde
- Justificado

El sistema:

- evita registros duplicados para el mismo alumno, materia y fecha;
- permite corregir una asistencia ya registrada;
- impide registrar alumnos de otro curso;
- impide que un docente modifique dictados que no le pertenecen;
- impide registrar asistencia para fechas futuras;
- permite consultar el historial de asistencias.

---

# Notas

Los docentes pueden registrar calificaciones para los alumnos de sus cursos.

Cada nota posee:

- alumno;
- materia / dictado;
- período;
- evaluación;
- calificación;
- fecha;
- observaciones.

Las calificaciones permitidas se encuentran entre **1 y 10**.

El sistema:

- permite calificaciones decimales;
- evita duplicados para una misma evaluación;
- permite modificar una nota existente;
- impide cargar notas a alumnos de otro curso;
- restringe el acceso a los dictados del docente autenticado;
- permite consultar el historial de evaluaciones.

---

# Vista del alumno

El alumno autenticado puede consultar:

- sus datos personales;
- curso;
- nivel educativo;
- materias;
- profesores;
- horarios;
- notas;
- historial de asistencia.

También puede modificar únicamente sus datos de contacto:

- correo electrónico;
- teléfono;
- domicilio.

No puede modificar información académica ni administrativa.

---

# Vista del tutor

El padre o tutor puede consultar los alumnos que se encuentran asociados a su cuenta.

Para cada alumno asociado puede consultar:

- datos académicos;
- materias;
- profesores;
- horarios;
- notas;
- asistencia;
- deportes activos.

Un tutor no puede consultar información de alumnos que no estén asociados a su cuenta.

La consulta de deuda podrá incorporarse posteriormente.

---

# Sports

El módulo de deportes permite administrar:

- deportes;
- grupos deportivos;
- profesores;
- horarios;
- valores mensuales;
- inscripciones de alumnos.

Las inscripciones controlan:

- duplicados;
- cantidad de deportes activos;
- superposición de horarios.

Las bajas se realizan de forma lógica conservando la información histórica.

---

# Services

Gestiona servicios complementarios de la institución.

Actualmente incluye:

## Transporte

Permite administrar:

- rutas;
- valores mensuales;
- contrataciones de transporte por alumno;
- período mensual de contratación.

## Comedor

Permite administrar:

- servicios de comedor;
- valores;
- contrataciones por alumno;
- período mensual de contratación.

El sistema evita contrataciones duplicadas para un mismo alumno y período.

---

# Billing

Gestiona cuotas, facturación y pagos.

## Cuotas

Permite:

- registrar cuotas mensuales;
- modificar cuotas;
- desactivar cuotas;
- definir mes, año, importe y fecha de vencimiento.

## Facturación

Las facturas se generan por alumno y período.

Una factura puede incluir conceptos correspondientes a:

- cuota mensual;
- deportes;
- transporte;
- comedor.

Los importes se registran en detalles de factura para conservar el valor histórico utilizado al momento de generar la factura.

Estados disponibles:

- Pendiente
- Parcial
- Pagada
- Vencida
- Anulada

El sistema calcula:

- total facturado;
- total pagado;
- saldo pendiente.

También actualiza las facturas vencidas según su fecha de vencimiento.

---

# Pagos

Los pagos se registran contra una factura.

Estados disponibles:

- Pendiente
- Validado
- Rechazado

Un pago puede aplicarse a uno o más conceptos de la factura.

El sistema controla:

- que el importe sea válido;
- que no se supere el saldo disponible;
- que las aplicaciones correspondan a la misma factura;
- que los pagos rechazados liberen nuevamente el saldo;
- que solamente los pagos validados reduzcan la deuda real.

---

# Comprobantes de transferencia

Al registrar un pago se pueden adjuntar uno o más comprobantes.

Formatos admitidos:

- PDF
- JPG
- JPEG
- PNG

Los archivos se almacenan dentro del directorio `media/`.

El directorio de archivos subidos se encuentra excluido del repositorio mediante `.gitignore`.

---

# Reportes administrativos

El sistema cuenta con reportes para usuarios administradores.

Actualmente se encuentran implementados:

- reporte general de pagos;
- reporte de ingresos por deportes;
- reporte de ingresos por transporte.

El reporte general permite consultar:

- total facturado;
- total pagado;
- deuda pendiente;
- facturas pendientes;
- facturas parciales;
- facturas pagadas;
- facturas vencidas;
- ingresos por tipo de concepto.

Los reportes consideran únicamente pagos validados para calcular ingresos efectivos.

---

# Seguridad y permisos

El sistema utiliza la autenticación provista por Django.

Cada usuario posee un perfil con un rol determinado.

Se utilizan decoradores de autorización para restringir el acceso a las vistas según el rol:

- administrador;
- docente;
- alumno;
- tutor.

Además de controlar el rol, las vistas verifican la relación entre el usuario autenticado y los datos solicitados.

Por ejemplo:

- un docente solamente puede administrar sus propios dictados;
- un alumno solamente puede consultar sus propios datos académicos;
- un tutor solamente puede consultar alumnos asociados a su cuenta.

---

# Base de datos

El proyecto utiliza PostgreSQL.

La configuración se obtiene mediante variables de entorno almacenadas en un archivo `.env`.

El archivo `.env` no debe incorporarse al repositorio.

Variables utilizadas:

```env
SECRET_KEY=clave-local-de-django
DEBUG=True

DB_NAME=nombre_base_datos
DB_USER=usuario_postgresql
DB_PASSWORD=contraseña_postgresql
DB_HOST=localhost
DB_PORT=5432
```

Nunca se deben publicar credenciales reales dentro del repositorio.

---

# Instalación

Clonar el repositorio:

```bash
git clone https://github.com/luciano-castillo/Educar-para-Trasformar.git
```

Ingresar al proyecto:

```bash
cd Educar-para-Trasformar
```

Crear el entorno virtual:

```bash
py -m venv .venv
```

En Windows PowerShell, activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

# Configuración de PostgreSQL

Antes de ejecutar Django debe existir una base de datos PostgreSQL y un usuario con permisos sobre ella.

Luego se deben configurar en `.env`:

```env
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
```

---

# Migraciones

Aplicar las migraciones existentes:

```bash
python manage.py migrate
```

Para verificar que no existan cambios de modelos sin una migración correspondiente:

```bash
python manage.py makemigrations --check --dry-run
```

---

# Ejecutar el proyecto

Iniciar el servidor de desarrollo:

```bash
python manage.py runserver
```

Por defecto Django estará disponible en:

```text
http://127.0.0.1:8000/
```

---

# Verificación del proyecto

Ejecutar las comprobaciones internas de Django:

```bash
python manage.py check
```

---

# Pruebas automatizadas

Para ejecutar todas las pruebas:

```bash
python manage.py test
```

Para ejecutar únicamente las pruebas del módulo académico:

```bash
python manage.py test academic
```

Actualmente el proyecto cuenta con **64 pruebas automatizadas** distribuidas entre los módulos principales.

Las pruebas verifican, entre otros aspectos:

- reglas de facturación;
- pagos;
- comprobantes;
- cálculo de deuda;
- deportes;
- servicios;
- asistencia;
- notas;
- permisos;
- privacidad entre alumnos;
- acceso de tutores.

---

# Integración continua

El proyecto utiliza **GitHub Actions**.

Workflow:

```text
.github/workflows/django-ci.yml
```

La integración continua se ejecuta automáticamente al realizar:

- push sobre `main`;
- Pull Request hacia `main`.

También puede ejecutarse manualmente mediante `workflow_dispatch`.

El workflow utiliza:

- Ubuntu;
- Python 3.11.3;
- PostgreSQL 16.

Durante cada ejecución se realizan los siguientes controles:

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py check
python manage.py test
```

Esto permite detectar automáticamente errores de configuración, migraciones pendientes o fallos en las pruebas.

---

# Estructura principal

```text
Educar-para-Trasformar/
│
├── accounts/
├── academic/
├── sports/
├── services/
├── billing/
├── config/
├── static/
├── templates/
├── .github/
│   └── workflows/
├── manage.py
├── requirements.txt
└── README.md
```

---

# Estado actual

Actualmente se encuentran implementados los principales módulos definidos para el sistema:

- autenticación y roles;
- gestión académica;
- profesores y tutores;
- asistencia;
- notas;
- deportes;
- transporte;
- comedor;
- cuotas;
- facturación;
- pagos;
- comprobantes;
- cálculo de deuda;
- reportes administrativos;
- vistas académicas para alumnos y tutores;
- pruebas automatizadas;
- integración continua.

El proyecto continúa en etapa de revisión, mejora visual, documentación y preparación para demostración.
