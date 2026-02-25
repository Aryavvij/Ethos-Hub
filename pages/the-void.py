from flask import Blueprint, render_template

the_void_bp = Blueprint('the_void', __name__)

@the_void_bp.route('/void')
def the_void():
    return render_template('the-void.html')
