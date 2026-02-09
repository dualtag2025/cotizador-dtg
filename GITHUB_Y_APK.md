# 🚀 GUÍA: Subir Proyecto a GitHub y Generar APK

## 📋 PASOS COMPLETOS DESDE CERO

---

## PARTE 1: Crear Repositorio en GitHub

### 1. Ve a GitHub
- Abre https://github.com
- Inicia sesión con tu cuenta

### 2. Crear nuevo repositorio
- Click en el botón verde **"New"** (o el **+** arriba a la derecha → "New repository")
- **Repository name:** `cotizador-dtg`
- **Description:** (opcional) "App móvil para consultar tasas DTG"
- **Privacy:** Elige **Private** (recomendado) o **Public**
- ❌ **NO marques** "Initialize with README"
- Click en **"Create repository"**

### 3. Copiar la URL del repositorio
Verás algo como:
```
https://github.com/TU-USUARIO/cotizador-dtg.git
```
**Cópiala** (la necesitarás en el siguiente paso)

---

## PARTE 2: Descargar el Proyecto en tu Windows

### Opción A: Descargar como ZIP desde GitHub (después de subir)

1. Una vez que subas el proyecto (siguiente sección)
2. Ve a tu repositorio en GitHub
3. Click en el botón verde **"Code"**
4. Click en **"Download ZIP"**
5. Descomprime en `C:\Users\TuNombre\cotizador-dtg\`

### Opción B: Clonar con Git (recomendado)

**Primero instala Git para Windows:**
- Descarga: https://git-scm.com/download/win
- Instalar (siguiente, siguiente, instalar)

**Luego abre PowerShell o Git Bash y ejecuta:**

```bash
cd C:\Users\TuNombre\
git clone https://github.com/TU-USUARIO/cotizador-dtg.git
cd cotizador-dtg
```

---

## PARTE 3: Generar el APK

Una vez que tienes el proyecto en tu Windows:

### 1. Abrir PowerShell en la carpeta del proyecto

```powershell
cd C:\Users\TuNombre\cotizador-dtg\frontend
```

### 2. Instalar dependencias

```powershell
npm install
```

### 3. Instalar EAS CLI (solo primera vez)

```powershell
npm install -g eas-cli
```

### 4. Login en Expo

```powershell
eas login
```

### 5. Generar el APK

```powershell
eas build --platform android --profile preview
```

**Preguntas:**
- "Create project?" → `Y`
- "Android package?" → `ENTER`
- "Generate keystore?" → `Y`

⏱️ **Espera 10-15 minutos**

### 6. Descargar APK

Copia el link que te da (termina en `.apk`) y ábrelo en tu navegador.

---

## 🔄 ALTERNATIVA: Si NO puedes subir el proyecto a GitHub desde aquí

Si el sistema te impide hacer push desde Emergent, puedes:

### Manual Upload (más simple):

1. **Descarga los archivos importantes** usando la vista VS Code de Emergent
2. **Crea la estructura de carpetas** en tu PC:
   ```
   cotizador-dtg/
   ├── frontend/
   │   ├── app/
   │   ├── app.json
   │   ├── eas.json
   │   ├── package.json
   │   └── ...
   └── backend/
       ├── server.py
       ├── requirements.txt
       └── ...
   ```
3. **Copia y pega cada archivo** desde Emergent a tu PC
4. **Sigue desde PARTE 3** para generar el APK

---

## 📦 Archivos Esenciales que DEBES copiar:

### Frontend (/app/frontend):
- ✅ `app.json`
- ✅ `eas.json`
- ✅ `package.json`
- ✅ `.env`
- ✅ Carpeta `app/` (con todos sus archivos)
- ✅ Carpeta `assets/`

### Backend (/app/backend):
- ✅ `server.py`
- ✅ `requirements.txt`
- ✅ `.env`

---

## ❓ Preguntas Frecuentes

**P: ¿Necesito el backend para generar el APK?**
R: No, solo necesitas la carpeta `/frontend`

**P: ¿El APK funcionará sin el backend?**
R: No, necesitas que el backend esté corriendo en:
   `https://mcc-query-tool.preview.emergentagent.com`

**P: ¿Cuánto pesa el APK?**
R: Aproximadamente 50-70 MB

**P: ¿Puedo generar el APK sin cuenta de Expo?**
R: No, EAS Build requiere cuenta (pero es gratis)

---

## 🆘 ¿Problemas?

Si te trabas en algún paso, avísame y te guío en tiempo real.

---

✅ **Una vez que tengas el APK, solo compártelo por WhatsApp/Telegram y listo!**
