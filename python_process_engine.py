import socket
import multiprocessing
import os
import uuid
import subprocess
import json
from collections import deque

# Track running jobs {job_id: process}
jobs = {}
# Track job logs {job_id: output}
job_logs = {}
job_logs_queue = deque(maxlen=100)  # Limit log storage to avoid memory bloat

def execute_script(script_name, script_args, job_id):
    """Runs a script as a separate process and logs output."""
    try:
        process = subprocess.Popen(
            ["python3", script_name, *script_args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        jobs[job_id] = process  # Store the job

        stdout, stderr = process.communicate()  # Wait for script completion

        output = stdout if stdout else stderr
        job_logs[job_id] = output
        job_logs_queue.append((job_id, output))

        del jobs[job_id]  # Remove from active jobs after completion
    except Exception as e:
        job_logs[job_id] = f"Error: {str(e)}"
        job_logs_queue.append((job_id, f"Error: {str(e)}"))

def handle_client(conn):
    """Handles incoming requests from clients."""
    try:
        request = conn.recv(65536).decode("utf-8").strip()
        parts = request.split(" ")
        command = parts[0]

        if command == "run":
            script_name = parts[1]
            script_args = parts[2:] if len(parts) > 2 else []
            job_id = str(uuid.uuid4())

            # Run the script in a separate process
            process = multiprocessing.Process(target=execute_script, args=(script_name, script_args, job_id))
            process.start()

            conn.sendall(f"Job started: {job_id}\n".encode("utf-8"))

        elif command == "status":
            job_id = parts[1]
            status = "running" if job_id in jobs else "completed"
            conn.sendall(f"Job {job_id} status: {status}\n".encode("utf-8"))

        elif command == "logs":
            job_id = parts[1]
            log = job_logs.get(job_id, "No logs found.")
            conn.sendall(f"Logs for {job_id}:\n{log}\n".encode("utf-8"))

        elif command == "list":
            running_jobs = list(jobs.keys())
            completed_jobs = list(job_logs.keys())
            response = json.dumps({"running": running_jobs, "completed": completed_jobs})
            conn.sendall(f"{response}\n".encode("utf-8"))

        elif command == "exit":
            conn.sendall(b"Shutting down server.\n")
            conn.close()
            os._exit(0)

        else:
            conn.sendall(b"Unknown command.\n")
    except Exception as e:
        conn.sendall(f"Error: {str(e)}\n".encode("utf-8"))
    finally:
        conn.close()

def start_server(socket_path="/tmp/python_process_engine.sock"):
    """Starts a Unix socket server for process-based script execution."""
    try:
        if os.path.exists(socket_path):
            os.remove(socket_path)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(socket_path)
        server.listen(5)
        print(f"Python Process Engine running at {socket_path}")

        while True:
            conn, _ = server.accept()
            multiprocessing.Process(target=handle_client, args=(conn,)).start()
    except KeyboardInterrupt:
        print("Shutting down Python Process Engine.")
        server.close()
        os._exit(0)

if __name__ == "__main__":
    start_server()
