from flask import Blueprint, request, jsonify
from app.models.db import mongo

blueprint = Blueprint("products", __name__)

@blueprint.route("/products", methods=["GET"])
def get_products():
    products = mongo.db.products.find()
    return jsonify([{"_id": str(p["_id"]), "name": p["name"], "price": p["price"], "stock": p["stock"]} for p in products])

@blueprint.route("/products", methods=["POST"])
def add_product():
    data = request.json
    mongo.db.products.insert_one(data)
    return jsonify({"message": "Product added successfully"}), 201

@blueprint.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    mongo.db.products.update_one({"_id": product_id}, {"$set": data})
    return jsonify({"message": "Product updated successfully"}), 200

@blueprint.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    mongo.db.products.delete_one({"_id": product_id})
    return jsonify({"message": "Product deleted successfully"}), 200
