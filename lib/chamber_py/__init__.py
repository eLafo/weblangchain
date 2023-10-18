import os
import yaml
import glob
from pathlib import Path
from deepmerge import always_merger
from dotenv import load_dotenv

class Chamber:
    settings = {}
        
    @classmethod
    def _load_settings(cls, dict):
        always_merger.merge(cls.settings, dict)

    @classmethod
    def _load_from_yaml(cls, file_path):
        with open(file_path, 'r') as f:
            settings = yaml.safe_load(f)
            if settings:
                cls._load_settings(settings)
            
    @classmethod
    def _override_with_env(cls):
        load_dotenv()
        def _update_with_env(d, keys):
            for k, v in d.items():
                if isinstance(v, dict):
                    _update_with_env(v, keys + [k])
                else:
                    env_key = '_'.join(keys + [k]).upper()
                    if env_key in os.environ:
                        d[k] = os.environ[env_key]

        _update_with_env(cls.settings, [])

    @classmethod
    def reset(cls):
        cls.settings = {}
        
    @classmethod
    def load(cls, settings_folder=Path("config/settings")):
        environment = os.environ.get('LANGCHAIN_ENVIRONMENT', 'development')

        config_folder = Path("config")
        precedence_order = [
            f"{config_folder}/settings.yaml",
            f"{config_folder}/settings.{environment}yaml",
            f"{config_folder}/settings.local.yaml"
        ]

        settings_folder = Path(f"{config_folder}/settings")
        if settings_folder.exists() and settings_folder.is_dir():

            precedence_order.extend([
                f"{config_folder}/settings/*.yaml",
                f"{config_folder}/settings/*.{environment}.yaml",
                f"{config_folder}/settings/*.local.yaml"
            ])
                    
        # Load settings from all YAML files in the 'config/settings' folder based on precedence
        # settings_folder = Path("config/settings")
        for pattern in precedence_order:
            
            for yaml_file in glob.glob(pattern):
                cls._load_from_yaml(yaml_file)
                
        # Override settings from environment variables
        cls._override_with_env()

    @classmethod
    def reload(cls):
        cls.reset()
        cls.load()

    def __init__(self):
        self.load()

    def __getitem__(self, key):
        return self.settings.get(key, None)
