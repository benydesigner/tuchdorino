from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://user:password@localhost/vehicle_db' # Example URL
    SECRET_KEY: str = 'your_secret_key' # For JWT
    ALGORITHM: str = 'HS256' # For JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # For JWT

    class Config:
        env_file = '.env' # If you want to use a .env file

settings = Settings()
