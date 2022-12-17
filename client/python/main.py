import os
import requests
from kazoo.client import KazooClient
from flask import Flask, request, jsonify
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


@app.route('/get_parent_ip', methods=['PUT'])
def get_parent_ip_from_root():
    if not is_root:
        return jsonify({'error' : 'The node is not the root node of the tree structure'}), 405
   
    params = request.get_json()
    node_ip_addr = params['node_ip_addr']
    
    parent_node = binary_tree.add_node(node_ip_addr)
    return jsonify({'parent_node_ip_addr' : parent_node.ip_addr}), 200


@app.route('/data', methods=['GET'])
def get_data():
    params = request.get_json()
    key = params['key']
    value = cache.get(key)
    if value is not None:
        return jsonify({'value' : value}), 200
    
    value = node.get_data_from_parent(parent_node_ip_addr, cache, key)
    if value is not None:
        return jsonify({'value' : value}), 200
    
    return jsonify({'error' : f'no value stored under key {key} was found'}), 400


@app.route('/data', methods=['PUT'])
def add_data():
    params = request.get_json()
    key = params['key']
    value = params['value']
    
    cache.put(key, value)
    if not is_root:
        Thread(target=node.propagate_updated_data, args=(parent_node_ip_addr, key, value, )).start()
    return "", 200


@app.route('/data', methods=['DELETE'])
def delete_data():
    params = request.get_json()
    key = params['key']
    if cache.delete(key):
        return "", 200

    if not is_root:
        node.propagate_deleted_data(parent_node_ip_addr, key)
    return jsonify({'error' : f'there is no value stored under key {key} to be deleted'}), 400


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
        parent_node_ip_addr = node.get_parent_ip(root_node_ip_addr, node_ip_addr)
        log.info(f'I am a leaf ({node_ip_addr}) in the tree structure with assigned parent {parent_node_ip_addr}')
        
    zk = KazooClient(hosts=zoo_servers_ip_addr)
    zk.start()
    register(zk, node_ip_addr, parent_node_ip_addr, is_root)    
    
    app.run(host=str(node_ip_addr), debug=False)