from time import sleep
from kazoo.client import KazooClient

from logger import log

def register(zk : KazooClient, node_ip_addr, parent_node_ip_addr, root=False):
    if root is True:
        log.info('Registering the root node with the Zookeeper')
        _create_new_path(zk, node_path=f'/{node_ip_addr}')
        return
    
    parent_node_path = _get_parent_node_path(zk, node_ip_addr, parent_node_ip_addr)
    if parent_node_path is None:
        log.error(f'Parent path of {node_ip_addr} does not exist! Exiting...')
        exit()
    _create_new_path(zk, node_path=f'{parent_node_path}/{node_ip_addr}')
    

def _create_new_path(zk : KazooClient, node_path):
    if not zk.exists(f'{node_path}'):
        log.info(f'Creating a new node in the Zookeeper structure {node_path}')
        zk.create(f'{node_path}', makepath=True)
    else:
        log.warn(f'Path {node_path} already exists in the Zookeeper structure')
        
        
def _get_parent_node_path(zk : KazooClient, node_ip_addr, parent_node_ip_addr):
    ATTEMPT_COUNT = 4
    SLEEP_PERIOD_SEC = 2
    
    log.info(f'Finding the parent node path of {node_ip_addr}')
    for index in range(0, ATTEMPT_COUNT):
        log.debug(f'Attempt ({index}) of finding the parent node path of {node_ip_addr}')
        
        parent_node_path = _retrieve_parent_node_path(zk, node_ip_addr, parent_node_ip_addr)
        if parent_node_path is not None:
            return parent_node_path
        
        sleep(SLEEP_PERIOD_SEC)
    
    return None


def _retrieve_parent_node_path(zk : KazooClient, node_ip_addr, parent_node_ip_addr):
    paths = ['/']
    while len(paths) > 0:
        log.debug(f'paths = {paths}')
        curr_path = paths.pop()
        data, stat = zk.get(curr_path)
        
        if stat.children_count > 0:
            children = zk.get_children(curr_path)
            if parent_node_ip_addr in children:
                return f'{curr_path}/{parent_node_ip_addr}'
            
            for ip_addr in children:
                if curr_path == '/':
                    paths.append(f'/{ip_addr}')
                else:
                    paths.append(f'{curr_path}/{ip_addr}')
    return None