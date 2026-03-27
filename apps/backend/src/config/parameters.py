from dotenv import load_dotenv
import os

_basedir = os.path.abspath(os.path.dirname('./'))
_env_path = os.path.join(_basedir, '.env')

load_dotenv(dotenv_path=_env_path)

mongoDBConnection = os.getenv('mongoDBConnection')
