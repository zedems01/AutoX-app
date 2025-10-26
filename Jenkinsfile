pipeline {
    agent any

    options {
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        BACKEND_DIR = 'x_automation_app/backend'
        FRONTEND_DIR = 'x_automation_app/frontend'
        
        PYTHON_VENV = 'venv'
        
        BACKEND_IMAGE_NAME = 'autox-backend'
        FRONTEND_IMAGE_NAME = 'autox-frontend'
        
        NODEJS_TOOL = 'nodejs-22.20.0'
        
        AWS_REGION = 'eu-west-3'
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
                    env.IMAGE_TAG = rawBranch == 'main' ? 'latest' : "${rawBranch}"
                    env.IMAGE_TAG = env.IMAGE_TAG.replaceAll('[^A-Za-z0-9._-]', '-')
                    echo "Resolved image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        // BACKEND CI/CD
        stage('Backend: Set Up Python Environment') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh '''
                        python3 -m venv ${PYTHON_VENV}
                        . ${PYTHON_VENV}/bin/activate
                        python3 -m pip install --upgrade pip
                        pip3 install uv
                        uv pip install .
                    '''
                }
            }
        }

        stage('Backend: Run Tests') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh """
                        set -e
                        . ${PYTHON_VENV}/bin/activate
                        pytest
                        echo "Tests completed."
                    """
                }
            }
        }

        stage('Backend: Build Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-token',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_PASSWORD'
                )]) {
                    dir(env.BACKEND_DIR) {
                        script {
                            def dockerHubImage = "${DOCKERHUB_USERNAME}/${BACKEND_IMAGE_NAME}:${IMAGE_TAG}"
                            sh "docker build -t ${dockerHubImage} ."
                        }
                    }
                }
            }
        }

        stage('Backend: Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-token',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_PASSWORD'
                )]) {
                    dir(env.BACKEND_DIR) {
                        script {
                            def dockerHubImage = "${DOCKERHUB_USERNAME}/${BACKEND_IMAGE_NAME}:${IMAGE_TAG}"
                            sh """
                                set -e
                                echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                                docker push ${dockerHubImage}
                            """
                        }
                    }
                }
            }
            post {
                always {
                    sh 'docker logout'
                }
            }
        }


        stage('Backend: Push to AWS ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-account-id', variable: 'AWS_ACCOUNT_ID'),
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
                    usernamePassword(
                        credentialsId: 'dockerhub-token',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    )
                ]) {
                    dir(env.BACKEND_DIR) {
                        script {
                            def dockerHubImage = "${DOCKERHUB_USERNAME}/${BACKEND_IMAGE_NAME}:${IMAGE_TAG}"
                            def ecrRepo = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                            def ecrImage = "${ecrRepo}/${BACKEND_IMAGE_NAME}:${IMAGE_TAG}"
                            
                            sh """
                                set -e
                                aws --version

                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ecrRepo}
                                docker tag ${dockerHubImage} ${ecrImage}
                                docker push ${ecrImage}
                            """
                        }
                    }
                }
            }
            post {
                always {
                    sh "docker logout"
                }
            }
        }

        // FRONTEND CI/CD
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

        stage('Frontend: Docker Build & Push') {
            when {
                expression { fileExists("${env.FRONTEND_DIR}/Dockerfile") }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-token',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_PASSWORD'
                )]) {
                    dir(env.FRONTEND_DIR) {
                        script {
                            def dockerHubImage = "${DOCKERHUB_USERNAME}/${FRONTEND_IMAGE_NAME}:${IMAGE_TAG}"
                            sh """
                                set -e
                                echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                                docker build -t ${dockerHubImage} .
                                docker push ${dockerHubImage}
                            """
                        }
                    }
                }
            }

            post {
                always {
                    sh 'docker logout'
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

        // DEPLOYMENT TRIGGER for main branch
        stage('Trigger AWS ECS Deployment') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        # Force ECS service to use the new task definition
                        aws ecs update-service \
                            --cluster autox-cluster \
                            --service autox-backend-service \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                        
                        echo "ECS deployment triggered successfully"
                    """
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
            echo "+++++ Pipeline completed successfully! +++++"
        }

        failure {
            echo "----- Pipeline failed. Check logs for details. -----"
        }
    }
}

