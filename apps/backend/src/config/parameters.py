from dotenv import load_dotenv
import os

_basedir = os.path.abspath(os.path.dirname('./'))
_env_path = os.path.join(_basedir, '.env')

load_dotenv(dotenv_path=_env_path)

port = os.getenv("MONGO_PORT", "27017")
user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
db_name = os.getenv("MONGO_DB_NAME")
mongo_uri = f"mongodb://{user}:{password}@mongo_db:{port}/{db_name}?authSource=admin"

mongoDBConnection = mongo_uri
