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
        PYTHON_VENV = '.venv'
        IMAGE_NAME = 'autox-backend'
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

        stage('Set Up Python Environment') {
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

        stage('Run Tests') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh '''
                        . ${PYTHON_VENV}/bin/activate
                        pytest -v
                    '''
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-autox', usernameVariable: 'DOCKERHUB_USERNAME', passwordVariable: 'DOCKERHUB_PASSWORD')]) {
                    dir(env.BACKEND_DIR) {
                        sh '''
                            set -e
                            echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                            docker build -t "$DOCKERHUB_USERNAME"/${IMAGE_NAME}:${IMAGE_TAG} .
                            docker push "$DOCKERHUB_USERNAME"/${IMAGE_NAME}:${IMAGE_TAG}
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
    }

    post {
        always {
            dir(env.BACKEND_DIR) {
                sh 'rm -rf ${PYTHON_VENV}'
            }
            cleanWs()
        }
    }
}

