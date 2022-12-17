import requests
from threading import Lock

from logger import log
    
    
def get_parent_ip(root_node_ip_addr, node_ip_addr):
    try:
        response = requests.put(f'http://{root_node_ip_addr}:5000/get_parent_ip', json={'node_ip_addr' : node_ip_addr})
        if response.status_code == 200:
            data = response.json()
            return data['parent_node_ip_addr']
        else:
            log.error(f'Error when retrieving the parent ip: status code {response.status_code}')
    except Exception as e:
        log.error(f'Error when retrieving the parent ip: {e}')
    return None


def get_data_from_parent(parent_node_ip_addr, cache, key):
    try:
        response = requests.get(f'http://{parent_node_ip_addr}:5000/data', json={'key' : key})
        if response.status_code == 200:
            data = response.json()
            value = data['value']
            cache.put(key, value)
            return value
        return None
    except Exception as e:
        log.error(f'Error when receiving data from the parent node: {e}')
    return None


def propagate_updated_data(parent_node_ip_addr, key, value):
    try:
        response = requests.put(f'http://{parent_node_ip_addr}:5000/data', json={'key' : key, 'value' : value})
        if response.status_code != 200:
            log.error('Failed to update data in the parent node')
    except Exception as e:
        log.error(f'Error when updating data in the parent node: {e}')
        
        
def propagate_deleted_data(parent_node_ip_addr, key):
    try:
        response = requests.delete(f'http://{parent_node_ip_addr}:5000/data', json={'key' : key})
        if response.status_code != 200:
            log.error('Failed to delete data in the parent node')
    except Exception as e:
        log.error(f'Error when deleting data in the parent node: {e}')