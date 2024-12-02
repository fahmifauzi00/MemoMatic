from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MESOLITICA_API_URL: str = "https://api.mesolitica.com"
    MESOLITICA_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        
settings = Settings()