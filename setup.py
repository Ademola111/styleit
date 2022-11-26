"""to start an app"""
from styleitapp import app, socketio

if __name__ == "__main__":
    # app.run(debug=True, port=8080)
    socketio.run(app)
