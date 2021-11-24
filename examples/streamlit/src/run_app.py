import os
from subprocess import Popen, PIPE, STDOUT
import sys
import time
import webbrowser


def main():

    # Getting path to python executable (full path of deployed python on Windows)
    executable = sys.executable

    path_to_main = os.path.join(os.path.dirname(__file__), "app.py")

    # Running streamlit server in a subprocess and writing to log file
    proc = Popen(
        [
            executable,
            "-m",
            "streamlit",
            "run",
            path_to_main,
            # The following option appears to be necessary to correctly start the streamlit server,
            # but it should start without it. More investigations should be carried out.
            "--server.headless=true",
            "--global.developmentMode=false",
        ],
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
    )
    proc.stdin.close()

    # Force the opening (does not open automatically) of the browser tab after a brief delay to let
    # the streamlit server start.
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

    while True:
        s = proc.stdout.read()
        if not s:
            break
        print(s, end="")

    proc.wait()


if __name__ == "__main__":
    main()
