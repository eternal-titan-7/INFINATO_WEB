import fcntl
import logging
import os
import pty
import select
import struct
import subprocess
import sys
import termios
import threading

from flask import Flask, render_template, request
from flask_socketio import SocketIO

clients = dict()

app = Flask(__name__)
socketio = SocketIO(app)


def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def reading(cid, sid):
    def func():
        active = True
        while active:
            socketio.sleep(0.1)
            (data_ready, _, _) = select.select([clients[cid]['fd']], [], [], 0)
            if data_ready:
                output = os.read(clients[cid]['fd'], 1024).decode()
                if "Process finished with exit code" in output:
                    os.close(clients[cid]['fd'])
                    clients[cid]['fd'] = None
                    clients[cid]['pid'] = None
                    socketio.emit("pty-output", {"output": output, "sid": sid}, namespace="/pty")
                    active = False
                else:
                    socketio.emit("pty-output", {"output": output, "sid": sid}, namespace="/pty")

    return func


@socketio.on("save", namespace="/pty")
def _save(data):
    code = data['code']
    sid = data['sid']
    cid = request.values.to_dict().get('t')
    client = clients[cid]
    clients[cid]['sid'] = sid
    with open(f"{sid}.c", "w") as test:
        test.write(code)
    pid, fd = pty.fork()
    client['pid'] = pid
    client['fd'] = fd
    if pid == 0:
        subprocess.call(["clear"])
        process = subprocess.Popen(["gcc", f"{sid}.c", "-o", f"{sid}.exe"])
        returncode = process.wait()
        try:
            process1 = subprocess.Popen([f"./{sid}.exe"])
            subprocess.call(["rm", f"{sid}.c", f"{sid}.exe"])
            returncode1 = process1.wait()
            subprocess.call(["echo", f"\n\033[01;33mProcess finished with exit code {returncode1}\033[0m\n"])
        except:
            subprocess.call(["rm", f"{sid}.c"])
            subprocess.call(["echo", f"\n\033[01;33mProcess finished with exit code {returncode}\033[0m\n"])
    else:
        t = threading.Thread(target=reading(cid, sid))
        t.start()


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    client = request.values.to_dict().get('t')
    fd = clients[client].get('fd')
    if fd:
        os.write(fd, data['input'].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    client = request.values.to_dict().get('t')
    fd = clients[client].get('fd')
    if fd:
        set_winsize(fd, data["rows"], data["cols"])


@socketio.on("disconnect", namespace="/pty")
def disconnect():
    client = request.values.to_dict().get('t')
    clients.pop(client)


@socketio.on("connect", namespace="/pty")
def connect():
    cid = request.values.to_dict().get('t')
    clients[cid] = {}


def main():
    port = 5000
    socketio.run(app, debug=True, port=port)


@app.route("/")
def _main():
    return render_template("infinato.html")


# @app.route("/infinato")
# def _infinato():
#     return render_template("infinato.html", infsrc=f"INFINATO PAGE REACHED...")


# @app.route("/search")
# def _search():
#     return render_template("infinato.html", infsrc=f"You Searched for {request.args['s']}...")


if __name__ == "__main__":
    main()
    # app.run(debug=True, port=80)
