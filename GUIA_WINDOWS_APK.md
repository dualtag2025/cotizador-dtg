# 📱 GUÍA COMPLETA PARA WINDOWS - Generar APK Cotizador DTG

## ✅ PASO A PASO DESDE CERO

---

## 🔧 PASO 1: Verificar si tienes Node.js instalado

### 1.1 Abrir PowerShell:
- Presiona `Windows + X`
- Selecciona "Windows PowerShell" o "Terminal"
- O busca "PowerShell" en el menú inicio

### 1.2 Verificar Node.js:
Escribe en PowerShell:
```powershell
node --version
```

**Si aparece algo como:** `v18.x.x` o `v20.x.x`
→ ✅ ¡Perfecto! Salta al PASO 2

**Si dice:** "no se reconoce como comando"
→ ⚠️ Necesitas instalarlo (sigue abajo)

---

## 📥 INSTALAR NODE.JS (si no lo tienes)

### Opción A: Descarga directa
1. Ve a: https://nodejs.org/
2. Descarga "LTS" (versión recomendada)
3. Ejecuta el instalador
4. Siguiente → Siguiente → Instalar
5. **Reinicia PowerShell** después de instalar
6. Verifica de nuevo: `node --version`

### Opción B: Usando winget (Windows 11)
```powershell
winget install OpenJS.NodeJS.LTS
```

⏱️ **Tiempo:** 5 minutos

---

## 🚀 PASO 2: Instalar EAS CLI

En PowerShell, ejecuta:

```powershell
npm install -g eas-cli
```

**Verás algo como:**
```
added 459 packages in 54s
```

⏱️ **Tiempo:** 1-2 minutos

---

## 🔑 PASO 3: Login en Expo

### 3.1 Crear cuenta Expo (si no tienes)

Ve a: https://expo.dev/signup

- Usa tu email
- Crea una contraseña
- Verifica tu email

⏱️ **Tiempo:** 2 minutos

### 3.2 Login desde PowerShell

En PowerShell, ejecuta:
```powershell
eas login
```

**Te preguntará:**
```
Email or username: [escribe tu email]
Password: [escribe tu contraseña]
```

**Verás:**
```
✔ Logged in as tu-email@ejemplo.com
```

---

## 📂 PASO 4: Descargar el proyecto

Tienes dos opciones:

### Opción A: Desde Emergent Agent
Si estás usando Emergent Agent, descarga el proyecto completo desde el workspace.

### Opción B: Si ya tienes los archivos
Asegúrate de tener la carpeta `/app/frontend` con todos los archivos.

---

## 🏗️ PASO 5: Navegar a la carpeta del proyecto

En PowerShell, ve a donde descargaste el proyecto:

```powershell
cd C:\ruta\donde\descargaste\app\frontend
```

**Ejemplo:**
```powershell
cd C:\Users\TuNombre\Downloads\app\frontend
```

**Verifica que estás en la carpeta correcta:**
```powershell
ls
```

Deberías ver archivos como:
- app.json
- eas.json
- package.json

---

## 🎯 PASO 6: Instalar dependencias del proyecto

Ejecuta:
```powershell
npm install
```

o si prefieres yarn:
```powershell
yarn install
```

⏱️ **Tiempo:** 2-3 minutos

---

## 🔨 PASO 7: GENERAR EL APK

**¡Este es el comando importante!**

```powershell
eas build --platform android --profile preview
```

### Lo que sucederá:

**Pregunta 1:** 
```
? Would you like to create a project for @tu-usuario/cotizador-dtg?
```
**Responde:** `Y` (presiona Enter)

**Pregunta 2:**
```
? What would you like your Android package to be?
```
**Responde:** Presiona `ENTER` (ya está configurado como com.dtg.cotizador)

**Pregunta 3:**
```
? Would you like to generate a new keystore?
```
**Responde:** `Y` (presiona Enter)

### Verás esto:

```
✔ Build started
✔ Build ID: abc123-def456-ghi789
✔ Build queued...
✔ Build in progress...
```

**⏱️ ESPERA 10-15 MINUTOS**

El proceso se hace en la nube de Expo, no en tu PC.

---

## 📥 PASO 8: Descargar tu APK

Cuando termine, verás:

```
✔ Build finished!

📱 Android app:
https://expo.dev/artifacts/eas/abc123def456.apk

Install and run the app:
• Download from above link
```

### 8.1 Copiar el link
- Copia el link que termina en `.apk`

### 8.2 Descargar
- Pega el link en tu navegador Chrome/Edge
- Se descargará: `cotizador-dtg.apk`

### 8.3 Ubicación
Normalmente en: `C:\Users\TuNombre\Downloads\`

---

## 📤 PASO 9: Compartir el APK

### Opción 1: WhatsApp
1. Abre WhatsApp Web o la app
2. Selecciona el grupo
3. Adjunta el archivo `.apk`
4. Enviar

### Opción 2: Google Drive
1. Sube el `.apk` a Drive
2. Comparte el link con "Cualquiera con el enlace"
3. Envía el link al grupo

### Opción 3: Telegram
1. Arrastra el archivo `.apk` al chat
2. Enviar

---

## 📲 PASO 10: Instalar en Android

### Para ti y tu equipo:

1. **Descargar el APK** en el teléfono Android
2. **Abrir el archivo** (puede estar en Descargas)
3. **Si sale advertencia:**
   - "Instalar aplicaciones desconocidas"
   - Permitir para Chrome/WhatsApp/Archivos
4. **Tocar "Instalar"**
5. **¡Listo!** La app se instalará

---

## 🎉 RESUMEN RÁPIDO

```powershell
# 1. Instalar EAS
npm install -g eas-cli

# 2. Login
eas login

# 3. Ir a carpeta
cd C:\ruta\a\app\frontend

# 4. Instalar dependencias
npm install

# 5. Generar APK
eas build --platform android --profile preview

# 6. Esperar 10-15 min
# 7. Copiar link del APK
# 8. Descargar y compartir
```

---

## ⚠️ PROBLEMAS COMUNES EN WINDOWS

### "node no se reconoce como comando"
**Solución:** Necesitas instalar Node.js desde https://nodejs.org/

### "eas no se reconoce como comando"
**Solución:** 
```powershell
# Reinicia PowerShell después de instalar
npm install -g eas-cli
```

### "No se puede ejecutar scripts"
**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Error de permisos"
**Solución:** Ejecuta PowerShell como Administrador:
- Click derecho en PowerShell → "Ejecutar como administrador"

---

## 📞 ¿Necesitas Ayuda?

Si te trabas en algún paso, avísame exactamente:
1. ¿En qué paso estás?
2. ¿Qué mensaje de error ves?
3. Te guío desde ahí

---

## ✅ CHECKLIST ANTES DE EMPEZAR

- [ ] Tengo Windows 10 u 11
- [ ] Tengo conexión a internet
- [ ] Tengo ~20 minutos disponibles
- [ ] Puedo instalar programas en mi PC
- [ ] Tengo o puedo crear cuenta de email para Expo

---

**🚀 ¡Empieza con el PASO 1!**

Cualquier duda, pregúntame y te ayudo en tiempo real.
