from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models import Product, ProductInventory
import requests
import os
import csv

bp = Blueprint('main', __name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        organization = request.form['organization']
        # Add your login logic here
        return redirect(url_for('main.marketplaces'))
    return render_template('authorization.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        organization = request.form['organization']
        # Add your registration logic here
        return redirect(url_for('main.marketplaces'))
    return render_template('registartion.html')

@bp.route('/marketplaces')
def marketplaces():
    return render_template('marketplaces.html')

@bp.route('/products')
def products():
    data = Product.query.all()
    return render_template('products.html', data=data)

@bp.route('/fetch', methods=['POST'])
def fetch_data():
    data = request.get_json()
    api_key = data.get('apiKey')
    if not api_key:
        return jsonify({"error": "API Key is required"}), 400

    try:
        api_data = fetch_data_from_api(api_key)
        insert_data_into_db(api_data)
        return redirect(url_for('main.products'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            process_csv(filepath)
            flash('File successfully uploaded and processed')
            return redirect(url_for('main.products'))
    return render_template('mywarehouse.html')

def process_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Assuming the CSV has columns: supplierArticle, subject, brand, category, quantity
            product = Product(
                supplierArticle=row['supplierArticle'],
                subject=row['subject'],
                brand=row['brand'],
                category=row['category'],
                quantity=int(row['quantity'])
            )
            db.session.add(product)
        db.session.commit()

def fetch_data_from_api(api_key):
    url = "https://statistics-api-sandbox.wildberries.ru/api/v1/supplier/stocks"
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'dateFrom': '2024-12-01T00:00:00Z'}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")

def insert_data_into_db(data):
    for item in data:
        inventory = ProductInventory(
            last_change_date=item.get("lastChangeDate"),
            warehouse_name=item.get("warehouseName"),
            supplier_article=item.get("supplierArticle"),
            nm_id=item.get("nmId"),
            barcode=item.get("barcode"),
            quantity=item.get("quantity"),
            in_way_to_client=item.get("inWayToClient"),
            in_way_from_client=item.get("inWayFromClient"),
            quantity_full=item.get("quantityFull"),
            category=item.get("category"),
            subject=item.get("subject"),
            brand=item.get("brand"),
            tech_size=item.get("techSize"),
            days_on_site=item.get("daysOnSite"),
            price=item.get("Price"),
            discount=item.get("Discount"),
            is_supply=item.get("isSupply"),
            is_realization=item.get("isRealization"),
            sc_code=item.get("SCCode")
        )
        db.session.add(inventory)

        product = Product(
            supplierArticle=item.get("supplierArticle"),
            subject=item.get("subject"),
            brand=item.get("brand"),
            category=item.get("category"),
            quantity=item.get("quantity")
        )
        db.session.add(product)

    db.session.commit()