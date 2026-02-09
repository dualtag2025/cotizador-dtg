# ========================================
# GUÍA DE DESPLIEGUE EN CPANEL
# Cotizador DTG Backend
# ========================================

## PASO 0: CREAR EL SUBDOMINIO

1. Entra a tu cPanel: https://lidercomputeraqp.com.pe:2083
2. Busca **"Subdominios"** o **"Subdomains"**
3. Crear nuevo subdominio:
   - Subdominio: `api-cotizador-dtg`
   - Dominio: `lidercomputeraqp.com.pe`
   - Raíz del documento: `api-cotizador-dtg` (se autocompleta)
4. Click **"Crear"**

✅ Ahora tienes: `api-cotizador-dtg.lidercomputeraqp.com.pe`

---

## PASO 1: CREAR APLICACIÓN PYTHON EN CPANEL

1. Ve a **"Setup Python App"** o **"Python Selector"**
2. Click en **"+ Create Application"**
3. Configura:
   - **Python version:** 3.11 (o la más reciente)
   - **Application root:** `api-cotizador-dtg`
   - **Application URL:** `api-cotizador-dtg.lidercomputeraqp.com.pe`
   - **Application startup file:** `passenger_wsgi.py`
   - **Application Entry point:** `application`
4. Click **"Create"**

## PASO 2: SUBIR ARCHIVOS

Sube estos archivos a la carpeta `api-cotizador-dtg` que creaste:

```
api-cotizador-dtg/
├── server.py              (el backend principal)
├── passenger_wsgi.py      (archivo de inicio para cPanel)
├── requirements_cpanel.txt (dependencias)
└── .env.production        (configuración - RENOMBRARLO A .env)
```

**IMPORTANTE:** Renombra `.env.production` a `.env` después de subirlo

## PASO 3: INSTALAR DEPENDENCIAS

1. En cPanel, ve a tu aplicación Python
2. Busca la sección "Configuration files" o "Virtual Environment"
3. Haz click en "Run pip install" o usa el terminal:
   ```bash
   source /home/TU_USUARIO/virtualenv/cotizador-api/3.11/bin/activate
   pip install -r requirements_cpanel.txt
   ```

## PASO 4: REINICIAR LA APLICACIÓN

1. En "Setup Python App", busca tu aplicación
2. Click en "Restart"

## PASO 5: VERIFICAR QUE FUNCIONA

Visita: https://api-cotizador-dtg.lidercomputeraqp.com.pe/api/health

Deberías ver:
```json
{"status": "healthy", "timestamp": "..."}
```

## PASO 6: SINCRONIZAR DATOS

1. Primero, haz login como admin:
```bash
curl -X POST https://api-cotizador-dtg.lidercomputeraqp.com.pe/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "206141"}'
```

2. Copia el token que te devuelve

3. Ejecuta la sincronización:
```bash
curl -X POST https://api-cotizador-dtg.lidercomputeraqp.com.pe/api/sync \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

## NOTAS IMPORTANTES

- La base de datos MongoDB ya está configurada en MongoDB Atlas
- El admin por defecto es: usuario `admin`, contraseña `206141`
- Después de sincronizar, la app móvil funcionará con los datos

## SOLUCIÓN DE PROBLEMAS

### Error 500 Internal Server Error
- Revisa los logs en cPanel > Error Log
- Verifica que el archivo .env esté correcto

### Error de conexión a MongoDB
- Verifica que MongoDB Atlas permita conexiones desde cualquier IP (0.0.0.0/0)
- Revisa las credenciales en .env

### La app no responde
- Reinicia la aplicación Python en cPanel
- Verifica que el startup file sea passenger_wsgi.py
