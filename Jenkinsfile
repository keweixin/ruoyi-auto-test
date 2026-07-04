pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        // Windows 本机环境：测试项目与被测系统(后端/前端/MySQL/Redis)都在本机
        PYTHON         = '.venv\\Scripts\\python.exe'
        ALLURE_BIN     = 'E:\\allure-2.37.0\\allure-2.37.0\\bin\\allure.bat'

        // 通过 credentials 注入测试环境配置（config.py 优先读环境变量）
        BASE_URL       = credentials('ruoyi-base-url')
        WEB_URL        = credentials('ruoyi-web-url')
        ADMIN_USERNAME = credentials('ruoyi-admin-username')
        ADMIN_PASSWORD = credentials('ruoyi-admin-password')
        DB_HOST        = credentials('ruoyi-db-host')
        DB_PORT        = '3306'
        DB_USER        = credentials('ruoyi-db-user')
        DB_PASSWORD    = credentials('ruoyi-db-password')
        DB_NAME        = credentials('ruoyi-db-name')
        TENANT_ID      = '1'
        TENANT_NAME    = '芋道源码'
    }

    stages {
        stage('拉取代码') {
            steps { checkout scm }
        }

        stage('清理历史产物') {
            steps {
                bat 'if exist reports\\allure-report rmdir /s /q reports\\allure-report'
                bat 'if exist reports\\allure-results rmdir /s /q reports\\allure-results'
                bat 'if not exist reports mkdir reports'
                bat 'if not exist reports\\allure-results mkdir reports\\allure-results'
                bat 'if exist screenshots rmdir /s /q screenshots & mkdir screenshots'
                bat 'if exist traces rmdir /s /q traces & mkdir traces'
                bat 'if exist logs rmdir /s /q logs & mkdir logs'
            }
        }

        stage('安装依赖') {
            steps {
                // venv 已存在则复用；CI 首次需创建
                bat 'if not exist .venv python -m venv .venv'
                bat '%PYTHON% -m pip install --upgrade pip -q'
                bat '%PYTHON% -m pip install -r requirements.txt -q'
                bat '%PYTHON% -m playwright install chromium'
            }
        }

        stage('静态检查') {
            steps {
                bat '%PYTHON% -m compileall -q api_auto common ui_auto integration conftest.py'
                bat '%PYTHON% -m pytest --collect-only -q'
            }
        }

        stage('执行全量测试') {
            steps {
                bat '%PYTHON% -m pytest api_auto\\testcases ui_auto\\testcases integration --alluredir=reports\\allure-results'
            }
        }

        stage('生成 Allure 报告') {
            steps {
                // 用命令行 allure 生成报告（Allure Jenkins 插件与当前 Jenkins 版本不兼容）
                bat '%ALLURE_BIN% generate reports\\allure-results -o reports\\allure-report --clean'
            }
        }
    }

    post {
        always {
            // 归档失败截图、trace、日志、Allure 报告
            archiveArtifacts artifacts: 'screenshots/**, traces/**, logs/**, reports/allure-report/**', allowEmptyArchive: true
            // 输出测试结果摘要到构建日志
            bat 'if exist reports\\allure-results echo Allure results generated successfully'
        }
        success {
            echo '✅ 全量测试通过，Allure 报告已生成'
        }
        failure {
            echo '❌ 存在失败用例，请查看截图、trace 和 Allure 报告'
        }
    }
}
