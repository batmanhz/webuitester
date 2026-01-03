from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yaml
from pathlib import Path
from backend.app.core.config import Config, load_config

router = APIRouter()

class ConfigUpdate(BaseModel):
    provider: str
    name: str
    base_url: str
    api_key: str
    temperature: float
    thinking: bool
    headless: bool = False

@router.get("/config")
async def get_config():
    try:
        config = load_config()
        return config.model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_config(config_in: ConfigUpdate):
    try:
        # Load existing config to preserve server settings
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        config_path = base_dir / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            existing_data = yaml.safe_load(f) or {}

        # Update model section
        if "model" not in existing_data:
            existing_data["model"] = {}
            
        existing_data["model"]["provider"] = config_in.provider
        existing_data["model"]["name"] = config_in.name
        existing_data["model"]["base_url"] = config_in.base_url
        existing_data["model"]["api_key"] = config_in.api_key
        existing_data["model"]["temperature"] = config_in.temperature
        existing_data["model"]["thinking"] = config_in.thinking
        
        # Save headless setting if we add it to config later, 
        # currently it's not in ModelConfig but requested in story
        # For now, let's persist it in model config if schema allows, 
        # or just keep it in yaml for future use
        existing_data["model"]["headless"] = config_in.headless

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(existing_data, f, default_flow_style=False)
            
        # Reload settings in memory (optional, depending on how settings object is used)
        # For now, we rely on load_config() reading from file on next request
        # or restart required. 
        # Ideally, we should update the singleton 'settings' object too.
        from backend.app.core.config import settings
        settings.model.provider = config_in.provider
        settings.model.name = config_in.name
        settings.model.base_url = config_in.base_url
        settings.model.api_key = config_in.api_key
        settings.model.temperature = config_in.temperature
        settings.model.thinking = config_in.thinking
        settings.model.headless = config_in.headless
        
        return {"status": "success", "config": existing_data["model"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
