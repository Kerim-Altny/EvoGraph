from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   
    DATABASE_URL: str
    API_NINJAS_KEY: str = ""  # https://api-ninjas.com/profile
    GEMINI_API_KEY: str = ""  # https://aistudio.google.com/app/apikey
    UNSPLASH_ACCESS_KEY: str = ""  # https://unsplash.com/oauth/applications

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



settings = Settings()
