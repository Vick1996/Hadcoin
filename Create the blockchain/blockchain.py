#Module 1 - Create a blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify

#Part 1 - Building a blockchain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_hash = '0')

    def create_block(self, proof, prev_hash):
             block={'index':len(self.chain)+1,
                    'timestamp': str(datetime.datetime.now()),
                    'proof': proof,
                    'previous_hash':prev_hash}
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
        
# Part 2 - Mining blockchain

# Creating a web app
app = Flask(__name__)

# Creating a blockchain
blockchain = Blockchain()       
        
# Mining new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200               #http Status code : 200 i.e. OK

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
    
# Running app
app.run(host='0.0.0.0', port=5000) #From flask documentation

# Debug for flask
if __name__ == '__main__':
    app.debug = True
    app.run()
    