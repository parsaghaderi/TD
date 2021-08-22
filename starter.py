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
    import json
    s.send(json.dumps({'request':'id'}).encode())
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
    #TODO will be deleted for next version
    def __init__(self):
        self.node = '132.205.9.'+ sys.argv[2]
    
    def getGraph(self):
        return self.graph
    
    def updateGraph(self, newGraph):
        nx.Graph.update(self.graph, newGraph)
    
    def neighbors(self):
        neighbors = []
        for items in sys.argv[3:]:
            neighbors.append('132.205.9.'+items)
            ID = reqNodeID('132.205.9.'+ items)
            print('Requested ID from {} is {}, they should be equal!'.format(items, ID))
            self.graph.add_edge(self.node, ID)
            return neighbors

node = Node()

def server(address, n):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 8001))
    s.listen()

    while(True):
        clientSocket, clientAddress = s.accept()
        address = clientAddress
        print(" node {} is connected.".format(address))

        req = json.loads(clientSocket.recv(10000).decode())
        print('request is {}'.format(req))
        if req['request'] == 'status':
            print("incoming request for status from {}".format(address[0]))
            while node.lock:
                pass
            node.lock = True
            clientSocket.send(json.dumps({'response':node.VISITED}).encode())
            node.lock = False
        elif req['request'] == 'id':
            print('incoming request for id from ' + str(address))
            clientSocket.send(json.dumps({'response':node.node}).encode())
            node.neighbors()
        elif req['request'] == 'update':
            print('incoming request for update from {}'.format(address[0]))
            #semaphore lock
            while node.lock:
                print('lock')
            node.lock = True
            node.VISITED = True
            callRecursive(address[0], node)
            clientSocket.send(json.dumps({'response': nx.to_dict_of_lists(n.graph)}).encode()) #changed
            node.lock = False
        else:
            print('bad request')

def reqNodeStatus(address):
    print("outgoing request for status to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'status'}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    return response.get('response')

def reqNodeUpdate(address, node):
    print("outgoing request for update to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'update'}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    tmp = nx.from_dict_of_lists(response['response'])
    nx.Graph.update(node.graph, tmp)
    print('Graph updated')

def callRecursive(node):
    for item in node.neighbors():
        if not reqNodeStatus(item):
            reqNodeUpdate(item, node)

node = Node()  
node.VISITED = True

callRecursive(node)

print('FINAL')
print(nx.to_dict_of_lists(node.graph))