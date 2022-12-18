import json
import requests

from logger import log
    
    
def get_parent_ip(root_node_ip_addr, node_ip_addr):
    try:
        # Send an HTTP GET request to the root node to 
        # retrieve the IP address of the parent node.
        response = requests.put(f'http://{root_node_ip_addr}:5000/get_parent_ip', json={'node_ip_addr' : node_ip_addr})
        if response.status_code == 200:
            data = response.json()
            
            # Return the IP address to the caller.
            return data['parent_node_ip_addr']
        else:
            log.error(f'Error when retrieving the parent ip: status code {response.status_code}')
    except Exception as e:
        log.error(f'Error when retrieving the parent ip: {e}')
    return None


def get_data_from_parent(parent_node_ip_addr, cache, key):
    try:
        # Ask the parent node for its data stored under the given key.
        # If the parent does not have the data in its cache, it will
        # ask its parent and so forth. The root node is the last node
        # up the chain of calls.
        url = f'http://{parent_node_ip_addr}:5000/data?key={key}'
        log.debug(f'Sending an HTTP GET request to {url}')
        response = requests.get(url)
        
        # Return the value (may be None) along with the status code.
        return eval(response.text).strip(), response.status_code
    except Exception as e:
        log.error(f'Error when receiving data from the parent node: {e}')
    return None, 204


def propagate_updated_data(parent_node_ip_addr, key, value):
    try:
        # Send the update (PUT) to the parent node, so it can update its local cache.
        url = f'http://{parent_node_ip_addr}:5000/data?key={key}&value={value}'
        log.debug(f'Sending an HTTP PUT request to {url}')
        response = requests.put(url)
        if response.status_code != 200:
            log.error('Failed to update data in the parent node')
    except Exception as e:
        log.error(f'Error when updating data in the parent node: {e}')
        
        
def propagate_deleted_data(parent_node_ip_addr, key):
    try:
        # Send the update (DELETE) to the parent node, so it can update its local cache.
        url = f'http://{parent_node_ip_addr}:5000/data?key={key}'
        log.debug(f'Sending an HTTP DELETE request to {url}')
        response = requests.delete(url)
        if response.status_code != 200:
            log.error('Failed to delete data in the parent node')
    except Exception as e:
        log.error(f'Error when deleting data in the parent node: {e}')