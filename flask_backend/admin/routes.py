from flask import Blueprint

admin = Blueprint('admin', __name__)

@admin.route('/')
def index():
	return "Hello, World! This is the admin page."