import frida
import sys
import pathlib
import threading
import psutil

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("target required")
        exit(1)

    pid = frida.spawn(sys.argv[1:])
    session = frida.attach(pid)
    with open(pathlib.Path(__file__).parent.resolve() / "dump_key.js") as f:
        script = session.create_script(f.read())
    frida.resume(pid)

    event = threading.Event()
    script.on("message", lambda message, data: (print(message["payload"]), event.set()))
    script.load()
    event.wait()
    psutil.Process(pid).terminate()
    session.detach()
