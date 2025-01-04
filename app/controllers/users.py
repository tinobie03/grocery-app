from flask import Blueprint, request, jsonify
from app.models.db import mongo

blueprint = Blueprint("users", __name__)

@blueprint.route("/users", methods=["GET"])
def get_users():
    users = mongo.db.users.find()
    return jsonify([{"_id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u["role"]} for u in users])

@blueprint.route("/users", methods=["POST"])
def add_user():
    data = request.json
    mongo.db.users.insert_one(data)
    return jsonify({"message": "User added successfully"}), 201

@blueprint.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    mongo.db.users.update_one({"_id": user_id}, {"$set": data})
    return jsonify({"message": "User updated successfully"}), 200

@blueprint.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": user_id})
    return jsonify({"message": "User deleted successfully"}), 200
