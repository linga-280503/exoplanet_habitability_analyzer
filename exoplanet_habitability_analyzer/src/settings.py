import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DB', 'exo_habitability')
TZ = os.getenv('TZ', 'Asia/Kolkata')
