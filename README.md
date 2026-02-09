# 📱 Cotizador DTG - App Android

Aplicación móvil para consultar tasas de comisión por tipo de negocio (código CIIU o nombre de giro).

## 🚀 Características

- ✅ Búsqueda por código CIIU
- ✅ Búsqueda por nombre de giro de negocio
- ✅ Autocompletado inteligente
- ✅ Panel de administración (admin/206141)
- ✅ Sincronización con Google Sheets
- ✅ Soporte completo español (áéíóúñ)
- ✅ Funcionamiento offline
- ✅ Tasa Campaña (primeros 3 meses)
- ✅ Tasa Dinámica (desde mes 4)
- ✅ Tasa Pizarra

## 🛠️ Stack Tecnológico

**Frontend:**
- Expo / React Native
- React Navigation
- Axios
- AsyncStorage

**Backend:**
- FastAPI (Python)
- MongoDB
- JWT Authentication

## 📦 Instalación

### Prerequisitos

- Node.js v18+ 
- Python 3.11+
- MongoDB

### Frontend

```bash
cd frontend
npm install
# o
yarn install
```

### Backend

```bash
cd backend
pip install -r requirements.txt
```

## 🔨 Desarrollo

### Iniciar Backend

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Iniciar Frontend

```bash
cd frontend
npx expo start
```

## 📱 Generar APK

### 1. Instalar EAS CLI

```bash
npm install -g eas-cli
```

### 2. Login en Expo

```bash
eas login
```

### 3. Generar APK

```bash
cd frontend
eas build --platform android --profile preview
```

El proceso toma ~10-15 minutos y te dará un link para descargar el APK.

## 🔐 Credenciales Admin

- **Usuario:** admin
- **Contraseña:** 206141

## 📊 Google Sheets

La app sincroniza datos de dos Google Sheets:

1. **Comisión especial 3m** - Códigos CIIU con tasas promocionales
2. **Comisiones por Giro** - Nombres de giros de negocio con tasas

## 🌐 Backend URL

Producción: `https://mcc-query-tool.preview.emergentagent.com`

## 📝 Licencia

Propietario - DTG © 2025

## 👨‍💻 Autor

Desarrollado con ❤️ para DTG
