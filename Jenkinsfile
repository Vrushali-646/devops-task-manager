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

        stage('3. Docker Containerization & K8s Deployment') {
            steps {
                echo '=================================================='
                echo 'Building Docker Image and Deploying to Kubernetes'
                echo '=================================================='
                bat 'curl.exe -m 120 -s -N http://172.28.172.214:9999/deploy'
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
