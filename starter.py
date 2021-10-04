import socket
import pickle, json
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import _thread
import subprocess as sp
import hashlib
import _thread
import sys
import json
import time

'''
graph class, in charge of handling the graph not the node. 
the node is the actually entity of the network whilst the
graph is the common sense of the map of the network. 
'''
class Graph():
    g = nx.Graph()

    def add_edge(self, node1, node2):
        print('adding new edge between {} and {}'.format(node1, node2))
        self.g.add_edge(node1, node2)
    
    def getUpdate(self):
        return self.g
    '''
    returns a dictionary of list of the graph. key is the node
    and the value is a list of neighbors {node:[neighbor1, neighbor2, ...]}
    '''
    def getDict(self):
        return nx.to_dict_of_lists(self.g)

'''
returns the unique ID of the node. 
@param: the address of the desired node. 
'''
def reqNodeID(address):
    print("requesting ID from {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'id', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    msg = json.loads(s.recv(10000).decode())
    s.close()
    return msg.get('response')

'''
Node class, is the actual individual entity of the network
which acts independently of other nodes. but gets info through
communication and updates its map, Graph class
graph = new instance of the Graph class above. 
'''
class Node:
    node = None
    graph = Graph() 
    VISITED = False
    lock = False
    parent = None
    neighbors_list = []
    #TODO will be deleted for next version
    def __init__(self):
        self.node = '132.205.9.'+ sys.argv[2]
    
    def getGraph(self):
        return self.graph
    
    def updateGraph(self, newGraph):
        nx.Graph.update(self.graph, newGraph)
    
    def neighbors(self, parent = None ):
        neighbors = []
        for items in sys.argv[3:]:
            if '132.205.9.'+items != parent:
                neighbors.append('132.205.9.'+items)
                ID = reqNodeID('132.205.9.'+ items)
                print('Requested ID from {} is {}, they should be equal!'.format(items, ID))
                self.graph.add_edge(self.node, ID)
            else:
                self.graph.add_edge(self.node, parent)
        self.neighbors_list = neighbors
        return neighbors
        
    clusterID = sys.argv[2]
    clusterSet = False
    clusterCapacity = 5
node = Node()
'''
requesting the status of the node.
@return True/False (str)
returns the status of the desired node. 
@param address: address of the desired node to find out its status
'''
def reqNodeStatus(address):
    print("outgoing request for status to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'status', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    print("*****" + response['response'] + '*********')
    return response['response']
'''
requesting the latest version of the nodes graph (map)
@param address: address of the desired node
@param node: an instance of the local node
'''
def reqNodeUpdate(address, node):
    print("outgoing request for update to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    node.clusterCapacity -= 1
    s.send(json.dumps({'request':'update', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    tmp = nx.from_dict_of_lists(response['response'])
    nx.Graph.update(node.graph.g, tmp)
    print('Graph updated')





def reqClusterStatus(address):
    print("outgoing request for cluster status to {}".format(address))
    print("************\n************\n\t out req cluster stat" + "\n************\n************\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'cluster_status', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    return response['response']


def reqClusterUpdate(address, node):
    print("outgoing request for cluster update to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'cluster', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    node.clusterID = response['response']
    print("************\n************\n\t" + node.clusterID + "\n************\n************\n")

def setClusterID(address, ID):
    print("outgoing request to set cluster ID to {}".format(address))
    print("************\n************\n\t out req set cluster ID" + "\n************\n************\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'set_cluster', 'parent':'132.205.9.'+sys.argv[2], 'value': ID,
                                                'capacity':node.clusterCapacity}).encode()) #TODO check for -1 if needed
    s.close()

def setClusterIDSingle(address, ID):
    print("outgoing request to set cluster ID to {}".format(address))
    print("************\n************\n\t out req set cluster ID" + "\n************\n************\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'set_cluster', 'parent':'132.205.9.'+sys.argv[2], 'value': ID,
                                                'capacity':1}).encode())
    s.close()


def reqNeighborSize(address):
    print("outgoing request for neighbor size to {}".format(address))
    print("************\n************\n\t out req neigh size" + "\n************\n************\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'neighbors', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    s.close()


def callRecursiveCluster(node):
    neighbors_size = {}
    for item in node.neighbors_list:
        neighbors_size[item] = reqNeighborSize(item)
    sorted_neighbors = dict(sorted(neighbors_size.items(), key=lambda item: item[1]))
    sorted_neighbors_list = list(sorted_neighbors.keys())
    neighbor_capacity = {}
    for item in sorted_neighbors_list:
        if neighbors_size[item] > node.clusterCapacity:
            neighbor_capacity[item] = node.clusterCapacity
            break
        elif neighbors_size[item]<=node.clusterCapacity:
            if node.clusterCapacity == 0:
                neighbor_capacity[item] = 0
            neighbor_capacity[item] = neighbors_size[item]
            node.clusterCapacity = node.clusterCapacity - neighbors_size[item]

    for item in node.neighbors_list:
        if reqClusterStatus(item) == 'False':
            tmp = reqNeighborSize(item)
            if tmp > 1:
                reqClusterUpdate(item, node)
            else:
                setClusterIDSingle(item, sys.argv[2])
        else:
            print('{} is already assigned to a cluster'.format(item))




'''
calling the update on all neighbors
@param node: node has a list of all neighbors
    in this version the neighbors are passed as arguments but for future versions it would be discovered
    as a part of neighbor discovery
'''
def callRecursive(node):
    for item in node.neighbors():
        if reqNodeStatus(item) == 'False':

                reqNodeUpdate(item, node)
        else:
            print('{} is already visited'.format(item))

node = Node()  
node.VISITED = True

callRecursive(node)

print('FINAL')
print(nx.to_dict_of_lists(node.graph.g))
nx.draw(node.graph.g)
plt.savefig('fig.png')

callRecursiveCluster(node)
