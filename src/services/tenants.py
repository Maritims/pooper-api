import os
from typing import List
from fastapi import Request
import yaml


def get_tenants() -> List[str]:
    if os.path.exists('/var/pooper/conf/tenants.yaml') is False:
        return []
        
    with open('/var/pooper/conf/tenants.yaml') as file:
        tenants = yaml.load(file, Loader=yaml.FullLoader)
        return tenants['tenants']


def get_tenant(request: Request) -> str:
    database = 'pooper'
    
    # Get db from hostname.
    if request.base_url.hostname.find('.') != -1:
        database = request.base_url.hostname.split('.')[0]

    # Get db from headers.
    if 'HTTP_X_DATABASE' in request.headers:
        database = request.headers['HTTP_X_DATABASE']

    return database
    

def is_valid_tenant(tenant: str) -> bool:
    return tenant in get_tenants()
