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


node_ip_addr        = os.environ['NODE_ADDRESS']
root_node_ip_addr   = os.environ['ROOT_NODE']
zoo_servers_ip_addr = os.environ['ZOO_SERVERS']

is_root = (node_ip_addr == root_node_ip_addr)

parent_node_ip_addr = None
root_node           = None
binary_tree         = None
cache               = Cache()

app = Flask(__name__)
api = Api(app)


@app.route('/get_parent_ip', methods=['PUT'])
def get_parent_ip_from_root():
    if not is_root:
        return jsonify({'error' : 'The node is not the root node of the tree structure'}), 405
   
    params = request.get_json()
    node_ip_addr = params['node_ip_addr']
    
    parent_node = binary_tree.add_node(node_ip_addr)
    return jsonify({'parent_node_ip_addr' : parent_node.ip_addr}), 200


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
        key = request.args.get('key')
        if key is None:
            log.error(f'Received HTTP GET /data request with no key')
            return 'Missing the key parameter', 400
        else:
            log.debug(f'Received HTTP GET /data request with key {key}')
            value = cache.get(key)
            if value is not None:
                return value, 200
            
            if not is_root:
                log.debug(f'No value under the key {key} was found locally. Retrieving data from the parent node...')
                value, status_code = node_utils.get_data_from_parent(parent_node_ip_addr, cache, key)
                if status_code == 200:
                    cache.put(key, value)
                    return value, 200
                else:
                    log.debug(f'No value under the key {key} was found in the parent node either')   
            
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
        key = request.args.get('key')        
        if key is None:
            log.error(f'Received HTTP PUT /data request with no key')
            return 'Missing the key parameter', 400

        value = request.args.get('value')        
        if value is None:
            log.error(f'Received HTTP PUT /data request with no value')
            return 'Missing the value', 400
        
        log.debug(f'Received HTTP PUT /data request with key {key} and value {value}')
        log.debug(f'Storing value {value} under key {key} into the cache')
        cache.put(key, value)
        
        if not is_root:
           log.debug(f'Propagating the value up the tree structure') 
           Thread(target=node_utils.propagate_updated_data, args=(parent_node_ip_addr, key, value, )).start()
        
        return 'The value was successfully stored in the cache', 200
        

#@app.route('/data', methods=['DELETE'])
#def delete_data():
#    params = request.get_json()
#    key = params['key']
#    if cache.delete(key):
#        return "", 200
#
#    if not is_root:
#        node_utils.propagate_deleted_data(parent_node_ip_addr, key)
#    return jsonify({'error' : f'there is no value stored under key {key} to be deleted'}), 400


if __name__ == '__main__':
    log.info('Starting the node')
    
    log.info(f'node ip addr = {node_ip_addr}')
    log.info(f'root ip addr = {root_node_ip_addr}')
    log.info(f'zoo servers  = {zoo_servers_ip_addr}')
    
    if is_root:
        root_node = TreeNode(node_ip_addr)
        binary_tree = BinaryTree(root_node)
        log.info('I am the root of the tree structure')
    else:
        parent_node_ip_addr = node_utils.get_parent_ip(root_node_ip_addr, node_ip_addr)
        log.info(f'I am a leaf ({node_ip_addr}) in the tree structure with assigned parent {parent_node_ip_addr}')
        
    zk = KazooClient(hosts=zoo_servers_ip_addr)
    zk.start()
    register(zk, node_ip_addr, parent_node_ip_addr, is_root)    
    
    app.run(host=str(node_ip_addr), debug=True)