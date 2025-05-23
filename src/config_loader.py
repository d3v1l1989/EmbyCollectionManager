import os
import yaml

class ConfigLoader:
    def __init__(self, yaml_path=None):
        self.config = {}
        if yaml_path and os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

    def get(self, key, default=None):
        # Priority: YAML > ENV > default
        if key in self.config:
            return self.config[key]
        return os.getenv(key, default)

    def as_dict(self):
        # Merge ENV and YAML, YAML takes precedence
        merged = dict(os.environ)
        merged.update(self.config)
        return merged

