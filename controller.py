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
import os
from _thread import *

THREADS = 0
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
    # sending the parent node in json format
    # s.send(json.dumps({'parent':'132.205.9.'+sys.argv[2]}).encode())
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
    #TODO will be deleted for next version
    def __init__(self):
        self.node = '132.205.9.'+ sys.argv[2]
    
    def getGraph(self):
        return self.graph
    
    def updateGraph(self, newGraph):
        nx.Graph.update(self.graph, newGraph)
    
    def neighbors(self, parent):
        print("requesting ID from the neighbors")
        neighbors = []
        for items in sys.argv[3:]:
            if '132.205.9.'+items != parent:
                neighbors.append('132.205.9.'+items)
                ID = reqNodeID('132.205.9.'+ items)
                print('Requested ID from {} is {}, they should be equal!'.format(items, ID))
                self.graph.add_edge(self.node, ID)
            else:
                self.graph.add_edge(self.node, parent)
        return neighbors

node = Node()

# def server(address, node):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind((address, 8001))
#     s.listen(20)

#     while(True):
#         clientSocket, clientAddress = s.accept()
#         address = clientAddress
#         print(" node {} is connected.".format(address))  

#         while node.lock:
#             print('waiting')
#             time.sleep(0.3)    
#         node.lock = True

#         req = json.loads(clientSocket.recv(10000).decode())
#         node.parent = req['parent']   
#         print(req['parent'])
#         print('request is {}'.format(req))
#         if req['request'] == 'status':
#             print("incoming request for status from {}".format(address[0]))
#             clientSocket.send(json.dumps({'response':node.VISITED}).encode())
#         elif req['request'] == 'id':
#             print('incoming request for id from ' + str(address))
#             clientSocket.send(json.dumps({'response':node.node}).encode())
#             print('response to id request from '+ str(address) + ' was sent')
            
#             # node.neighbors()
#         elif req['request'] == 'update':
#             print('incoming request for update from {}'.format(address[0]))
#             #semaphore lock
#             # while node.lock:
#             #     print('lock')
#             # node.lock = True
#             node.VISITED = True
#             callRecursive(node)
#             clientSocket.send(json.dumps({'response': nx.to_dict_of_lists(node.graph)}).encode()) #changed
#             print('response to update request from '+str(address) + ' was sent')
#             # node.lock = False
#         else:
#             print('bad request')
#         node.lock = False
def threaded_client(clientSocket, clientAddress, node):
    req = json.loads(clientSocket.recv(10000).decode())
    node.parent = req['parent']

    if req['request'] == 'status':
            print("incoming request for status from {}".format(clientAddress[0]))
            if node.VISITED == True:
                clientSocket.send(json.dumps({'response':'True'}).encode())
            else:
                clientSocket.send(json.dumps({'response':'False'}).encode())
            print("response to status request was sent to {}".format(clientAddress[0]))

    elif req['request'] == 'id':
        print('incoming request for id from ' + format(clientAddress[0]))
        clientSocket.send(json.dumps({'response':node.node}).encode())
        print('response to id request was sent to '+ format(clientAddress[0]))

    elif req['request'] == 'update':
        print('incoming request for update from {}'.format(format(clientAddress[0])))
        node.VISITED = True
        callRecursive(node)
        clientSocket.send(json.dumps({'response': nx.to_dict_of_lists(node.graph.g)}).encode()) #changed
    else:
        print('bad request')
    clientSocket.close()
    print('connection from {} for - {} - request is closed'.format(clientAddress[0], req['request']))

def server(address, node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 8001))
    s.listen(20)

    while True:
        clientSocket, clientAddress = s.accept()
        print(" node {} is connected.".format(str(clientAddress))) 
        start_new_thread(threaded_client, (clientSocket, clientAddress, node))
        

def reqNodeStatus(address):
    print("outgoing request for status to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    # sending the parent node in json format
    # s.send(json.dumps({'parent':sys.argv[2]}).encode())
    s.send(json.dumps({'request':'status', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    print("*****" + response['response'] + '*********')
    return response['response']

def reqNodeUpdate(address, node):
    print("outgoing request for update to {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    # sending the parent node in json format
    # s.send(json.dumps({'parent':sys.argv[2]}).encode())
    s.send(json.dumps({'request':'update', 'parent':'132.205.9.'+sys.argv[2]}).encode())
    response = json.loads(s.recv(10000).decode())
    print(response)
    s.close()
    tmp = nx.from_dict_of_lists(response['response'])
    nx.Graph.update(node.graph, tmp)
    print('Graph updated')

def callRecursive(node):
    for item in node.neighbors(node.parent):
        if item != node.parent:
            if reqNodeStatus(item) == 'False':
                reqNodeUpdate(item, node)
            else:
                print('{} is already visited'.format(item))
        else:
            print('{} can\'t send request to parent node {}'.format(item, node.parent))



server('132.205.9.'+sys.argv[1], node)

