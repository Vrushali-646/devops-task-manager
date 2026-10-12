pipeline {
    agent any

    triggers {
        // Automatically poll SCM every minute for changes pushed to GitHub
        pollSCM('* * * * *')
    }

    environment {
        APP_NAME = 'devops-task-manager'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo '=================================================='
                echo 'Checking out latest commit from GitHub repository'
                echo '=================================================='
                checkout scm
            }
        }

        stage('2. Build Validation') {
            steps {
                echo '=================================================='
                echo 'Validating application files and dependencies'
                echo '=================================================='
                bat 'call npm install'
                bat 'call npm run build'
            }
        }

        stage('3. Docker Containerization') {
            steps {
                echo '=================================================='
                echo 'Building and tagging Docker container image'
                echo '=================================================='
                bat 'wsl docker build -t devops-task-manager:latest .'
                bat 'wsl docker images | grep devops-task-manager'
            }
        }

        stage('4. Deploy to Kubernetes') {
            steps {
                echo '=================================================='
                echo 'Applying Kubernetes manifests (Deployment & Service)'
                echo '=================================================='
                bat 'wsl kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml'
                bat 'wsl kubectl rollout restart deployment devops-task-manager'
                bat 'wsl kubectl rollout status deployment devops-task-manager --timeout=60s'
            }
        }

        stage('5. Health & Pod Verification') {
            steps {
                echo '=================================================='
                echo 'Verifying running Pods and LoadBalancer endpoints'
                echo '=================================================='
                bat 'wsl kubectl get pods -l app=devops-task-manager -o wide'
                bat 'wsl kubectl get svc devops-task-manager-service'
            }
        }
    }

    post {
        success {
            echo '=================================================='
            echo 'SUCCESS: CI/CD Pipeline completed! App is live on K8s.'
            echo 'Metrics available at: http://localhost:9090'
            echo 'Dashboard available at: http://localhost:3001'
            echo '=================================================='
        }
        failure {
            echo '=================================================='
            echo 'FAILURE: Pipeline failed. Check console logs above.'
            echo '=================================================='
        }
    }
}
