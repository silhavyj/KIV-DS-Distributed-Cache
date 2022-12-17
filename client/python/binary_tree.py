from threading import Lock

from logger import log


class TreeNode:
        
    def __init__(self, ip_addr, parent_node = None):
        self.nodes = []
        self.ip_addr = ip_addr
        self.parent_node = None        
    
    def has_free_child_spot(self):
        children_count = len(self.nodes)
        return children_count < 2
    
    def assign_child(self, child_node):
        self.nodes.append(child_node)
        

class BinaryTree:
    
    def __init__(self, root_node):
        self._lock = Lock()
        self._root_node = root_node
        
    
    def add_node(self, node_ip_addr):
        with self._lock:
            nodes = [self._root_node]
            while len(nodes) > 0:
                curr_node = nodes.pop(0)
                
                if curr_node.has_free_child_spot():
                    curr_node.assign_child(TreeNode(node_ip_addr, parent_node=curr_node))
                    return curr_node
                
                for node in curr_node.nodes:
                    nodes.append(node)
                    
        return None