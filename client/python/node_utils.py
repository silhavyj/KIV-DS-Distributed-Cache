import requests

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
        url = f'http://{parent_node_ip_addr}:5000/data?key={key}'
        log.debug(f'Sending an HTTP GET request to {url}')
        response = requests.get(url)
        return response.text, response.status_code
    except Exception as e:
        log.error(f'Error when receiving data from the parent node: {e}')
    return None, 204


def propagate_updated_data(parent_node_ip_addr, key, value):
    try:
        url = f'http://{parent_node_ip_addr}:5000/data?key={key}&value={value}'
        log.debug(f'Sending an HTTP PUT request to {url}')
        response = requests.put(url)
        if response.status_code != 200:
            log.error('Failed to update data in the parent node')
    except Exception as e:
        log.error(f'Error when updating data in the parent node: {e}')
        
        
#def propagate_deleted_data(parent_node_ip_addr, key):
#    try:
#        response = requests.delete(f'http://{parent_node_ip_addr}:5000/data', json={'key' : key})
#        if response.status_code != 200:
#            log.error('Failed to delete data in the parent node')
#    except Exception as e:
#        log.error(f'Error when deleting data in the parent node: {e}')