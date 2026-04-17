pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BACKEND = "backend"
        DOCKER_IMAGE_FRONTEND = "frontend"
        REGISTRY = "local"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Build Images') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE_BACKEND}:latest -f Dockerfile.backend ."
                    sh "docker build -t ${DOCKER_IMAGE_FRONTEND}:latest -f Dockerfile.frontend ."
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    // This assumes the Jenkins agent has access to kubectl and minikube context
                    sh "kubectl apply -f k8s/secrets.yaml"
                    sh "kubectl apply -f k8s/"
                }
            }
        }

        stage('Verification') {
            steps {
                sh "kubectl get pods"
                sh "kubectl get svc"
                sh "kubectl rollout status deployment/backend-deployment"
            }
        }
    }

    post {
        always {
            echo 'Deployment Pipeline Finished'
        }
    }
}
