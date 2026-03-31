import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import timezone

load_dotenv()

# Configuramos el contexto para usar Argon2 por defecto
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class HashHelper:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compara la pass que manda el user con el hash de la DB"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Crea el hash 'puré de papa' para guardar en la DB"""
        return pwd_context.hash(password)
    
# Traemos las variables que configuraste
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(data: dict):
    """Crea el token JWT con un tiempo de expiración (UTC-aware)"""
    to_encode = data.copy()
    
    # Obtenemos la hora actual en UTC de forma explícita
    now = datetime.now(timezone.utc)
    
    # Calculamos el momento exacto de la muerte del token
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # El claim 'exp' tiene que ser un timestamp de Unix
    to_encode.update({"exp": expire})
    
    # Firmamos con la SECRET_KEY y el Algoritmo del .env
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt