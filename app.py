from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from waitress import serve
from flask_migrate import Migrate
import os
load_dotenv()

# Create the app first
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').strip()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after creating app
from models import db
migrate = Migrate(app, db)
from routes import exam_bp

# Initialize the app with SQLAlchemy
db.init_app(app)

app.register_blueprint(exam_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running'})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=4000)