# Educar Para Transformar

Trabajo Práctico Integrador de **Metodología de Sistemas II – TUP 2026**.

**Integrantes:** Luciano Castillo · Franco Zarate  
**Profesora:** Carolina Vargas

Educar Para Transformar es una solución integral para la gestión de un centro educativo. El proyecto incluye:

- sitio web público;
- sistema web de gestión;
- API REST;
- aplicación móvil Flutter para padres/tutores;
- base de datos PostgreSQL compartida;
- gestión económica y facturación;
- notificaciones automáticas por correo;
- despliegue productivo en Railway;
- integración continua con GitHub Actions.

---

## Estado del proyecto

El proyecto se encuentra funcional y desplegado en producción.

**Web:**  
https://educar-para-trasformar-production.up.railway.app/

La aplicación móvil se conecta al mismo backend y a la misma base de datos que el sistema web, evitando duplicación e inconsistencias de información.

---

## Arquitectura general

```text
Sitio web público
        │
Sistema web Django
        │
        ├───────────────┐
        │               │
     API REST       Administración web
        │               │
        └──────┬────────┘
               │
          PostgreSQL
               │
          Flutter Mobile
               │
       Padres / Tutores

Railway Cron
     │
     └── Procesamiento de notificaciones
               │
             Resend
               │
       Correos + factura PDF
```

La web y la aplicación móvil reutilizan la misma lógica de negocio y persisten la información en una única base PostgreSQL.

---

# Tecnologías utilizadas

## Backend y web

- Python 3
- Django 5.2
- Django REST Framework
- PostgreSQL
- Django ORM
- HTML
- CSS
- Gunicorn
- WhiteNoise
- dj-database-url
- python-dotenv
- psycopg

## Mobile

- Flutter
- Dart
- HTTP
- flutter_secure_storage
- file_picker
- open_filex

## Notificaciones y documentos

- django-anymail
- Resend
- ReportLab

## DevOps

- Git
- GitHub
- GitHub Actions
- Railway
- PostgreSQL administrado
- Railway Volume
- Railway Cron

---

# Componentes del sistema

## 1. Sitio web público

El módulo público permite presentar la institución y recibir información de personas interesadas.

Incluye:

- información institucional;
- niveles educativos;
- noticias;
- galería;
- formulario de contacto;
- solicitudes de inscripción;
- opiniones de visitantes;
- postulaciones de empleo.

Las opiniones son revisadas antes de quedar visibles públicamente.

---

## 2. Accounts

Gestiona autenticación, perfiles y permisos.

Roles:

- Administrador
- Docente
- Alumno
- Padre / Tutor

El backend valida el rol real asociado al usuario. La selección visual de un perfil no concede permisos por sí sola.

---

## 3. Academic

Gestiona:

- niveles educativos;
- cursos;
- alumnos;
- profesores;
- materias;
- horarios;
- dictados;
- tutores;
- relación tutor-alumno;
- asistencia;
- notas.

### Alumnos

El administrador puede:

- registrar alumnos;
- listar;
- modificar;
- realizar baja lógica;
- asignar curso.

Se controla la unicidad de DNI y legajo.

### Profesores

El administrador puede:

- registrar profesores;
- modificar;
- listar;
- desactivar;
- asignar materias, cursos y horarios.

### Asistencia

Los docentes pueden registrar:

- Presente
- Ausente
- Tarde
- Justificado

Se controlan duplicados, fechas futuras, curso correspondiente y permisos del docente.

### Notas

Se administran:

- período;
- evaluación;
- calificación;
- fecha;
- observaciones.

Las calificaciones permitidas se encuentran entre 1 y 10.

---

## 4. Sports

Gestiona:

- deportes;
- grupos deportivos;
- profesores responsables;
- horarios;
- valores mensuales;
- inscripciones.

Reglas principales:

- máximo de dos deportes activos por alumno;
- prevención de inscripciones duplicadas;
- validación de superposición horaria;
- baja lógica para conservar historial.

---

## 5. Services

### Transporte

Permite administrar:

- recorridos;
- valores mensuales;
- contratación por alumno;
- período mensual.

### Comedor

Permite administrar:

- servicios;
- valores;
- contratación por alumno;
- período mensual.

Se evita registrar contrataciones duplicadas para un mismo período.

---

# 6. Billing

Gestiona cuotas, facturación, pagos y comprobantes.

## Cuotas

Permite definir:

- mes;
- año;
- importe;
- vencimiento;
- estado.

## Facturas

Las facturas se generan por alumno y período.

Pueden incluir:

- cuota mensual;
- deportes;
- transporte;
- comedor.

Estados:

- Pendiente
- Parcial
- Pagada
- Vencida
- Anulada

