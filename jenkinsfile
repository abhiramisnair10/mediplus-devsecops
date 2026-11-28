pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        APP_NAME = 'mediplus'
        DOCKER_IMAGE = 'mediplus-app'
        PYTHON_IMAGE = 'python:3.11-slim'

        // SonarQube configuration
        SONAR_HOST_URL = 'http://172.31.40.249:9000'
        SONAR_PROJECT_KEY = 'mediplus'

        // Application running on EC2 host, port 8001
        ZAP_TARGET_URL = 'http://host.docker.internal:8001'
    }

    stages {

        // ==========================================
        // 1. CHECKOUT
        // ==========================================
        stage('Checkout') {
            steps {
                echo 'Checking out Mediplus from GitHub'

                checkout scm

                sh '''
                    echo "Repository checkout successful"
                    ls -la
                '''
            }
        }

        // ==========================================
        // 2. PYTHON DEPENDENCY INSTALLATION
        // ==========================================
        stage('Python Dependency Installation') {
            steps {
                echo 'Installing Python dependencies'

                sh '''
                    set -e

                    test -f requirements.txt

                    docker run --rm \
                    --memory=256m \
                    --cpus=1 \
                    -v "$WORKSPACE:/app" \
                    -w /app \
                    -e PIP_NO_CACHE_DIR=1 \
                    "$PYTHON_IMAGE" \
                    sh -c "pip install --no-cache-dir --disable-pip-version-check --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt"

                    echo "Python dependencies installed successfully"
                '''
            }
        }

        // ==========================================
        // 3. DEPENDENCY SECURITY SCAN
        // ==========================================
        stage('Dependency Scan - pip-audit') {
            steps {
                echo 'Scanning Python dependencies for vulnerabilities'

                sh '''
                    set -e

                    docker run --rm \
                    --memory=256m \
                    --cpus=1 \
                    -v "$WORKSPACE:/app" \
                    -w /app \
                    "$PYTHON_IMAGE" \
                    sh -c "pip install --no-cache-dir pip-audit && pip-audit -r requirements.txt --format json --output pip-audit-report.json"
                '''
            }

            post {
                always {
                    archiveArtifacts artifacts: 'pip-audit-report.json',
                                     allowEmptyArchive: true
                }
            }
        }

        // ==========================================
        // 4. STATIC APPLICATION SECURITY TESTING
        // ==========================================
        stage('SAST - SonarQube') {
            steps {
                echo 'Running SonarQube static code analysis'

                withCredentials([
                    string(
                        credentialsId: 'sonar-token',
                        variable: 'SONAR_TOKEN'
                    )
                ]) {
                    sh '''
                        docker run --rm \
                        --memory=256m \
                        --cpus=1 \
                        --add-host=host.docker.internal:host-gateway \
                        -e SONAR_HOST_URL="http://172.31.40.249:9000" \
                        -e SONAR_TOKEN="$SONAR_TOKEN" \
                        -v "$WORKSPACE:/usr/src" \
                        -w /usr/src \
                        sonarsource/sonar-scanner-cli:latest \
                        -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions="**/.git/**,**/venv/**,**/__pycache__/**,**/node_modules/**"
                    '''
                }
            }
        }

        // ==========================================
        // 5. DYNAMIC APPLICATION SECURITY TESTING
        // ==========================================
        stage('DAST - OWASP ZAP') {
            steps {
                echo 'Running OWASP ZAP baseline security scan'

                sh '''
                    set -e

                    docker run --rm \
                    --memory=256m \
                    --cpus=1 \
                    --add-host=host.docker.internal:host-gateway \
                    -v "$WORKSPACE:/zap/wrk/:rw" \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py \
                    -t "$ZAP_TARGET_URL" \
                    -J zap-report.json \
                    -r zap-report.html
                '''
            }

            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html,zap-report.json',
                                     allowEmptyArchive: true
                }
            }
        }

        // ==========================================
        // 6. DOCKER IMAGE BUILD
        // ==========================================
        stage('Docker Build') {
            steps {
                echo 'Building Mediplus Docker image'

                sh '''
                    set -e

                    test -f Dockerfile

                    docker build \
                    -t "$DOCKER_IMAGE:$BUILD_NUMBER" \
                    -t "$DOCKER_IMAGE:latest" \
                    .

                    echo "Docker image built successfully"

                    docker images "$DOCKER_IMAGE"
                '''
            }
        }
    }

    // ==========================================
    // POST BUILD ACTIONS
    // ==========================================
    post {

        success {
            echo '''
            ======================================
            MEDIPLUS CI/CD PIPELINE SUCCESSFUL
            ======================================
            Python dependencies installed
            Dependency security scan completed
            SonarQube analysis completed
            OWASP ZAP scan completed
            Docker image built successfully
            ======================================
            '''
        }

        failure {
            echo '''
            ======================================
            MEDIPLUS CI/CD PIPELINE FAILED
            ======================================
            Please check Jenkins Console Output.
            Identify the failed stage and resolve
            the issue before rebuilding.
            ======================================
            '''
        }

        always {
            echo 'CI/CD Pipeline execution finished.'

            sh '''
                echo "Available Docker images:"
                docker images "$DOCKER_IMAGE" || true

                echo "Workspace disk usage:"
                df -h "$WORKSPACE"
            '''
        }
    }
}
