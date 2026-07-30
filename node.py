from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from blockchain import Blockchain
from wallet import Wallet

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def get_node_ui():
    return send_from_directory(directory="ui", path="node.html")


@app.route("/network", methods=["GET"])
def get_network_ui():
    return send_from_directory("ui", "network.html")


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_snapshot = blockchain.chain
    chain_snapshot_dict = [block.__dict__.copy() for block in chain_snapshot]
    for block_dict in chain_snapshot_dict:
        block_dict["transactions"] = [
            trx.__dict__ for trx in block_dict["transactions"]
        ]
    return jsonify(chain_snapshot_dict), 200


@app.route("/mine", methods=["POST"])
def add_block():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block["transactions"] = [
            trx.__dict__ for trx in dict_block["transactions"]
        ]
        response = {
            "message": "Adding a block succeeded",
            "block": dict_block,
            "funds": blockchain.get_balance(),
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Adding a block failed",
            "wallet_set_up": wallet.public_key != None,
        }
        return jsonify(response), 500


@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    if wallet.safe_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": blockchain.get_balance(),
        }
        return jsonify(response), 201
    else:
        response = {"message": "Saving keys failed"}
        return jsonify(response), 500


@app.route("/wallet", methods=["GET"])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": blockchain.get_balance(),
        }
        return jsonify(response), 201
    else:
        response = {"message": "Loading keys failed"}
        return jsonify(response), 500


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {"message": "Fetched balance successfully", "balance": balance}
        return jsonify(response), 200
    else:
        response = {
            "message": "Loading of balance failed",
            "wallet_set_up": wallet.public_key != None,
        }
        return jsonify(response), 500


@app.route("/acceptance/transaction", methods=["POST"])
def accept_transaction():
    trx_json = request.get_json();
    if not trx_json:
        return jsonify({"message": "No transaction passed to accept"}), 400
    required_fields = ["sender", "recipient", "amount", "signature"]
    if not all(required_field in trx_json for required_field in required_fields):
        return jsonify({"message": f"Required {required_fields} data is missing"}), 400
    success = blockchain.add_transaction(
        trx_json["sender"],
        trx_json["recipient"],
        trx_json["amount"],
        trx_json["signature"],
        is_receiving=True
    )
    if success:
        response = {
            "message": "Successfully accepted transaction",
            "transaction": {
                "sender": trx_json["sender"],
                "recipient": trx_json["recipient"],
                "amount": trx_json["amount"],
                "signature": trx_json["signature"],
            }
        }
        return jsonify(response), 201
    else:
        return jsonify({"message": "Creating a transaction failed"}), 500


@app.route("/transaction", methods=["POST"])
def add_transaction():
    if wallet.public_key == None:
        return jsonify({"message": "No wallet set up"}), 400
    trx_json = request.get_json()
    if not trx_json:
        return jsonify({"message": "No data found"}), 400
    required_fields = ["recipient", "amount"]
    if not all(field in trx_json for field in required_fields):
        return jsonify({"message": f"Required {required_fields} data is missing"}), 400
    recipient = trx_json["recipient"]
    amount = trx_json["amount"]
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        wallet.public_key, recipient, signature, amount
    )
    if success:
        response = {
            "message": "Successfully added transaction",
            "transaction": {
                "sender": wallet.public_key,
                "recipient": recipient,
                "amount": amount,
                "signature": signature,
            },
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        return jsonify({"message": "Creating a transaction failed"}), 500


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    transactions = blockchain.get_open_transacitions()
    dict_transactions = [trx.__dict__ for trx in transactions]
    return jsonify(dict_transactions), 200


@app.route("/node", methods=["POST"])
def add_node():
    values = request.get_json()
    if not values:
        return jsonify({"message": "No data sent"}), 400
    if "node_url" not in values:
        return jsonify({"message": "No node data found"}), 400
    node = values["node_url"]
    blockchain.add_peer_node(node)
    response = {
        "message": "Node added successfully",
        "all_nodes": blockchain.get_peer_nodes(),
    }
    return jsonify(response), 201


@app.route("/nodes", methods=["GET"])
def get_nodes():
    return jsonify({"all_nodes": blockchain.get_peer_nodes()}), 200


@app.route("/node/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == None or str.isspace(node_url):
        return jsonify({"message": "Invalid node identifier sent"}), 400
    blockchain.remove_peer_node(node_url)
    response = {
        "message": "Node removed successfully",
        "all_nodes": blockchain.get_peer_nodes(),
    }
    return jsonify(response), 200


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    print(f"Running a node on {port}")
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host="0.0.0.0", port=port)
