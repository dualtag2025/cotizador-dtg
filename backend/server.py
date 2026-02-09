from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
import pandas as pd
import requests
import io
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'cotizador-dtg-secret-key-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Cotizador DTG API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class AdminLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SheetConfigUpdate(BaseModel):
    comision_especial_url: str
    comisiones_por_giro_url: str

class SheetConfig(BaseModel):
    comision_especial_url: str
    comisiones_por_giro_url: str
    last_sync: Optional[datetime] = None

class SearchResult(BaseModel):
    tipo: str  # 'codigo' or 'nombre'
    valor: str  # The code or business name searched
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    debito_campana: Optional[str] = None
    credito_campana: Optional[str] = None
    debito_dinamica: Optional[str] = None
    credito_dinamica: Optional[str] = None
    debito_pizarra: Optional[str] = None
    credito_pizarra: Optional[str] = None

class AutocompleteResult(BaseModel):
    suggestions: List[str]

class SyncResponse(BaseModel):
    success: bool
    message: str
    records_synced: int
    last_sync: datetime

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ha expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def convert_to_export_url(sheet_url: str) -> str:
    """Convert Google Sheets URL to CSV export URL"""
    # Extract spreadsheet ID and gid
    spreadsheet_pattern = r'/d/([a-zA-Z0-9-_]+)'
    gid_pattern = r'gid=([0-9]+)'
    
    spreadsheet_match = re.search(spreadsheet_pattern, sheet_url)
    gid_match = re.search(gid_pattern, sheet_url)
    
    if not spreadsheet_match:
        raise ValueError("URL de Google Sheet inválida")
    
    spreadsheet_id = spreadsheet_match.group(1)
    gid = gid_match.group(1) if gid_match else '0'
    
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    return export_url

