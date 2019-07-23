import requests
import config as config
import json
import os
import sys
from urllib import parse
# 支持的Git服务器
support = ['gitlab', 'github', 'gitee', 'gitea', 'coding', 'gogs']

# 仓库存放目录
repos_dir = os.getcwd() + '/repos/'
