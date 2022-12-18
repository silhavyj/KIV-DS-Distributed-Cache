from time import sleep
from kazoo.client import KazooClient

from logger import log

def register(zk : KazooClient, node_ip_addr, parent_node_ip_addr, root=False):
    if root is True:
        # Create the root path for the root node
        # in the Zookeeper structure
        log.info('Registering the root node with the Zookeeper')
        _create_new_path(zk, node_path=f'/{node_ip_addr}')
        return
    
    # If the node is not the root node, retrieve its parent's path
    # in the Zookeeper structure.
    parent_node_path = _get_parent_node_path(zk, node_ip_addr, parent_node_ip_addr)
    
    # Make sure the parent's path was found.
    if parent_node_path is None:
        log.error(f'Parent path of {node_ip_addr} does not exist! Exiting...')
        exit()
        
    # Create a new path in the Zookeeper structure for the node being added.
    _create_new_path(zk, node_path=f'{parent_node_path}/{node_ip_addr}')
    

def _create_new_path(zk : KazooClient, node_path):
    # Make sure the path does not get created more than once.
    if not zk.exists(f'{node_path}'):
        log.info(f'Creating a new node in the Zookeeper structure {node_path}')
        zk.create(f'{node_path}', makepath=True)
    else:
        log.warn(f'Path {node_path} already exists in the Zookeeper structure')
        
        
def _get_parent_node_path(zk : KazooClient, node_ip_addr, parent_node_ip_addr):
    # Wrapper function for _retrieve_parent_node_path
    # It will try to call the method repetitively if it fails to retrieve the
    # parent's node path.
    
    ATTEMPT_COUNT = 4    # How many failed attempts we allow
    SLEEP_PERIOD_SEC = 2 # Number of sleep seconds between each attempt
    
    log.info(f'Finding the parent node path of {node_ip_addr}')
    for index in range(0, ATTEMPT_COUNT):
        log.debug(f'Attempt ({index}) of finding the parent node path of {node_ip_addr}')
        
        # Try to retrieve the parent's node path
        # and return it if the attempt was successful.
        parent_node_path = _retrieve_parent_node_path(zk, node_ip_addr, parent_node_ip_addr)
        if parent_node_path is not None:
            return parent_node_path
        
        # Wait for a few seconds before trying again.
        sleep(SLEEP_PERIOD_SEC)
    
    return None


def _retrieve_parent_node_path(zk : KazooClient, node_ip_addr, parent_node_ip_addr):
    paths = ['/'] # Treated as a queue
    
    # It performs a DFS algorithm to find the path
    # of the parent node.
    while len(paths) > 0:
        log.debug(f'paths = {paths}')
        
        # Pop the current path off the stack.
        curr_path = paths.pop()
        
        # Ask the Zookeeper for the data of the current path.
        data, stat = zk.get(curr_path)
        
        if stat.children_count > 0:
            children = zk.get_children(curr_path)
            
            # Check if the node is one of the current node's children.
            # If so, return the current node (it is the parent).
            if parent_node_ip_addr in children:
                return f'{curr_path}/{parent_node_ip_addr}'
            
            # Expand the current node (add its children into the stack).
            for ip_addr in children:
                if curr_path == '/':
                    paths.append(f'/{ip_addr}')
                else:
                    paths.append(f'{curr_path}/{ip_addr}')
    return None