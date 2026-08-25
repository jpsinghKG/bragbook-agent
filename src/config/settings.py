from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class AppConfig(BaseModel):
    days_since: int = 1


class SourcesConfig(BaseModel):
    git_local: bool = True
    github: bool = True
    linear: bool = True
    user_input: bool = True


class GitLocalConfig(BaseModel):
    roots: list[Path] = []
    identities: list[str] = []


class GithubConfig(BaseModel):
    identities: list[str] = []


class LLMConfig(BaseModel):
    provider: str
    model: str
    max_tokens: int | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="bragbook.toml")

    app: AppConfig = AppConfig()
    sources: SourcesConfig = SourcesConfig()
    git_local: GitLocalConfig = GitLocalConfig()
    github: GithubConfig = GithubConfig()
    llm: LLMConfig

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
    ):
        return (TomlConfigSettingsSource(settings_cls),)