El sistema calcula:

- total facturado;
- total pagado;
- saldo pendiente.

Los valores de cada concepto quedan almacenados en el detalle de la factura para conservar el histórico aunque posteriormente cambien los precios.

---

## Pagos

Los pagos se realizan mediante transferencia bancaria.

Estados:

- Pendiente
- Validado
- Rechazado

Un pago puede aplicarse a uno o más conceptos de una factura.

Validaciones principales:

- importe mayor a cero;
- no superar el saldo disponible;
- conceptos pertenecientes a la misma factura;
- solo pagos validados reducen la deuda;
- un pago rechazado libera nuevamente el saldo;
- una factura puede poseer varios comprobantes.

Formatos de comprobante admitidos:

- PDF
- JPG
- JPEG
- PNG

---

# 7. API REST

La API integra el sistema Django con la aplicación móvil.

Utiliza autenticación por Token y valida tanto el usuario autenticado como la relación entre tutor y alumno.

Principales funcionalidades:

- inicio y cierre de sesión;
- consulta de hijos asociados;
- consulta de facturas;
- resumen financiero;
- historial de deuda;
- historial de pagos;
- registro de transferencias;
- carga de comprobantes;
- descarga protegida de comprobantes.

Un tutor no puede consultar facturas, pagos ni comprobantes de alumnos que no estén asociados a su cuenta.

---

# 8. Aplicación móvil Flutter

La aplicación móvil fue desarrollada para la Parte 3 del Trabajo Práctico Integrador.

Está orientada principalmente a padres y tutores.

## Funcionalidades

- iniciar sesión;
- cerrar sesión;
- listar hijos asociados;
- consultar facturas por hijo;
- consultar cuotas pendientes y pagadas;
- consultar vencimientos;
- consultar importes y estados;
- visualizar resumen financiero;
- consultar historial de deuda;
- consultar historial de pagos;
- seleccionar conceptos a pagar;
- registrar transferencias;
- cargar uno o más comprobantes;
- visualizar comprobantes desde el celular.

## Flujo de pago

```text
Tutor
  ↓
Selecciona hijo
  ↓
Consulta factura
  ↓
Selecciona conceptos
  ↓
Registra transferencia
  ↓
Adjunta comprobante
  ↓
Pago queda PENDIENTE
  ↓
Administrador revisa desde la web
  ↓
Valida o rechaza
  ↓
La información se actualiza en Mobile
```

La aplicación utiliza almacenamiento seguro para el token y separa la sesión local de la sesión de producción mediante variables de entorno.

---

# 9. Reportes administrativos

El sistema dispone de reportes para administradores.

Incluyen:

- ingresos por período;
- pagos completos;
- pagos incompletos;
- facturación y deuda;
- ingresos por deporte;
- pagos por nivel, horario y profesor;
- pagos por recorrido de transporte.

Los ingresos efectivos consideran únicamente pagos validados.

---

# 10. Notificaciones automáticas

Se implementaron los requerimientos RF55 y RF56.

## RF55 — Recordatorio mensual

El último día hábil del mes se envía al tutor:

- alumno;
- período;
- composición de la factura;
- total;
- importe pagado;
- saldo;
- fecha de vencimiento;
- factura PDF adjunta.

## RF56 — Aviso de deuda

El día 20 se envía un aviso a los tutores que todavía poseen saldo pendiente.

El sistema evita enviar la misma notificación más de una vez para la misma factura y tutor.

### Infraestructura

Los correos se envían mediante:

- Resend;
- django-anymail;
- llamadas HTTPS desde Railway.

Un servicio independiente de Railway Cron ejecuta diariamente:

```bash
python manage.py procesar_notificaciones
```

El propio comando decide si corresponde ejecutar RF55, RF56 o finalizar sin enviar notificaciones.

---

# 11. Seguridad

Se aplican controles tanto en la web como en la API.

Ejemplos:

- acceso según rol;
- tutor activo;
- relación tutor-alumno;
- protección de facturas ajenas;
- protección de pagos ajenos;
- comprobantes protegidos mediante endpoints autenticados;
- validación de montos;
- prevención de sobrepagos;
- secretos mediante variables de entorno;
- archivos `.env` excluidos del repositorio;
- HTTPS en producción.

Los archivos `media` no se exponen de forma pública indiscriminada.

---

# 12. Base de datos

El proyecto utiliza PostgreSQL.

En desarrollo puede configurarse mediante variables individuales y en producción mediante `DATABASE_URL`.

Ejemplo de configuración local:

```env
SECRET_KEY=clave-local
DEBUG=True

DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432

TIME_ZONE=America/Argentina/Cordoba
```

