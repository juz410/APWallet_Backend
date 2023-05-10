from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    email_username: str
    email_password: str
    email_from: str
    email_smtp_server: str
    email_smtp_port: int
    private_key: str
    public_key: str
    class Config:
        env_file = ".env"

settings = Settings()
