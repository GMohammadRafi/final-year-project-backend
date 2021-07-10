from app import app
import socket

if __name__ == "__main__":
    hostname = socket.gethostname()
    # app.run(debug=False, host=socket.gethostbyname(hostname))
    app.run(debug=False, host="192.168.0.108")

