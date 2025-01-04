from flask import Blueprint, request, jsonify
from app.models.db import mongo

blueprint = Blueprint("sales", __name__)

@blueprint.route("/sales", methods=["GET"])
def get_sales():
    sales = mongo.db.sales.find()
    return jsonify([{"_id": str(s["_id"]), "product_id": s["product_id"], "quantity": s["quantity"], "total_price": s["total_price"], "date": s["date"]} for s in sales])

@blueprint.route("/sales", methods=["POST"])
def add_sale():
    data = request.json
    mongo.db.sales.insert_one(data)
    return jsonify({"message": "Sale recorded successfully"}), 201

@blueprint.route("/sales/<sale_id>", methods=["PUT"])
def update_sale(sale_id):
    data = request.json
    mongo.db.sales.update_one({"_id": sale_id}, {"$set": data})
    return jsonify({"message": "Sale updated successfully"}), 200

@blueprint.route("/sales/<sale_id>", methods=["DELETE"])
def delete_sale(sale_id):
    mongo.db.sales.delete_one({"_id": sale_id})
    return jsonify({"message": "Sale deleted successfully"}), 200
