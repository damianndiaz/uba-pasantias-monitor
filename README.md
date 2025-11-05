# 🎓 UBA Pasantías Monitor

Sistema automatizado para monitorear ofertas de pasantías de la Facultad de Derecho de la Universidad de Buenos Aires y recibir notificaciones por email cuando se publiquen nuevas ofertas.

## 📋 Características

- ✅ **Monitoreo automático diario** de la página de pasantías de la UBA
- 🔍 **Detección inteligente** de nuevas ofertas comparando con datos previos
- 📧 **Notificaciones por email** con todos los detalles de las ofertas
- ⚙️ **Configuración personalizable** para horarios y credenciales
- 📊 **Logs detallados** de todas las actividades
- 🔄 **Ejecución manual** para pruebas inmediatas

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.7 o superior
- Conexión a internet
- Cuenta de email (Gmail recomendado)

### Paso 1: Clonar o descargar el proyecto

El proyecto ya está configurado en tu carpeta actual.

### Paso 2: Configurar el entorno Python

El entorno virtual ya está creado y los paquetes instalados:
- requests
- beautifulsoup4  
- schedule
- lxml

### Paso 3: Configurar las credenciales de email

1. **Edita el archivo `config.json`** (se creó automáticamente cuando ejecutaste el sistema)

2. **Para Gmail**, necesitas generar una "Contraseña de aplicación":
   - Ve a tu cuenta de Google → Seguridad
   - Activa la verificación en 2 pasos
   - Genera una contraseña de aplicación
   - Usa esa contraseña en el config.json

3. **Configuración del archivo `config.json`**:
```json
{
  "email_settings": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "tu_email@gmail.com",
    "sender_password": "tu_contraseña_de_aplicacion",
    "sender_name": "UBA Pasantías Monitor"
  },
  "notification_settings": {
    "recipient_email": "tu_email_destino@gmail.com",
    "subject_template": "🎯 Nueva Pasantía UBA Disponible - Oferta #{numero}",
    "send_summary": true,
    "send_individual": true
  },
  "monitoring_settings": {
    "check_frequency_hours": 24,
    "retry_attempts": 3,
    "timeout_seconds": 30
  }
}
```

### Paso 4: Probar el sistema

1. **Prueba el scraper**:
```bash
python scraper.py
```

2. **Prueba el email** (después de configurar):
```bash
python scheduler.py --test-email
```

3. **Ver estado del sistema**:
```bash
python scheduler.py --status
```

## 🚀 Uso

### Ejecución Manual

```bash
# Revisar ofertas una sola vez
python scheduler.py --check

# Ver estado del monitor
python scheduler.py --status

# Enviar email de prueba
python scheduler.py --test-email
```

### Ejecución Automática (Recomendado)

```bash
# Iniciar el monitor automático
python scheduler.py
```

El sistema:
- Revisará la página todos los días a las 9:00 AM
- Te enviará un email cuando encuentre nuevas ofertas
- Seguirá ejecutándose hasta que lo detengas con `Ctrl+C`

### Ejecución en Segundo Plano (Windows)

Para que el monitor se ejecute permanentemente:

1. **Crear un archivo bat** (`iniciar_monitor.bat`):
```batch
@echo off
cd /d "C:\\Users\\HP PROBOOK\\Desktop\\trabajo"
".venv\\Scripts\\python.exe" scheduler.py
```

2. **Programar en el Programador de Tareas de Windows**:
   - Abre "Programador de tareas"
   - Crear tarea básica
   - Ejecutar al inicio del sistema
   - Programa: `iniciar_monitor.bat`

## 📁 Estructura del Proyecto

```
trabajo/
├── .github/
│   └── copilot-instructions.md  # Instrucciones del proyecto
├── .venv/                       # Entorno virtual Python
├── data/
│   ├── ofertas_pasantias.json   # Datos de ofertas (se genera automáticamente)
│   └── last_check.json          # Última revisión exitosa
├── logs/
│   ├── scraper.log              # Logs del web scraper
│   ├── monitor.log              # Logs del monitor principal
│   └── notifications.json       # Historial de notificaciones enviadas
├── scraper.py                   # Módulo de web scraping
├── email_sender.py              # Sistema de notificaciones por email
├── scheduler.py                 # Script principal y programador
├── config.json                  # Configuración (crear y completar)
└── README.md                    # Esta documentación
```

## 📧 Formato de las Notificaciones

Cuando se detecte una nueva oferta, recibirás un email con:

- 📋 **Número de búsqueda**
- 📅 **Fecha de publicación**  
- 🏢 **Área/Departamento**
- 🕐 **Horarios**
- 💰 **Asignación estímulo**
- 📧 **Email de contacto** (si está disponible)
- 🔗 **Enlace para más información**

> **Nota importante**: Los emails de contacto se publican automáticamente 24 horas después de la oferta según las políticas de la UBA.

## ⚠️ Consideraciones Importantes

1. **Respeta la página web**: El sistema hace máximo 1 consulta por día para no sobrecargar el servidor
2. **Emails de aplicación**: La oficina de Pasantías NO recepciona CVs. Envía directamente al email de cada oferta
3. **Contraseñas**: Usa contraseñas de aplicación, no tu contraseña normal de email
4. **Conexión**: Asegúrate de tener conexión estable a internet

## 🔧 Solución de Problemas

### Error: "Configuration not properly set"
- Revisa que completaste todos los campos en `config.json`
- Verifica que no queden valores como "tu_email@gmail.com"

### Error: "Authentication failed"
- Para Gmail: genera y usa una contraseña de aplicación
- Verifica que la verificación en 2 pasos esté activada

### Error: "Failed to fetch page"
- Verifica tu conexión a internet
- La página de la UBA puede estar temporalmente no disponible

### No llegan emails
- Revisa la carpeta de spam
- Verifica la configuración SMTP
- Prueba con `python scheduler.py --test-email`

## 📊 Comandos Útiles

```bash
# Ver todas las opciones
python scheduler.py --help

# Revisar una sola vez
python scheduler.py --check

# Ver estado y estadísticas
python scheduler.py --status

# Probar configuración de email
python scheduler.py --test-email

# Iniciar monitoreo automático
python scheduler.py
```

## 🎯 Página Monitoreada

[UBA Facultad de Derecho - Pasantías](https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php)

## 📝 Logs

El sistema mantiene logs detallados:
- `logs/scraper.log`: Actividad del web scraper
- `logs/monitor.log`: Actividad del monitor principal  
- `logs/notifications.json`: Historial de notificaciones enviadas

## 🤝 Contribuciones

Este proyecto fue desarrollado como una solución personalizada. Si encuentras algún problema o mejora, puedes modificar el código según tus necesidades.

---

**¡Buena suerte con tu búsqueda de pasantías! 🎓✨**