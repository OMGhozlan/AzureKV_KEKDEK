from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from .models import CustomerFeedback, SecureFeedback, db
from .helpers import encrypt_customer_feedback, decrypt_secure_feedback

def check_authentication(token):
    return token == "very-secret-token"  # Simple check for example purposes

def require_auth(f):
    """Decorator to require an 'Authorization' header."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not check_authentication(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/api/feedback', methods=['POST'])
def post_feedback():
    """
    Creates a new feedback record using the email, contact number and feedback provided
    in the JSON body of the request.

    Returns a JSON response with the ID of the newly created record.

    The request body should be a JSON object with the following keys:
        - email: The email address of the person providing the feedback
        - contact_number: The contact number of the person providing the feedback
        - feedback: The feedback provided

    :return: A JSON response with the ID of the newly created record
    :rtype: (int, dict)
    """
    try:
        data = request.json
        feedback = CustomerFeedback(data['email'], data['contact_number'], data['feedback'])
        secure_feedback = encrypt_customer_feedback(feedback)
        db.session.add(secure_feedback)
        db.session.commit()
        return jsonify({'id': secure_feedback.id}), 201
    except Exception as e:
        current_app.logger.error('Error while creating feedback: %s', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@routes_bp.route('/api/feedback/<int:id>', methods=['GET'])
@require_auth
def get_feedback(id):
    """
    Retrieves a feedback record by its ID.

    :param id: The ID of the record to retrieve
    :return: A JSON response with the feedback data
    :rtype: (int, dict)
    """    
    try:
        secure_feedback = SecureFeedback.query.get(id)
        if secure_feedback is None:
            return jsonify({'error': 'Not found'}), 404
        feedback = decrypt_secure_feedback(secure_feedback)
        return jsonify(feedback.__dict__), 200
    except Exception as e:
        current_app.logger.error('Error while retrieving feedback: %s', e)
        return jsonify({'error': 'Internal Server Error'}), 500

