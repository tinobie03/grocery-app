from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app.models.db import init_db
from app.controllers import transaction_controller
from flask import jsonify


app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/accounting_db"
mongo = PyMongo(app)

# Register blueprints and initialize the database
app.register_blueprint(transaction_controller.blueprint)
init_db(app)

@app.route('/')
def dashboard():
    # Fetch data for analytics
    total_items = mongo.db.inventory.count_documents({})
    total_sales = sum(sale['total'] for sale in mongo.db.sales.find())
    total_purchases = sum(purchase['total'] for purchase in mongo.db.purchases.find())
    total_expenses = sum(expense['amount'] for expense in mongo.db.expenses.find())

    return render_template('dashboard.html', 
                           total_items=total_items, 
                           total_sales=total_sales, 
                           total_purchases=total_purchases, 
                           total_expenses=total_expenses)

@app.route('/add_transactions')
def add_transactions():
    # Fetch inventory items
    items = list(mongo.db.inventory.find())
    return render_template('add_transaction.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    # Add a new item to the inventory
    item_name = request.form.get("item_name")
    quantity = request.form.get("quantity")
    price = request.form.get("price")

    if item_name and quantity and price:
        mongo.db.inventory.insert_one({
            "item_name": item_name,
            "quantity": int(quantity),
            "price": float(price)
        })
    return redirect(url_for('add_transactions'))

@app.route('/edit_item/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    try:
        # Convert item_id to ObjectId
        object_id = ObjectId(item_id)
    except Exception as e:
        return f"Invalid item ID: {item_id}", 400

    if request.method == 'POST':
        item_name = request.form.get("item_name")
        quantity = request.form.get("quantity")
        price = request.form.get("price")

        # Update item in MongoDB
        mongo.db.inventory.update_one(
            {"_id": object_id},
            {"$set": {
                "item_name": item_name,
                "quantity": int(quantity),
                "price": float(price)
            }}
        )
        return redirect(url_for('add_transactions'))

    item = mongo.db.inventory.find_one({"_id": object_id})
    if not item:
        return f"Item with ID {item_id} not found", 404

    return render_template('edit_transaction.html', item=item)

@app.route('/delete_item/<item_id>', methods=['GET'])
def delete_item(item_id):
    # Delete an item from the inventory
    mongo.db.inventory.delete_one({"_id": ObjectId(item_id)})
    return redirect(url_for('add_transactions'))

@app.route('/sales_management', methods=['GET', 'POST'])
def sales_management():
    # Fetch all items from inventory for the dropdown
    items = list(mongo.db.inventory.find())
    
    if request.method == 'POST':
        # Handle sale addition
        item_id = request.form.get("item_id")
        quantity = int(request.form.get("quantity"))

        # Fetch item details from inventory
        item = mongo.db.inventory.find_one({"_id": ObjectId(item_id)})
        
        if item and item["quantity"] >= quantity:
            # Calculate total price
            total_price = quantity * item["price"]

            # Insert sale into the sales collection
            mongo.db.sales.insert_one({
                "item_id": item_id,
                "item_name": item["item_name"],
                "quantity": quantity,
                "total": total_price
            })

            # Update inventory to reduce quantity
            mongo.db.inventory.update_one(
                {"_id": ObjectId(item_id)},
                {"$inc": {"quantity": -quantity}}
            )
        else:
            # Handle insufficient stock
            return "Insufficient stock for this sale.", 400

    # Fetch all sales for the page
    sales = list(mongo.db.sales.find())
    return render_template('sales_management.html', items=items, sales=sales)

@app.route('/total_purchases', methods=['GET', 'POST'])
def total_purchases():
    if request.method == 'POST':
        # Get data from form
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        # Calculate total for the purchase
        total = quantity * price

        # Add the new purchase to the database
        mongo.db.purchases.insert_one({
            'item_name': item_name,
            'quantity': quantity,
            'price': price,
            'total': total
        })

        # Redirect to the same page to show the updated list
        return redirect(url_for('total_purchases'))

    # Fetch all purchases from the database
    purchases = list(mongo.db.purchases.find())

    # Calculate total purchases
    total_purchases = sum(purchase['total'] for purchase in purchases)

    # Render the total purchases page with the fetched data
    return render_template('total_purchases.html', purchases=purchases, total_purchases=total_purchases)

@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    # Get data from form
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])

    # Calculate total for the purchase
    total = quantity * price

    # Add the new purchase to the database
    mongo.db.purchases.insert_one({
        'item_name': item_name,
        'quantity': quantity,
        'price': price,
        'total': total
    })

    # Fetch all purchases from the database
    purchases = list(mongo.db.purchases.find())

    # Calculate total purchases
    total_purchases = sum(purchase['total'] for purchase in purchases)

    # Return updated data as JSON response
    return jsonify({
        'item_name': item_name,
        'quantity': quantity,
        'total': total,
        'total_purchases': total_purchases
    })




if __name__ == "__main__":
    app.run(debug=True)
