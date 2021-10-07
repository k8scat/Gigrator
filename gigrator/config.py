"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
import yaml


def load_config(cfg_file: str) -> dict:
    with open(cfg_file, "r") as f:
        cfg = yaml.load(f)

    return cfg
