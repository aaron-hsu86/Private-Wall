from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import message_model, user_model

@app.route('/dashboard')
def dashboard():
    if 'id' not in session:
        flash('Please login!', 'user')
        return redirect('/')
    # user = user_model.Users.get_one(session['id'])
    user_info = user_model.Users.user_received_msgs(session['id'])
    sent_msg_info = user_model.Users.user_sent_msgs(session['id'])
    other_users = user_model.Users.get_other_users(session['id'])
    return render_template('dashboard.html', user_info = user_info, sent_msg_info=sent_msg_info, other_users=other_users)

@app.route('/delete_msg/<int:id>')
def delete_msg(id):
    if 'id' not in session:
        flash('Please login!', 'user')
        return redirect('/')
    message_model.Messages.delete_message(id)
    return redirect('/dashboard')

@app.route('/send_msg', methods=['post'])
def send_msg():
    if 'id' not in session:
        flash('Please login!', 'user')
        return redirect('/')
    message_model.Messages.save_message(request.form)
    return redirect('/dashboard')

