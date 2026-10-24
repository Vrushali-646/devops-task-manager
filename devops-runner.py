import http.server
import subprocess
import os
import socket
import json
import time

PORT = 9999
CANDIDATE_WORKSPACES = [
    '/mnt/c/ProgramData/Jenkins/.jenkins/workspace/cie-1',
    '/mnt/c/ProgramData/Jenkins/.jenkins/workspace/task-manager-build',
    '/mnt/c/Users/Vrushali Patil/OneDrive/Desktop/devops-task-manager'
]

last_scrape = 0
cached_metrics = ""

def get_k8s_metrics():
    global last_scrape, cached_metrics
    now = time.time()
    if now - last_scrape < 2.0 and cached_metrics:
        return cached_metrics
    try:
        cmd_dep = ["kubectl", "get", "deployment", "devops-task-manager", "-o", "json"]
        dep = json.loads(subprocess.check_output(cmd_dep, text=True, timeout=5))
        status = dep.get("status", {})
        spec = dep.get("spec", {})
        replicas = status.get("replicas", 0)
        ready = status.get("readyReplicas", 0)
        available = status.get("availableReplicas", 0)
        desired = spec.get("replicas", 0)

        cmd_pods = ["kubectl", "get", "pods", "-l", "app=devops-task-manager", "-o", "json"]
        pods = json.loads(subprocess.check_output(cmd_pods, text=True, timeout=5))
        items = pods.get("items", [])
        running_pods = sum(1 for p in items if p.get("status", {}).get("phase") == "Running" and not p.get("metadata", {}).get("deletionTimestamp"))
        terminating_pods = sum(1 for p in items if p.get("metadata", {}).get("deletionTimestamp"))
        pending_pods = sum(1 for p in items if p.get("status", {}).get("phase") == "Pending")

        lines = [
            '# HELP kube_deployment_spec_replicas Number of desired pods for a deployment.',
            '# TYPE kube_deployment_spec_replicas gauge',
            f'kube_deployment_spec_replicas{{deployment="devops-task-manager"}} {desired}',
            '# HELP kube_deployment_status_replicas The number of replicas per deployment.',
            '# TYPE kube_deployment_status_replicas gauge',
            f'kube_deployment_status_replicas{{deployment="devops-task-manager"}} {replicas}',
            '# HELP kube_deployment_status_replicas_available The number of available replicas per deployment.',
            '# TYPE kube_deployment_status_replicas_available gauge',
            f'kube_deployment_status_replicas_available{{deployment="devops-task-manager"}} {available}',
            '# HELP kube_deployment_status_replicas_ready The number of ready replicas per deployment.',
            '# TYPE kube_deployment_status_replicas_ready gauge',
            f'kube_deployment_status_replicas_ready{{deployment="devops-task-manager"}} {ready}',
            '# HELP kube_pod_status_phase The number of pods currently in each phase.',
            '# TYPE kube_pod_status_phase gauge',
            f'kube_pod_status_phase{{deployment="devops-task-manager",phase="Running"}} {running_pods}',
            f'kube_pod_status_phase{{deployment="devops-task-manager",phase="Terminating"}} {terminating_pods}',
            f'kube_pod_status_phase{{deployment="devops-task-manager",phase="Pending"}} {pending_pods}',
            ''
        ]
        cached_metrics = "\n".join(lines)
        last_scrape = now
    except Exception as e:
        cached_metrics = f"# ERROR: {e}\n"
    return cached_metrics


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
        if self.path in ['/k8s/metrics', '/metrics']:
            metrics = get_k8s_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics.encode('utf-8'))
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
            'sleep 2 && kubectl rollout restart deployment devops-task-manager || true',
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
