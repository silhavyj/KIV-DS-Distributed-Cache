# KIV/DS - Distributed Cache

<img src="img/01.png">

The goal of this assignment was to implement a distributed cache. The cache is made up of several nodes connected in a binary tree structure. The depth of the tree is defined prior to starting up the containers. Each of the nodes holds its own key-value storage. There are three operations that can be performed on any node.

* `GET <ip> <key>` - Return the value that is stored the given key.
    * If the node holds no such record, it recursively tries to retrieve the data from its parent, leaving the caller temporarily blocked.
    * The look-up does not go beyond the root node.
    * If the matching record is found on the way up the tree structure, all nodes involved in the process get to update their local storage on the way down.
* `PUT <ip> <key> <value>` - Stores the given key-value pair.
    * Updates the local storage
    * The node also sends the update toward the root node, so the nodes can update their local storage as well.
* `DELETE <ip> <key>` - Deletes the value that is stored with the given key.