Nunca deben publicarse credenciales reales en el repositorio.

---

# 13. Despliegue en producción

El backend está desplegado en Railway.

Servicios principales:

```text
Postgres
Educar-para-Trasformar
notificaciones-cron
```

El despliegue incluye:

- PostgreSQL administrado;
- Gunicorn;
- archivos estáticos con WhiteNoise;
- Volume persistente para comprobantes;
- variables de entorno;
- servicio Cron para notificaciones;
- Resend para correo transaccional.

Dominio:

```text
https://educar-para-trasformar-production.up.railway.app/
```

---

# 14. Instalación local del backend

Clonar el repositorio:

```bash
git clone https://github.com/luciano-castillo/Educar-para-Trasformar.git
cd Educar-para-Trasformar
```

Crear entorno virtual:

```bash
py -m venv .venv
```

Activar en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear el archivo `.env` con las variables locales necesarias.

Aplicar migraciones:

```bash
python manage.py migrate
```

Iniciar Django:

```bash
python manage.py runserver
```

---

# 15. Datos demo

Existe un comando de administración para cargar información de demostración:

```bash
python manage.py cargar_datos_demo
```

El comando genera datos de ejemplo para:

- niveles;
- cursos;
- profesores;
- tutores;
- alumnos;
- materias;
- deportes;
- servicios;
- facturas;
- usuarios demo.

Está diseñado para poder ejecutarse nuevamente sin duplicar las facturas demo ya creadas.

---

# 16. Ejecutar la aplicación móvil

Ingresar al directorio:

```bash
cd mobile
```

Instalar dependencias:

```bash
flutter pub get
```

## Desarrollo local

```bash
flutter run
```

Por defecto la aplicación utiliza:

```text
http://10.0.2.2:8000/api
```

## Ejecutar contra producción

```bash
flutter run --dart-define=APP_ENV=production --dart-define=API_BASE_URL=https://educar-para-trasformar-production.up.railway.app/api
```

---

# 17. Generar APK de producción

```bash
flutter build apk --release --dart-define=APP_ENV=production --dart-define=API_BASE_URL=https://educar-para-trasformar-production.up.railway.app/api
```

El archivo generado se encuentra en:

```text
mobile/build/app/outputs/flutter-apk/app-release.apk
```

El APK fue probado instalándolo de forma independiente en Android y comunicándose directamente con el backend desplegado en Railway.

---

# 18. Pruebas automatizadas

Ejecutar:

```bash
python manage.py test
```

El proyecto cuenta con **157 pruebas automatizadas**.

Las pruebas abarcan, entre otros aspectos:

- modelos y reglas de negocio;
- facturación;
- pagos;
- pagos parciales;
- comprobantes;
- generación de factura PDF;
- cálculo de deuda;
- deportes;
- transporte;
- comedor;
- asistencia;
- notas;
- API REST;
- autenticación;
- roles y permisos;
- privacidad entre tutores y alumnos;
- seguridad;
- reportes;
- notificaciones;
- comandos automáticos;
- integración web / base de datos / API / Mobile.

También se realizaron pruebas manuales del flujo completo en producción.

---

# 19. Integración continua

El proyecto utiliza GitHub Actions.

Workflow:

```text
.github/workflows/django-ci.yml
```

Se ejecuta ante:

- push a `main`;
- Pull Request hacia `main`;
- ejecución manual.

Controles principales:

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py check
python manage.py test
```

---

# 20. Estructura principal

```text
Educar-para-Trasformar/
│
├── accounts/
├── academic/
├── api/
├── billing/
├── services/
├── sports/
├── website/
├── config/
├── mobile/
├── static/
├── templates/
├── media/                  # excluido del repositorio
├── .github/
│   └── workflows/
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── requirements-dev.lock
└── README.md
```

---

# 21. Uso de Inteligencia Artificial

Durante el desarrollo de la Parte 3 se utilizó **ChatGPT** como herramienta de apoyo para:

- análisis de requisitos;
- diseño de integración Web–Mobile;
- aprendizaje de Flutter;
- construcción y revisión de API;
- generación y revisión de pruebas;
- análisis de errores;
- seguridad;
- despliegue;
- Railway;
- notificaciones;
- documentación.

Las soluciones propuestas por IA fueron revisadas, probadas y adaptadas al contexto real del proyecto antes de incorporarlas.

La IA se utilizó como herramienta de asistencia y no como reemplazo del conocimiento, análisis o responsabilidad del desarrollador.

---

# Autores

- **Luciano Castillo**
- **Franco Zarate**

Materia: **Metodología de Sistemas II**  
Profesora: **Carolina Vargas**  
TUP – 2026
