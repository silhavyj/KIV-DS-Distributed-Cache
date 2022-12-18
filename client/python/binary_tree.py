from threading import Lock

from logger import log


class TreeNode:
        
    def __init__(self, ip_addr, parent_node = None):
        self.nodes = []          # Child nodes
        self.ip_addr = ip_addr   # IP address of the node
        self.parent_node = None  # Reference to the parent node 
    
    
    def has_free_child_spot(self):
        # We are considering a binary tree - max 2 children.
        children_count = len(self.nodes)
        return children_count < 2 
    
    
    def assign_child(self, child_node):
        # The caller needs to make sure that the node
        # has not exceeded the maximum number of children (2).
        self.nodes.append(child_node)
        

class BinaryTree:
    
    def __init__(self, root_node):
        self._lock = Lock()         # For mutual exclusion
        self._root_node = root_node # Root node of the tree structure
        
    
    def add_node(self, node_ip_addr):
        # It performs a BFS algorithm to find 
        # the next free spot in the tree structure.
        with self._lock:
            nodes = [self._root_node] # Treated as a queue
            
            while len(nodes) > 0:
                # Retrieve the current node
                curr_node = nodes.pop(0)
                
                # Expand its children (add them to the queue as well)
                for node in curr_node.nodes:
                    # If the node is already in the tree structure,
                    # do not add it again, just return the parent node.
                    if node.ip_addr == node_ip_addr:
                        return curr_node
                    nodes.append(node)
                
                # If the current node has a free spot (has either 0 or 1 child),
                # assign it the node as its new child and return the parent (current node).
                if curr_node.has_free_child_spot():
                    curr_node.assign_child(TreeNode(node_ip_addr, parent_node=curr_node))
                    return curr_node
                    
        return None