def fetch_sheet_data(sheet_url: str) -> pd.DataFrame:
    """Fetch and parse Google Sheets data"""
    try:
        export_url = convert_to_export_url(sheet_url)
        response = requests.get(export_url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        logger.error(f"Error fetching sheet data: {str(e)}")
        raise ValueError(f"Error al obtener datos del sheet: {str(e)}")

def parse_comision_especial(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Parse Comisión especial 3m sheet (column G from row 14 onwards for CIIU codes)"""
    try:
        # Row 14 is index 13 (0-based)
        df = df.iloc[13:].reset_index(drop=True)
        
        records = []
        
        for _, row in df.iterrows():
            # Skip empty rows (check column G for CIIU code)
            if pd.isna(row.iloc[6]) or str(row.iloc[6]).strip() == '':
                continue
            
            # Get all relevant columns from same row
            record = {
                'codigo': str(row.iloc[6]).strip(),  # Column G - CIIU code
                'tipo': 'codigo',
                'grupo': str(row.iloc[4]).strip() if not pd.isna(row.iloc[4]) else None,  # Column E
                'subgrupo': str(row.iloc[5]).strip() if not pd.isna(row.iloc[5]) else None,  # Column F
                'debito_campana': str(row.iloc[8]).strip() if not pd.isna(row.iloc[8]) else None,  # Column I
                'credito_campana': str(row.iloc[9]).strip() if not pd.isna(row.iloc[9]) else None,  # Column J
            }
            records.append(record)
        
        return records
    except Exception as e:
        logger.error(f"Error parsing comision especial: {str(e)}")
        raise ValueError(f"Error al parsear datos: {str(e)}")

def parse_comisiones_por_giro(df: pd.DataFrame) -> tuple:
    """Parse Comisiones por Giro sheet - returns both name-based and code-based records"""
    try:
        # Row 7 is index 6 (0-based)
        df = df.iloc[6:].reset_index(drop=True)
        
        records_by_name = []  # For name-based searches
        records_by_code = {}  # For code matching with Sheet 1 (dict for faster lookup)
        
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.iloc[4]) or str(row.iloc[4]).strip() == '':
                continue
            
            # Record for name-based search
            record_name = {
                'nombre_giro': str(row.iloc[4]).strip(),  # Column E
                'tipo': 'nombre',
                'grupo': str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else None,  # Column D
                'subgrupo': str(row.iloc[4]).strip() if not pd.isna(row.iloc[4]) else None,  # Column E
                'debito_pizarra': str(row.iloc[5]).strip() if not pd.isna(row.iloc[5]) else None,  # Column F
                'credito_pizarra': str(row.iloc[6]).strip() if not pd.isna(row.iloc[6]) else None,  # Column G
                'debito_dinamica': str(row.iloc[7]).strip() if not pd.isna(row.iloc[7]) else None,  # Column H
                'credito_dinamica': str(row.iloc[8]).strip() if not pd.isna(row.iloc[8]) else None,  # Column I
            }
            records_by_name.append(record_name)
            
            # Also store by code (Column C) for matching with Sheet 1
            codigo = str(row.iloc[2]).strip() if not pd.isna(row.iloc[2]) else None
            if codigo:
                records_by_code[codigo] = {
                    'debito_dinamica': str(row.iloc[7]).strip() if not pd.isna(row.iloc[7]) else None,  # Column H
                    'credito_dinamica': str(row.iloc[8]).strip() if not pd.isna(row.iloc[8]) else None,  # Column I
                }
        
        return records_by_name, records_by_code
    except Exception as e:
        logger.error(f"Error parsing comisiones por giro: {str(e)}")
        raise ValueError(f"Error al parsear datos: {str(e)}")

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database with default data"""
    # Create admin user if not exists
    admin = await db.admin_users.find_one({"username": "admin"})
    if not admin:
        hashed_pwd = hash_password("206141")
        await db.admin_users.insert_one({
            "username": "admin",
            "password": hashed_pwd,
            "created_at": datetime.utcnow()
        })
        logger.info("Admin user created")
    
    # Create default sheet config if not exists
    config = await db.sheet_config.find_one({})
    if not config:
        default_config = {
            "comision_especial_url": "https://docs.google.com/spreadsheets/d/1El9bDW28oNVvbc1rxI7xIgA8oSlMjbbviHHz2r6kJ1A/edit?gid=505615848#gid=505615848",
            "comisiones_por_giro_url": "https://docs.google.com/spreadsheets/d/11lN-AjTmgKrriRHbnyyZ6gewlSvgVcVgx5kQh54nqps/edit?gid=820797387#gid=820797387",
            "last_sync": None
        }
        await db.sheet_config.insert_one(default_config)
        logger.info("Default sheet config created")

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Cotizador DTG API", "version": "1.0.0"}

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: AdminLogin):
    """Admin login endpoint"""
    # Find admin user
    admin = await db.admin_users.find_one({"username": credentials.username})
    
    if not admin or not verify_password(credentials.password, admin['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    # Create access token
    access_token = create_access_token({"sub": credentials.username, "role": "admin"})
    
    return TokenResponse(access_token=access_token)

@api_router.get("/config/sheets", response_model=SheetConfig)
async def get_sheet_config():
    """Get current sheet configuration (public endpoint)"""
    config = await db.sheet_config.find_one({}, {"_id": 0})
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config

@api_router.put("/config/sheets", response_model=SheetConfig)
async def update_sheet_config(
    config_update: SheetConfigUpdate,
    token_data: dict = Depends(verify_token)
):
    """Update sheet URLs (admin only)"""
    # Update configuration
    update_data = {
        "comision_especial_url": config_update.comision_especial_url,
        "comisiones_por_giro_url": config_update.comisiones_por_giro_url
    }
    
    await db.sheet_config.update_one(
        {},
        {"$set": update_data},
        upsert=True
    )
    
    # Get updated config
    config = await db.sheet_config.find_one({}, {"_id": 0})
    return config

@api_router.post("/sync", response_model=SyncResponse)
async def sync_sheets(token_data: dict = Depends(verify_token)):
    """Synchronize data from Google Sheets (admin only)"""
    try:
        # Get sheet URLs
        config = await db.sheet_config.find_one({})
        if not config:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        # Fetch and parse both sheets
        logger.info("Fetching Comisión especial 3m...")
        df1 = fetch_sheet_data(config['comision_especial_url'])
        records1 = parse_comision_especial(df1)
        
        logger.info("Fetching Comisiones por Giro...")
        df2 = fetch_sheet_data(config['comisiones_por_giro_url'])
        records2 = parse_comisiones_por_giro(df2)
        
        # Clear existing data
        await db.codigo_data.delete_many({})
        await db.nombre_data.delete_many({})
        
        # Insert code-based records (from first sheet)
        if records1:
            await db.codigo_data.insert_many(records1)
        
        # Insert name-based records (from second sheet)
        if records2:
            await db.nombre_data.insert_many(records2)
        
        # Update last sync time
        sync_time = datetime.utcnow()
        await db.sheet_config.update_one(
            {},
            {"$set": {"last_sync": sync_time}}
        )
        
        total_records = len(records1) + len(records2)
        logger.info(f"Sync completed: {len(records1)} códigos, {len(records2)} nombres = {total_records} total")
        
        return SyncResponse(
            success=True,
            message="Sincronización completada exitosamente",
            records_synced=total_records,
            last_sync=sync_time
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en sincronización: {str(e)}")

@api_router.get("/autocomplete", response_model=AutocompleteResult)
async def autocomplete_search(q: str):
    """Get autocomplete suggestions for business names"""
    if not q or len(q) < 2:
        return AutocompleteResult(suggestions=[])
    
    # Search in nombre_data collection using regex for partial match
    query = {"nombre_giro": {"$regex": q, "$options": "i"}}
    results = await db.nombre_data.find(query, {"nombre_giro": 1, "_id": 0}).limit(20).to_list(20)
    
    suggestions = [r['nombre_giro'] for r in results]
    return AutocompleteResult(suggestions=suggestions)

@api_router.get("/search/{query}", response_model=SearchResult)
async def search_data(query: str):
    """Search for data by code or business name"""
    query = query.strip()
    
    # Try searching in codigo_data first (by code)
    codigo_result = await db.codigo_data.find_one({"codigo": query}, {"_id": 0})
    
    if codigo_result:
        return SearchResult(
            tipo='codigo',
            valor=codigo_result['codigo'],
            grupo=codigo_result.get('grupo'),
            subgrupo=codigo_result.get('subgrupo'),
            debito_campana=codigo_result.get('debito_campana'),
            credito_campana=codigo_result.get('credito_campana'),
            debito_dinamica=None,
            credito_dinamica=None,
            debito_pizarra=None,
            credito_pizarra=None
        )
    
    # If not found by code, search by business name
    nombre_result = await db.nombre_data.find_one({"nombre_giro": query}, {"_id": 0})
    
    if nombre_result:
        return SearchResult(
            tipo='nombre',
            valor=nombre_result['nombre_giro'],
            grupo=nombre_result.get('grupo'),
            subgrupo=nombre_result.get('subgrupo'),
            debito_campana=None,
            credito_campana=None,
            debito_dinamica=nombre_result.get('debito_dinamica'),
            credito_dinamica=nombre_result.get('credito_dinamica'),
            debito_pizarra=nombre_result.get('debito_pizarra'),
            credito_pizarra=nombre_result.get('credito_pizarra')
        )
    
    # Not found in either collection
    raise HTTPException(
        status_code=404,
        detail="Datos no encontrados"
    )

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
