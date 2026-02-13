import logging
import yaml
import sys
from pathlib import Path

def load_config():
    """Charge la configuration depuis config/config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def setup_logging(config):
    """Configure le logging"""
    log_level = getattr(logging, config['logging']['level'].upper())
    log_file = Path(__file__).parent.parent / config['logging']['file']
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("Kaguya")