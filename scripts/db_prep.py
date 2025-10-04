import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database.db import init_db

os.environ["RUN_TIMEZONE_CHECK"] = "0"

load_dotenv()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
