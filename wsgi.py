from flask_backend.app import socketio, app

if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)