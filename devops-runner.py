import http.server
import subprocess
import os
import socket

PORT = 9999
CANDIDATE_WORKSPACES = [
    '/mnt/c/ProgramData/Jenkins/.jenkins/workspace/cie-1',
    '/mnt/c/ProgramData/Jenkins/.jenkins/workspace/task-manager-build',
    '/mnt/c/Users/Vrushali Patil/OneDrive/Desktop/devops-task-manager'
]

class DeployHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path in ['/health', '/ping']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK\n')
            return
        self.handle_deploy()

    def do_POST(self):
        self.handle_deploy()

    def handle_deploy(self):
        workspace = None
        for path in CANDIDATE_WORKSPACES:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'Dockerfile')):
                workspace = path
                break

        if not workspace:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Workspace directory not found!\n')
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()

        commands = [
            'echo "========================================================"',
            'echo "[CI/CD STAGE 3] Building Docker Container Image"',
            'echo "========================================================"',
            f'cd "{workspace}" && docker build -t devops-task-manager:latest .',
            'echo ""',
            'echo "========================================================"',
            'echo "[CI/CD STAGE 4] Deploying to Kubernetes Cluster"',
            'echo "========================================================"',
            f'cd "{workspace}" && kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml',
            'kubectl rollout restart deployment devops-task-manager',
            'kubectl rollout status deployment devops-task-manager --timeout=60s',
            'echo ""',
            'echo "========================================================"',
            'echo "[CI/CD STAGE 5] Verifying Pods and Services"',
            'echo "========================================================"',
            'kubectl get pods -l app=devops-task-manager -o wide',
            'kubectl get svc devops-task-manager-service',
            'echo ""',
            'echo "========================================================"',
            'echo "CI/CD Pipeline Completed Successfully! App is live on K8s!"',
            'echo "========================================================"'
        ]

        full_cmd = ' && '.join(commands)
        process = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in iter(process.stdout.readline, ''):
            self.wfile.write(line.encode('utf-8'))
            self.wfile.flush()

        process.wait()
        if process.returncode != 0:
            self.wfile.write(f'\nDeployment failed with exit code {process.returncode}\n'.encode('utf-8'))

    def log_message(self, format, *args):
        pass

class DualStackServer(http.server.ThreadingHTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        super().server_bind()

if __name__ == '__main__':
    server = DualStackServer(('::', PORT), DeployHandler)
    server.serve_forever()
