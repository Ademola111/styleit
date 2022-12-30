"""to start an app"""
from styleitapp import app, sio

if __name__ == "__main__":
    # app.run(debug=True, port=8080)
    # socketio.run(app)
    sio.run(app, debug=True)
    