"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
import yaml

# https://pyyaml.org/wiki/PyYAMLDocumentation
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def load_config(cfg_file: str) -> dict:
    with open(cfg_file, "r") as f:
        cfg = yaml.load(f, Loader=Loader)

    return cfg
