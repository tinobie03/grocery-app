from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    # Initialize MongoDB connection

    app.config["MONGO_URI"]="mongodb://localhost:27017/accounting_db"
    mongo.init_app(app)
    
    # Define collections
    transactions_collection = mongo.db.transactions
    products_collection = mongo.db.products
    sales_collection = mongo.db.sales
    users_collection = mongo.db.users


