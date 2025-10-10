from flask import Flask
from flask_cors import CORS
from routes.email_routes import email_bp


app = Flask(__name__)
CORS(app)

# Register blueprints (route groups)
# Creates a mini Flask app that can handle routes.
# All routes defined with @email_bp.route(...) belong to that blueprint.
'''
So when you start your app, Flask automatically includes:
/emails
/analyze
/url
/distance
because they were defined in that registered blueprint. (In email_routes.py)
'''
app.register_blueprint(email_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
