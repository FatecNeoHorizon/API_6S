from dotenv import load_dotenv
import os

_basedir = os.path.abspath(os.path.dirname('./'))
_env_path = os.path.join(_basedir, '.env')

load_dotenv(dotenv_path=_env_path)

def get_mongo_settings():
	host = os.getenv("MONGO_HOST", "mongo_db")
	port = os.getenv("MONGO_PORT", "27017")
	user = os.getenv("MONGO_USER") or os.getenv("MONGO_INITDB_ROOT_USERNAME")
	password = os.getenv("MONGO_PASSWORD") or os.getenv("MONGO_INITDB_ROOT_PASSWORD")
	db_name = os.getenv("MONGO_DB_NAME", "tecsys")

	if not user or not password:
		raise ValueError("Mongo credentials are missing. Set MONGO_USER/MONGO_PASSWORD or MONGO_INITDB_ROOT_USERNAME/MONGO_INITDB_ROOT_PASSWORD.")

	return host, port, user, password, db_name


def get_mongo_uri():
	host, port, user, password, db_name = get_mongo_settings()
	return f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin"

mongoDBConnection = get_mongo_uri()
