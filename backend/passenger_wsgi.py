import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables from .env.production
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.production'))

# Import FastAPI app
from server import app

# cPanel's Passenger needs an 'application' variable
application = app
