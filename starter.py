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

class Graph:
    g = nx.Graph()
    def add_edge(self, node1, node2):
        self.g.add_edge(node1, node2)
    def getUpdate(self):
        return self.G
    
    #return the graph as a dictionary of lists, key is the node, value is a list of connections
    def getDict(self):
        return nx.to_dict_of_lists(self.g)

'''
    request the unique ID of each node (address) to create the graph. 
    in this version the id is given as an argument but in future will be generated
'''
def clientNodeID(address):
    print("requesting for ID from {}".format(address))
    import socket 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    import json
    s.send(json.dumps({'request':'id'}).encode())
    msg = json.loads(s.recv(10000).decode())
    s.close()
    return msg.get('response')

class Node:
    node = None
    graph = Graph()
    VISITED = False
    lock = False
    def __init__(self):
        self.node = '132.205.9.'+sys.argv[2]
    '''
    request the unique ID of each node (address) to create the graph. 
    in this version the id is given as an argument but in future will be generated
    '''
    def getNodeID(self):
        # TODO for testing the unique ID is changed to primary IP address of each node. 
        return '132.205.9.'+sys.argv[2]

    '''
    return the graph as it is in the networkx format. 

    '''
    def getGraph(self):
        return self.graph

    def updateGraph(self, newGraph):
        nx.Graph.update(self.graph, newGraph)
    
    '''
    create the initial state of the graph for each node based on its neighbors. 
    TODO the neighbors are passed as arguments, must find neighbors automatically. 
    '''
    def neighbors(self):
        neighbor = []
        for items in sys.argv[3:]:
            neighbor.append('132.205.9.'+items)
            self.graph.add_edge(self.getNodeID(), clientNodeID('132.205.9.'+items))
        print(neighbor)
        print(self.graph.g.edges())
        return neighbor

def server(address, n):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = '132.205.9.' + address
    s.bind((address, 8001))
    s.listen()
    while True:
        clientSocket, clientAddress = s.accept()
        address = clientAddress
        print("node {} connected".format(address))
        req = json.loads(clientSocket.recv(10000).decode())
        if req['request'] == 'status':
            print("incoming request for status from ")
            print(address)
            print("****")
            while node.lock:
                pass
            node.lock = True
            clientSocket.send(json.dumps({'response':node.VISITED}).encode())
            node.lock = False
        elif req['request'] == 'id':
            print('incoming request for id from ' + str(address))
            clientSocket.send(json.dumps({'response':node.getNodeID()}).encode())
            node.neighbors()
        elif req['request'] == 'update':
            print('incoming request for update from ')
            print(address)
            print("****")
            #semaphore lock
            while node.lock:
                print('lock')
            node.lock = True
            node.VISITED = True
            callRecursive(address[0], node)
            clientSocket.send(json.dumps({'response': nx.to_dict_of_dicts(n.graph)}).encode())
            node.lock = False
        else:
            clientSocket.send(json.dumps({'response':'bad_request'}).encode())
        clientSocket.close()


def clientNodeStatus(address):
    print("requesting for status from {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'status'}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    return response.get('response')

def clientNodeUpdate(address, node):
    print("outgoing request for update to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'update'}).encode())
    msg = json.loads(s.recv(10000).decode())
    print(msg)
    tmp = nx.from_dict_of_dicts(msg['response'])
    nx.Graph.update(node.graph, tmp)

def callRecursive(node):
    for item in node.neighbors():
        if not clientNodeStatus(item):
            clientNodeUpdate(item, node)


node = Node()
print('neighbors')      
node.VISITED = True

callRecursive(node)
print(nx.to_dict_of_lists(node.graph))