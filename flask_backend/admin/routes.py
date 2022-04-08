from flask import Blueprint, render_template
from flask_user import roles_required

admin = Blueprint('admin', __name__)

# Route to demo admin
@admin.route('/admin')
@roles_required('Admin')    # Use of @roles_required decorator
def admin_page():
    # String-based templates
    return render_template('admin.html')
