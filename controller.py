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
class Node:
    graph = nx.Graph()
    VISITED = False
    lock = False
    
    #TODO store this in variable so we don't calculate it each time.
    def getNodeID(self):
        digest = ''
        for items in sp.getoutput('ip link show').split('\n')[1::2]:
            digest+=hashlib.sha256(items.split()[-3].encode()).hexdigest()
        return hashlib.sha256(digest.encode()).hexdigest()
    
    def getGraph(self):
        return self.graph

    def updateGraph(self, newGraph):
        self.graph = nx.Graph.update(self.graph, newGraph)
    
    def neighbors(self):
        #TODO this is for local test only
        neighbor = []
        # for items in sp.getoutput('ip -4 neighbor').split('\n'):
        #     if items.split()[0][:8] == '132.205.' and items.split()[3] != 'FAILED':
        #         neighbor.append(items.split()[0])
        for items in sys.argv[2:]:
            neighbor.append('132.205.9.'+items)
        return neighbor

node = Node()
print(nx.to_dict_of_dicts(node.graph))

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
            print('incoming request for status from '+ address)
            clientSocket.send(json.dumps({'response':node.VISITED}).encode())
        elif req['request'] == 'id':
            print('incoming request for id from ' + address)
            clientSocket.send(json.dumps({'response':node.getNodeID()}).encode())
        elif req['request'] == 'update':
            print('incoming request for update from ' + address)
            #semaphore lock
            while node.lock:
                pass
            node.lock = True
            node.VISITED = True
            callRecursive(address, node)
            clientSocket.send(json.dumps({'response': n.neighbors()}).encode())
            node.lock = False
        else:
            clientSocket.send(json.dumps({'response':'bad_request'}).encode())
        clientSocket.close()

def clientNodeID(address):
    print("requesting for id from {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'id'}).encode())
    print(json.loads(s.recv(10000).decode()))
    s.close()

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
    print("outgoing request for update from {}".format(address))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 8001))
    s.send(json.dumps({'request':'update'}).encode())
    msg = json.loads(s.recv(10000).decode())
    print(msg)
    tmp = nx.from_dict_of_dicts(msg['response'])
    nx.Graph.update(node.graph, tmp)

def callRecursive(parent, node):
    for item in node.neighbors():
        if item != parent:
            if not clientNodeStatus(item):
                clientNodeUpdate(item, node)
            
            

server(sys.argv[1], node)