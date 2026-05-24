import os

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '489gb4ubntun9hggnigbn0234'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

messages = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join_chat():
    username = request.form.get('username')
    room = request.form.get('room')
    if not username or not room:
        return redirect(url_for('index'))
    session['username'] = username
    session['room'] = room
    return redirect(url_for('room'))

@app.route('/room')
def room():
    if 'username' not in session or 'room' not in session:
        return redirect(url_for('index'))
    room = session['room']
    room_messages = messages.get(room, [])[-50:]
    return render_template('room.html',
                           username=session['username'],
                           room=room,
                           messages=room_messages)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('system_message',
         {'msg': f'{username} присоединился к чату',
          'time': datetime.now().strftime('%H:%M:%S')},
         room=room)


@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('system_message',
         {'msg': f'{username} покинул чат',
          'time': datetime.now().strftime('%H:%M:%S')},
         room=room)

@socketio.on('send_message')
def handle_message(data):
    username = data['username']
    room = data['room']
    message = data['message']
    timestamp = datetime.now().strftime('%H:%M:%S')
    if room not in messages:
        messages[room] = []
    messages[room].append({
        'username': username,
        'message': message,
        'time': timestamp
    })
    emit('receive_message', {
        'username': username,
        'message': message,
        'time': timestamp
    }, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, log_output=None, use_reloader=None)