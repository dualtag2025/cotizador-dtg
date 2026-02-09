# 📱 Guía para Generar APK - Cotizador DTG

## ✅ Proyecto YA CONFIGURADO

El proyecto está 100% listo para generar el APK. Solo necesitas seguir estos pasos:

---

## 📋 PASO 1: Instalar EAS CLI

Abre tu terminal y ejecuta:

```bash
npm install -g eas-cli
```

**Tiempo:** ~1 minuto

---

## 📋 PASO 2: Crear Cuenta Expo (si no tienes)

Ve a: https://expo.dev/signup

O crea cuenta directamente desde la terminal en el paso 3.

**Tiempo:** ~2 minutos

---

## 📋 PASO 3: Login en Expo

En tu terminal, ejecuta:

```bash
eas login
```

Te pedirá:
1. **Email o username** (usa el de tu cuenta Expo)
2. **Password**

Si no tienes cuenta, el CLI te dará opción de crear una.

**Tiempo:** ~1 minuto

---

## 📋 PASO 4: Navegar a la carpeta del proyecto

```bash
cd /app/frontend
```

---

## 📋 PASO 5: Generar el APK

Ejecuta este comando:

```bash
eas build --platform android --profile preview
```

**Lo que sucederá:**

1. **Primera vez:** Te preguntará si quieres crear un proyecto en Expo
   - Responde: `Y` (Yes)

2. **Android package name:** Te preguntará el package
   - Ya está configurado: `com.dtg.cotizador`
   - Solo presiona ENTER

3. **Keystore:** Te preguntará sobre certificado
   - Responde: `Y` (deja que Expo lo genere automáticamente)

4. **Build iniciará:** Verás mensajes como:
   ```
   ✔ Build started
   ✔ Build ID: xxxxx-xxxx-xxxx
   ✔ Build queued...
   ```

5. **Espera 10-15 minutos** mientras se compila en la nube

6. **Cuando termine:** Verás un link como:
   ```
   ✔ Build finished!
   📱 Download: https://expo.dev/artifacts/eas/xxxxx.apk
   ```

---

## 📋 PASO 6: Descargar el APK

1. Copia el link que te dio (el que termina en `.apk`)
2. Ábrelo en tu navegador
3. Descargará el archivo: `cotizador-dtg.apk` (~50-70 MB)

---

## 📋 PASO 7: Compartir el APK

Ahora puedes compartir este archivo `.apk` por:
- ✅ WhatsApp
- ✅ Telegram  
- ✅ Email
- ✅ Google Drive
- ✅ Cualquier forma de compartir archivos

**Importante:** Las personas que lo reciban necesitarán:
1. Permitir "Instalar apps de fuentes desconocidas" en Android
2. Simplemente abrir el archivo APK para instalarlo

---

## 🔧 Configuración Actual del APK

**Nombre de la app:** Cotizador DTG
**Package:** com.dtg.cotizador  
**Version:** 1.0.0
**Backend URL:** https://mcc-query-tool.preview.emergentagent.com

**Funcionalidades incluidas:**
✅ Búsqueda por código CIIU
✅ Búsqueda por nombre de giro
✅ Autocompletado
✅ Panel de administración (admin/206141)
✅ Sincronización de Google Sheets
✅ Caracteres especiales en español
✅ Funciona offline después de cargar datos

---

## ⚠️ Notas Importantes

1. **El APK es permanente:** Una vez generado, funciona para siempre
2. **No caduca:** No necesitas pagar nada después
3. **Backend debe estar activo:** La URL actual debe seguir funcionando
4. **Google Sheets:** Deben seguir siendo públicos/accesibles

---

## 🆘 Si tienes problemas

**Error "EXPO_TOKEN":**
- Asegúrate de haber hecho `eas login` correctamente

**Error "Project not found":**
- Es normal la primera vez, responde `Y` cuando pregunte

**Build falla:**
- Revisa que tengas conexión a internet estable
- Intenta de nuevo con el mismo comando

**No puedo instalar el APK:**
- Ve a Ajustes → Seguridad → "Fuentes desconocidas" (activar)
- O "Instalar apps desconocidas" → permitir para tu navegador/WhatsApp

---

## 🔄 Para Actualizar la App en el Futuro

Si necesitas una nueva versión:

1. Cambia la versión en `/app/frontend/app.json`:
   ```json
   "version": "1.0.1"  // o 1.1.0, 2.0.0, etc.
   ```

2. Ejecuta de nuevo:
   ```bash
   eas build --platform android --profile preview
   ```

3. Comparte el nuevo APK

---

## ✅ Checklist Final

Antes de empezar, verifica:
- [ ] Tienes Node.js instalado (v16 o superior)
- [ ] Tienes conexión a internet estable  
- [ ] Tienes ~15-20 minutos disponibles
- [ ] Tienes email para crear cuenta Expo (si no tienes)

---

**¿Listo? Empieza con el PASO 1** 🚀

Cualquier duda durante el proceso, avísame y te ayudo.
