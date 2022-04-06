from flask_backend import socketio, app

if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)