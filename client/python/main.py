import os
import requests
from kazoo.client import KazooClient
from flask import Flask, request, jsonify
from flask_restx import Resource, Api
from threading import Thread

import node_utils
from cache import Cache
from logger import log
from zookeeper_utils import register
from binary_tree import TreeNode, BinaryTree


# Store environment variables for the given node.
node_ip_addr        = os.environ['NODE_ADDRESS']
root_node_ip_addr   = os.environ['ROOT_NODE']
zoo_servers_ip_addr = os.environ['ZOO_SERVERS']

# Flag indicating whether the node is the root
# node of the tree structure or not.
is_root = (node_ip_addr == root_node_ip_addr)

parent_node_ip_addr = None    # IP address of the parent node
root_node           = None    # Root node (used in binary_tree)
binary_tree         = None    # Tree structure used by the tree node (if the node is not the root, binary_tree remains None)
cache               = Cache() # Cache holding node's local values

app = Flask(__name__)
api = Api(app)


@app.route('/get_parent_ip', methods=['PUT'])
def get_parent_ip_from_root():
    # Only the root is allowed to have this endpoint exposed.
    if not is_root:
        return jsonify({'error' : 'The node is not the root node of the tree structure'}), 405
   
    # Retrieve the node's IP address (who is asking for its parent).
    params = request.get_json()
    node_ip_addr = params['node_ip_addr']
    
    # Add the node into the tree structure (parent node is returned).
    # If the node is already there (Flask initializes twice in the debug mode), only
    # the parent node is returned.
    parent_node = binary_tree.add_node(node_ip_addr)
    if parent_node is None:
        log.error('No parent node was found. Exiting...')
        exit()
    
    # Return the IP address of the parent node
    return jsonify({'parent_node_ip_addr' : parent_node.ip_addr}), 200


# This class expose endpoints that allow the user
# to manipulate with the values stored in the local cache.
@api.route('/data')
class DataResource(Resource):
    
    
    @api.doc(
        params = {
            'key': 'Key under which data is stored in the cache'
        },
        responses = {
            200: 'Value was successfully retrieved from the cache',
            204: 'No value was found',
            400: 'Missing the key parameter'
        }
    )
    def get(self):
        # Retrieve the key parameter (?key=...)
        key = request.args.get('key')
        
        # Make sure the key has been provided by the caller.
        if key is None:
            log.error(f'Received HTTP GET /data request with no key')
            return 'Missing the key parameter', 400
        else:
            log.debug(f'Received HTTP GET /data request with key {key}')
            
            # Check if the data can be found in the local cache.
            # If so, return it.
            value = cache.get(key)
            if value is not None:
                return value, 200
            
            # Otherwise, unless the node is the root, ask the parent node for the data.
            if not is_root:
                log.debug(f'No value under key {key} was found locally. Retrieving data from the parent node...')
                
                # Ask the parent node for the data (the caller is blocked).
                value, status_code = node_utils.get_data_from_parent(parent_node_ip_addr, cache, key)
                
                # If the parent provided the data the caller is asking for,
                # update it in the local cache as well.
                if status_code == 200:
                    cache.put(key, value)
                    return value, 200
                else:
                    log.debug(f'No value under key {key} was found in the parent node either')   
            
            return f'No value stored under key {key} was found', 204


    @api.doc(
        params = {
            'key'   : 'Key under which data is stored in the cache',
            'value' : 'Value to be stored in the cache'
        },
        responses = {
            200: 'Value was successfully stored in the cache',
            400: 'At least one of the required parameter is missing'
        }
    )
    def put(self):
        # Retrieve the key parameter from the request (?key=...)
        # and make it is not None.
        key = request.args.get('key')        
        if key is None:
            log.error(f'Received HTTP PUT /data request with no key')
            return 'Missing the key parameter', 400

        # Retrieve the value parameter from the request (?key=...&value=...)
        # and make it is not None.
        value = request.args.get('value')        
        if value is None:
            log.error(f'Received HTTP PUT /data request with no value')
            return 'Missing the value', 400
        
        # Update the data in the local cache.
        log.debug(f'Received HTTP PUT /data request with key {key} and value {value}')
        log.debug(f'Storing value {value} under key {key} into the cache')
        cache.put(key, value)
        
        # Unless the node is the root, asynchronously propagate
        # the update up the tree structure.
        if not is_root:
           log.debug(f'Propagating the value up the tree structure') 
           Thread(target=node_utils.propagate_updated_data, args=(parent_node_ip_addr, key, value, )).start()
        
        return 'The value was successfully stored in the cache', 200
        

    @api.doc(
        params = {
            'key'   : 'Key under which data is stored in the cache',
        },
        responses = {
            200: 'Data was successfully deleted from the cache',
            204: 'No data stored under the given key is stored in the cache',
            400: 'The key parameter is missing'
        }
    )
    def delete(self):
        # Retrieve the key parameter from the request (?key=...)
        # and make sure it is not None.
        key = request.args.get('key')
        if key is None:
            log.error(f'Received HTTP DELETE /data request with no key')
            return 'Missing the key parameter', 400
        else:
            log.debug(f'Received HTTP DELETE /data request with key {key}')
            
            # Try to delete the data from the local cache (it may not be there).
            if cache.delete(key) is True:
                log.debug(f'Data stored under key {key} was successfully deleted from the cache')
                
                # If the data was successfully delete, asynchronously propagate the change up the tree structure.
                if not is_root:
                    Thread(target=node_utils.propagate_deleted_data, args=(parent_node_ip_addr, key, )).start()
                return 'Data was successfully deleted from the cache', 200
            
            return f'No data stored under key {key} was found', 204
            

if __name__ == '__main__':
    # Welcome message.
    log.info('Starting the node')
    
    # Print out environment variables of the node
    log.info(f'node ip addr = {node_ip_addr}')
    log.info(f'root ip addr = {root_node_ip_addr}')
    log.info(f'zoo servers  = {zoo_servers_ip_addr}')
    
    if is_root:
        # If the node is the root, create the tree structure.
        root_node = TreeNode(node_ip_addr)
        binary_tree = BinaryTree(root_node)
        log.info('I am the root of the tree structure')
    else:
        # Else find out who the parent node is.
        parent_node_ip_addr = node_utils.get_parent_ip(root_node_ip_addr, node_ip_addr)
        log.info(f'I am a leaf ({node_ip_addr}) in the tree structure with assigned parent {parent_node_ip_addr}')
        
    # Initialize a Zookeeper client.
    zk = KazooClient(hosts=zoo_servers_ip_addr)
    zk.start()
    
    # Register the node with the Zookeeper.
    register(zk, node_ip_addr, parent_node_ip_addr, is_root)    
    
    # Start the server.
    app.run(host=str(node_ip_addr), debug=True)