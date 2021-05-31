from app import app
import socket

if __name__ == "__main__":
    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname))

