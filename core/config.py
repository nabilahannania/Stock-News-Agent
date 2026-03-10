from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    TAVILY_API_KEY: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


APPSetting = Settings()
