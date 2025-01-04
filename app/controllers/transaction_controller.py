from flask import Blueprint, request, jsonify
from app.models.db import mongo

blueprint = Blueprint("transactions", __name__)

@blueprint.route("/transactions", methods=["GET"])
def get_transactions():
    transactions = mongo.db.transactions.find()
    return jsonify([t for t in transactions])

@blueprint.route("/transactions", methods=["POST"])
def add_transaction():
    data = request.json
    mongo.db.transactions.insert_one(data)
    return jsonify({"message": "Transaction added"}), 201
