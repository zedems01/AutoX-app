pipeline {
    agent any

    options {
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        // Directories
        BACKEND_DIR = 'x_automation_app/backend'
        FRONTEND_DIR = 'x_automation_app/frontend'
        
        // Python
        PYTHON_VENV = '.venv'
        
        // Docker images
        BACKEND_IMAGE_NAME = 'autox-backend'
        FRONTEND_IMAGE_NAME = 'autox-frontend'
        
        // Node.js
        NODEJS_TOOL = 'node22'
        
        // AWS
        AWS_REGION = 'us-east-1'  // Update with your AWS region
        AWS_ACCOUNT_ID = credentials('aws-account-id')  // Store in Jenkins credentials
        ECR_BACKEND_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${BACKEND_IMAGE_NAME}"
    }

    tools {
        nodejs NODEJS_TOOL
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Image Tag') {
            steps {
                script {
                    def rawBranch = env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'detached'
                    rawBranch = rawBranch.replaceFirst(/^origin\//, '')
                    rawBranch = rawBranch.replaceAll('/', '-')
                    env.IMAGE_TAG = rawBranch == 'main' ? 'latest' : "dev-${rawBranch}"
                    env.IMAGE_TAG = env.IMAGE_TAG.replaceAll('[^A-Za-z0-9._-]', '-')
                    echo "Resolved image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        // ============================================
        // BACKEND CI/CD
        // ============================================
        stage('Backend: Set Up Python Environment') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh '''
                        python3 -m venv ${PYTHON_VENV}
                        . ${PYTHON_VENV}/bin/activate
                        pip install --upgrade pip
                        pip install uv
                        uv pip install .
                    '''
                }
            }
        }

        stage('Backend: Run Tests') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh '''
                        . ${PYTHON_VENV}/bin/activate
                        pytest -v
                    '''
                }
            }
        }

        stage('Backend: Docker Build & Push') {
            parallel {
                stage('Push to Docker Hub') {
                    steps {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub-autox',
                            usernameVariable: 'DOCKERHUB_USERNAME',
                            passwordVariable: 'DOCKERHUB_PASSWORD'
                        )]) {
                            dir(env.BACKEND_DIR) {
                                sh '''
                                    set -e
                                    echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                                    docker build -t "$DOCKERHUB_USERNAME"/${BACKEND_IMAGE_NAME}:${IMAGE_TAG} .
                                    docker push "$DOCKERHUB_USERNAME"/${BACKEND_IMAGE_NAME}:${IMAGE_TAG}
                                '''
                            }
                        }
                    }
                }

                stage('Push to AWS ECR') {
                    steps {
                        withCredentials([
                            string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                            string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                        ]) {
                            dir(env.BACKEND_DIR) {
                                sh '''
                                    set -e
                                    # Login to AWS ECR
                                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_BACKEND_REPO}
                                    
                                    # Build and tag for ECR
                                    docker build -t ${BACKEND_IMAGE_NAME}:${IMAGE_TAG} .
                                    docker tag ${BACKEND_IMAGE_NAME}:${IMAGE_TAG} ${ECR_BACKEND_REPO}:${IMAGE_TAG}
                                    
                                    # Push to ECR
                                    docker push ${ECR_BACKEND_REPO}:${IMAGE_TAG}
                                '''
                            }
                        }
                    }
                }
            }

            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }

        // ============================================
        // FRONTEND CI/CD
        // ============================================
        stage('Frontend: Install Dependencies') {
            steps {
                dir(env.FRONTEND_DIR) {
                    sh 'npm ci'
                }
            }
        }

        stage('Frontend: Run Linter') {
            steps {
                dir(env.FRONTEND_DIR) {
                    sh 'npm run lint'
                }
            }
        }

        stage('Frontend: Run Tests') {
            steps {
                dir(env.FRONTEND_DIR) {
                    sh 'npm test -- --runInBand'
                }
            }
        }

        stage('Frontend: Build App') {
            steps {
                dir(env.FRONTEND_DIR) {
                    sh 'npm run build'
                }
            }
        }

        stage('Frontend: Docker Build & Push') {
            when {
                expression { fileExists("${env.FRONTEND_DIR}/Dockerfile") }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-autox',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_PASSWORD'
                )]) {
                    dir(env.FRONTEND_DIR) {
                        sh '''
                            set -e
                            REGISTRY=${DOCKERHUB_NAMESPACE:-$DOCKERHUB_USERNAME}
                            echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                            docker build -t "$REGISTRY"/${FRONTEND_IMAGE_NAME}:${IMAGE_TAG} .
                            docker push "$REGISTRY"/${FRONTEND_IMAGE_NAME}:${IMAGE_TAG}
                        '''
                    }
                }
            }

            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }

        stage('Frontend: Archive Artifacts') {
            steps {
                dir(env.FRONTEND_DIR) {
                    archiveArtifacts artifacts: '.next/standalone/**', allowEmptyArchive: true
                }
            }
        }

        // ============================================
        // DEPLOYMENT TRIGGER (for main branch only)
        // ============================================
        stage('Trigger AWS ECS Deployment') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        # Force ECS service to use the new task definition
                        aws ecs update-service \
                            --cluster autox-cluster \
                            --service autox-backend-service \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                        
                        echo "ECS deployment triggered successfully"
                    '''
                }
            }
        }
    }

    post {
        always {
            dir(env.BACKEND_DIR) {
                sh 'rm -rf ${PYTHON_VENV} || true'
            }
            cleanWs()
        }

        success {
            echo "✅ Pipeline completed successfully!"
        }

        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}

