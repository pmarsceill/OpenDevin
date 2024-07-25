import subprocess
import threading
import time
import signal
import psutil

class TerminalHandler:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.process = None
        self.output = ""
        self.error = ""

    def run_command(self, command):
        def target():
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self.output, self.error = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self.terminate_process()
            return None, "Command timed out", True

        return self.output, self.error, False

    def terminate_process(self):
        if self.process:
            parent = psutil.Process(self.process.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
            gone, still_alive = psutil.wait_procs(children + [parent], timeout=3)
            for p in still_alive:
                p.kill()

    def is_interactive(self, command):
        interactive_commands = ['python', 'ipython', 'bash', 'sh', 'zsh', 'vim', 'nano']
        return any(cmd in command.split() for cmd in interactive_commands)

    def execute_command(self, command):
        if self.is_interactive(command):
            return None, "Interactive command detected and blocked", True

        output, error, timed_out = self.run_command(command)
        if timed_out:
            return output, error, timed_out

        return output, error, False

# Example usage
if __name__ == "__main__":
    handler = TerminalHandler(timeout=10)
    output, error, timed_out = handler.execute_command("echo 'Hello, World!'")
    print(f"Output: {output}")
    print(f"Error: {error}")
    print(f"Timed out: {timed_out}")

    output, error, timed_out = handler.execute_command("python -c 'while True: pass'")
    print(f"Output: {output}")
    print(f"Error: {error}")
    print(f"Timed out: {timed_out}")
