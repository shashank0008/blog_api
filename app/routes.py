from flask import Blueprint, request, jsonify, current_app as app
from app import db, cache, limiter
from app.models import User, BlogPost
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, Forbidden
import re

# Create a Blueprint for the routes
bp = Blueprint('routes', __name__)

# Function to validate email format
def validate_email(email):
    email_regex = app.config['EMAIL_REGEX']
    return re.match(email_regex, email)

# Function to validate password length
def validate_password(password):
    min_length = app.config['PASSWORD_MIN_LENGTH']
    return len(password) >= min_length

# Route for user signup
@bp.route('/signup', methods=['POST'])
@limiter.limit("10 per minute") # Rate limiting
def signup():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid JSON data')

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            app.logger.warning('Email and password are required')
            return jsonify({'message': 'Email and password are required'}), 400

        if not validate_email(email):
            app.logger.warning('Invalid email format')
            return jsonify({'message': 'Invalid email format'}), 400

        if not validate_password(password):
            app.logger.warning('Password must be at least 8 characters long')
            return jsonify({'message': f'Password must be at least {app.config["PASSWORD_MIN_LENGTH"]} characters long'}), 400

        if User.query.filter_by(username=email).first():
            app.logger.warning('User already exists')
            return jsonify({'message': 'User already exists'}), 400

        user = User(username=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        app.logger.info('User created successfully')
        return jsonify({'message': 'User created successfully'}), 201
    except BadRequest as e:
        app.logger.error('Bad request: %s', e)
        return jsonify({'message': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route for user login
@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid JSON data')

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            app.logger.warning('Email and password are required')
            return jsonify({'message': 'Email and password are required'}), 400

        if not validate_email(email):
            app.logger.warning('Invalid email format')
            return jsonify({'message': 'Invalid email format'}), 400

        user = User.query.filter_by(username=email).first()
        if user is None or not user.check_password(password):
            app.logger.warning('Invalid credentials')
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.id)
        app.logger.info('User logged in successfully')
        return jsonify(access_token=access_token), 200
    except BadRequest as e:
        app.logger.error('Bad request: %s', e)
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route to create a new blog post
@bp.route('/posts', methods=['POST'])
@jwt_required() # JWT authentication required
@limiter.limit("5 per minute") # Rate limiting
def create_post():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            app.logger.warning('User not authorized')
            return jsonify({'message': 'User not authorized'}), 403

        data = request.get_json()
        if not data:
            raise BadRequest('Invalid JSON data')

        title = data.get('title')
        body = data.get('body')
        user_id = get_jwt_identity()

        if not title or not body:
            app.logger.warning('Title and body are required')
            return jsonify({'message': 'Title and body are required'}), 400

        post = BlogPost(title=title, body=body, user_id=user_id)
        db.session.add(post)
        db.session.commit()

        app.logger.info('Post created successfully')
        return jsonify({'message': 'Post created successfully','id': post.id}), 201
    except BadRequest as e:
        app.logger.error('Bad request: %s', e)
        return jsonify({'message': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route to get all blog posts for the logged-in user
@bp.route('/posts', methods=['GET'])
@jwt_required()  # JWT authentication required
@cache.cached(timeout=60, query_string=True) # Caching
def get_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        user_id = get_jwt_identity()

        pagination = BlogPost.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
        posts = pagination.items

        data = [{
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'timestamp': post.timestamp
        } for post in posts]

        app.logger.info('Posts retrieved successfully')
        return jsonify({
            'posts': data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    except SQLAlchemyError as e:
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route to get a specific blog post by ID
@bp.route('/posts/<int:id>', methods=['GET'])
@jwt_required()  # JWT authentication required
@limiter.limit("20 per minute") # Rate limiting
def get_post(id):
    try:
        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=id, user_id=user_id).first()
        if post is None:
            app.logger.warning('User not authorized to access this post')
            return jsonify({'message': 'User not authorized to access this post'}), 403

        app.logger.info('Post retrieved successfully: %s', post.id)
        return jsonify({'id': post.id, 'title': post.title, 'body': post.body, 'timestamp': post.timestamp})
    except SQLAlchemyError as e:
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route to update a specific blog post by ID
@bp.route('/posts/<int:id>', methods=['PUT'])
@jwt_required() # JWT authentication required
@limiter.limit("5 per minute") # Rate limiting
def update_post(id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid JSON data')

        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=id, user_id=user_id).first()
        if post is None:
            app.logger.warning('User not authorized to access this post')
            return jsonify({'message': 'User not authorized to access this post'}), 403

        title = data.get('title')
        body = data.get('body')

        if not title or not body:
            app.logger.warning('Title and body are required')
            return jsonify({'message': 'Title and body are required'}), 400

        post.title = title
        post.body = body
        db.session.commit()

        app.logger.info('Post updated successfully: %s', post.id)
        return jsonify({'message': 'Post updated successfully'})
    except BadRequest as e:
        app.logger.error('Bad request: %s', e)
        return jsonify({'message': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500

# Route to delete a specific blog post by ID
@bp.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required() # JWT authentication required
@limiter.limit("5 per minute") # Rate limiting
def delete_post(id):
    try:
        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=id, user_id=user_id).first()
        if post is None:
            app.logger.warning('User not authorized to access this post')
            return jsonify({'message': 'User not authorized to access this post'}), 403

        db.session.delete(post)
        db.session.commit()

        app.logger.info('Post deleted successfully: %s', post.id)
        return jsonify({'message': 'Post deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error('Database error: %s', e)
        return jsonify({'message': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', e)
        return jsonify({'message': 'An unexpected error occurred', 'details': str(e)}), 500
