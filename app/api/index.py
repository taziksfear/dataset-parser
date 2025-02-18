from flask import Flask, jsonify
from app import create_app

app = create_app()

@app.route('/')
def hello():
    return jsonify({"message": "Hello deloyment version"})

if __name__ == "__main__":
    app.run()