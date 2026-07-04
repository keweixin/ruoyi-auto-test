pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    environment {
        PYTHON = 'python'
        BASE_URL = credentials('ruoyi-base-url')
        WEB_URL = credentials('ruoyi-web-url')
        ADMIN_USERNAME = credentials('ruoyi-admin-username')
        ADMIN_PASSWORD = credentials('ruoyi-admin-password')
        DB_HOST = credentials('ruoyi-db-host')
        DB_PORT = '3306'
        DB_USER = credentials('ruoyi-db-user')
        DB_PASSWORD = credentials('ruoyi-db-password')
        DB_NAME = credentials('ruoyi-db-name')
        TENANT_ID = '1'
        TENANT_NAME = '芋道源码'
    }

    stages {
        stage('拉取代码') {
            steps { checkout scm }
        }

        stage('清理历史产物') {
            steps {
                sh 'rm -rf reports/allure-report logs screenshots traces'
                sh 'mkdir -p reports/allure-results logs screenshots traces'
            }
        }

        stage('安装依赖') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install --with-deps chromium'
            }
        }

        stage('静态检查') {
            steps {
                sh 'python -m compileall -q api_auto common ui_auto integration conftest.py'
                sh 'pytest --collect-only -q'
            }
        }

        stage('执行全量测试') {
            steps {
                sh 'pytest api_auto/testcases ui_auto/testcases integration --alluredir=reports/allure-results'
            }
        }

        stage('生成 Allure 报告') {
            steps {
                sh 'allure generate reports/allure-results -o reports/allure-report --clean'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'screenshots/**, traces/**, logs/**, reports/allure-report/**', allowEmptyArchive: true
            allure includeProperties: false, results: [[path: 'reports/allure-results']]
        }
    }
}
