import os
from kazoo.client import KazooClient

# Zookeeper IP address
zoo_servers_ip_addr = os.environ['ZOO_SERVERS']

# Initialize a Zookeeper client
zk = KazooClient(hosts=zoo_servers_ip_addr)
zk.start()

paths = ['/'] # Treated as a stack

# Performs a DFS algorithm to recursively find
# different nodes registered with the Zookeeper
while len(paths) > 0:
    # Pop the current path off the stack and print it out
    curr_path = paths.pop()
    print(f'path: {curr_path}')
    
    data, stats = zk.get(curr_path)
    if stats.children_count > 0:
        # Expand the current path (add its child nodes)
        children = zk.get_children(curr_path)
        for ip_addr in children:
            if curr_path == '/':
                paths.append(f'/{ip_addr}')
            else:
                paths.append(f"{curr_path}/{ip_addr}")

# Stop the Zookeeper client
zk.stop()