from pydantic import BaseSettings

class Settings(BaseSettings):
    telegram_token: str
    client_key: str
    client_secret: str
    api_host: str

    class Config:
        env_file = ".env"
        

settings = Settings()