#Module 2 - Create a cryptocurrency
#requests==2.18.4 : pip install

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Part 1 - Building a blockchain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions=[] #List of transactions before adding to the block
        self.create_block(proof=1, prev_hash = '0')
        self.nodes = set()

    def create_block(self, proof, prev_hash):
             block={'index':len(self.chain)+1,
                    'timestamp': str(datetime.datetime.now()),
                    'proof': proof,
                    'previous_hash':prev_hash,
                    'transactions': self.transactions}
             self.transactions=[]
             self.chain.append(block)
             return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof=True
            else:
                new_proof+=1
        return new_proof 
    
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        index = 1
        while index < len(chain):
            block = chain[index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof= previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            index+=1
        return True
        
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({'sender':sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
           response = requests.get(f'http://{node}/get_chain') #F string syntax
           if response.status_code == 200:
              length = response.json()['length']
              chain = response.json()['chain']
              if length > max_length and self.is_chain_valid(chain):
                  max_length = length
                  longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
           
# Part 2 - Mining blockchain

# Creating a web app
app = Flask(__name__)

#Creating an address for the node on port 5000
node_address = str(uuid4()).replace('-','')   #uuid4 will create a random but unique address
 
# Creating a blockchain
blockchain = Blockchain()       
        
# Mining new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'You', amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200 #http Status code : 200 i.e. OK

# Getting the full blockchain
@app.route('/get_chain',methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200
    
# Check if block is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    flag = blockchain.is_chain_valid(blockchain.chain)
    if flag==True:
        response = {'message': 'All good, blockchain is valid'}
    else:
        response={'message': 'Houston, we have a problem! The blockchain is not valid'}
    return jsonify(response), 200
    
#Adding a new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of transaction are missing', 400 #HTTP response for bad request
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {'message': f'This transaction will be added to the Block {index}'}
    return jsonify(response), 201

#Part 3 : Decentralizing a blockchain

#Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are connected. The Hadcoin blockchain now contains the following list:',
                'total_nodes': list(blockchain.nodes) }
    return jsonify(response), 201
    

#Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced==True:
        response = {'message': 'The nodes had different chains,so chain was replaced by the longer chain',
                    'new_chain': blockchain.chain}
    else:
        response={'message': 'All good. The chain is the largest one.',
                  'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running app
app.run(host='0.0.0.0', port=5003) #From flask documentation

# Debug for flask
if __name__ == '__main__':
    app.debug = True
    app.run()
    