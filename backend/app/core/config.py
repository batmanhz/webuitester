import yaml
import os
from pathlib import Path
from pydantic import BaseModel

class ModelConfig(BaseModel):
    provider: str
    name: str
    base_url: str
    api_key: str
    temperature: float = 0.0
    thinking: bool = False
    use_vision: bool = True

class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 19000

class Config(BaseModel):
    model: ModelConfig
    server: ServerConfig = ServerConfig()

def load_config() -> Config:
    # Try to find config.yaml in backend root
    base_dir = Path(__file__).resolve().parent.parent.parent
    config_path = base_dir / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
        
    return Config(**config_data)

settings = load_config()
