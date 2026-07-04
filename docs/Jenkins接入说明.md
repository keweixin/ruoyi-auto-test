# Jenkins 接入说明

> 记录如何在本机把 Jenkins 跑起来并接入 ruoyi-auto-test 测试项目。
>
> 适合：复现环境、排查问题、后续让 UI 测试也能在 Jenkins 跑通。

---

## 一、环境前提

| 项 | 值 |
|---|---|
| Jenkins war | `C:\Users\Administrator\jenkins.war`（v2.541.2） |
| JENKINS_HOME | `E:\jenkins\home` |
| Java | JDK 17（`java -version` 确认） |
| 被测系统 | 后端 48080 / 前端 80 / MySQL 3306 / Redis 6379（都在本机） |
| Allure | `E:\allure-2.37.0\allure-2.37.0\bin\allure.bat` |
| jcli | `E:\jenkins\jcli.exe`（Jenkins CLI 管理工具，可选） |

---

## 二、启动 Jenkins

### 首次启动（带引导向导）

```bash
mkdir -p /e/jenkins/home
JENKINS_HOME=/e/jenkins/home java -Djenkins.install.runSetupWizard=true \
  -jar /c/Users/Administrator/jenkins.war --httpPort=8080 > /e/jenkins/jenkins.log 2>&1 &
```

初始密码在 `E:\jenkins\home\secrets\initialAdminPassword`，或日志里搜 `Please use the following password`。

### 后续启动（跳过引导）

```bash
JENKINS_HOME=/e/jenkins/home java -Djenkins.install.runSetupWizard=false \
  -jar /c/Users/Administrator/jenkins.war --httpPort=8080 > /e/jenkins/jenkins.log 2>&1 &
```

访问 `http://localhost:8080`，用户名 `admin`，密码同初始密码。

### 停止

```bash
# 找监听 8080 的 PID
netstat -ano | grep "LISTENING" | grep ":8080"
# 杀掉（Windows）
taskkill //PID <PID> //F
```

> **注意**：Windows 上 Jenkins 不支持 `safe-restart`（`Default Windows lifecycle does not support restart`），改配置后需手动停进程再启动。

---

## 三、已安装的插件

| 插件 | 状态 | 用途 |
|------|------|------|
| git | ✅ 已装 | 从 GitHub 拉代码 |
| workflow-cps / workflow-job | ✅ 已装 | Pipeline 引擎 |
| pipeline-model-definition | ✅ 已装 | 声明式 Pipeline（`pipeline {}` 语法） |
| pipeline-stage-view | ✅ 已装 | 阶段视图 |
| credentials / credentials-binding | ✅ 已装 | 凭据管理 |
| ws-cleanup | ✅ 已装 | 工作区清理 |
| **allure-jenkins-plugin** | ❌ 未装 | 与 Jenkins 2.541 不兼容（`AllureXStreamAliases` 错误） |

> Allure 报告改用命令行 `allure.bat` 生成，不依赖插件。

### 安装插件（命令行）

```bash
PASS="<初始密码>"
java -jar /e/jenkins/jenkins-cli.jar -s http://localhost:8080 -auth "admin:$PASS" \
  install-plugin <plugin-name> -deploy
```

> 装完插件需重启 Jenkins（Windows 上手动停进程再启动）。

---

## 四、已配置的 Credentials

8 个 secret-text 凭据（在 `Manage Jenkins > Credentials > System > Global` 查看）：

| ID | 值 |
|----|-----|
| ruoyi-base-url | http://localhost:48080 |
| ruoyi-web-url | http://localhost:80 |
| ruoyi-admin-username | admin |
| ruoyi-admin-password | admin123 |
| ruoyi-db-host | 127.0.0.1 |
| ruoyi-db-user | root |
| ruoyi-db-password | 123456 |
| ruoyi-db-name | ruoyi-vue-pro |

Jenkinsfile 通过 `credentials('ruoyi-xxx')` 注入为环境变量，`config.py` 优先读环境变量。

---

## 五、Pipeline 任务

- **任务名**：`ruoyi-auto-test`
- **类型**：Pipeline（从 GitHub 拉 Jenkinsfile）
- **SCM**：`https://github.com/keweixin/ruoyi-auto-test.git`，分支 `master`
- **Jenkinsfile**：仓库根目录，Windows 兼容版本（`bat` 代替 `sh`）

### 流水线阶段

```
拉取代码 → 清理历史产物 → 安装依赖 → 静态检查 → 执行全量测试 → 生成 Allure 报告
```

### 触发构建

- 浏览器：`http://localhost:8080/job/ruoyi-auto-test/` 点"立即构建"
- 命令行：
  ```bash
  java -jar /e/jenkins/jenkins-cli.jar -s http://localhost:8080 -auth "admin:$PASS" \
    build ruoyi-auto-test
  ```

---

## 六、当前构建状态

### Build #6 结果：全部通过 ✅

| 测试类型 | 结果 |
|----------|------|
| API 接口测试 | ✅ 75 passed |
| UI 自动化测试 | ✅ 64 passed |
| 接口联动测试 | ✅ 20 passed |
| **合计** | ✅ **159 passed in 196s** |

流水线 6 阶段全部成功，Allure 报告已生成。

### 之前的 UI 失败问题及修复

Build #3 时 UI 测试全部超时失败（55 errors + 5 failed），根因和修复如下：

**根因**：Vite dev server 首次编译路由 chunk 较慢，conftest 的登录态创建链路（`LoginPage.wait_logged_in` 的 `wait_for_url`）默认 15s 超时不够。

**修复**（commit `f56faa4`，用 `CI` 环境变量开关，本地默认不受影响）：

| 文件 | 改动 |
|------|------|
| `conftest.py` | `browser` fixture：CI 下 `chromium.launch` 加 `--no-sandbox` 等 headless 稳定性参数 |
| `ui_auto/pages/login_page.py` | `wait_logged_in`：CI 下超时 15s → 40s |
| `ui_auto/auth/auth_state_manager.py` | `new_authenticated_page`：CI 下 `goto` 用 `domcontentloaded` + 30s 超时 |
| `ui_auto/base/base_page.py` | `open`：CI 下 `goto` 用 `domcontentloaded` + 30s |
| `Jenkinsfile` | `environment` 加 `CI = '1'` 触发宽松分支 |

**修复要点**：
1. `wait_until="domcontentloaded"` 代替默认 `"load"`——不等所有资源（字体、图片）加载完，dev server 首编时 `load` 事件会很慢
2. 超时从 15s 放宽到 30-40s——dev server 首次编译路由 chunk 需要时间
3. `--no-sandbox` 等 args——headless Chromium 在服务会话下的稳定性

**另一个修复**（commit `55f4889`）：Jenkinsfile 清理阶段的 `rmdir /s /q ... & mkdir ...` 串联命令有时序竞态（rmdir 未完成 mkdir 就执行），导致 `allure-results` 目录丢失，pytest 写 allure 结果时 `FileNotFoundError`。改为每条命令单独执行。

---

## 七、后续手动配置（如需）

### 重装 Allure 插件（待其适配新版 Jenkins）

若 Allure 插件出新版支持 Jenkins 2.541：
```bash
java -jar /e/jenkins/jenkins-cli.jar -s http://localhost:8080 -auth "admin:$PASS" \
  install-plugin allure-jenkins-plugin -deploy
# 手动重启 Jenkins
```
然后把 Jenkinsfile 的"生成 Allure 报告"阶段改回 `allure includeProperties: false, results: [[path: 'reports/allure-results']]`。

### 配置 GitHub Webhook（推送自动触发）

1. Jenkins 装 GitHub Integration Plugin
2. 任务配置 > 构建触发器 > 勾选 GitHub hook trigger
3. GitHub 仓库 > Settings > Webhooks > 添加 `http://<你的IP>:8080/github-webhook/`

---

## 八、常见问题

### Q: `No such DSL method 'pipeline' found`
**A**: 没装声明式 Pipeline 插件。装 `pipeline-model-definition` 后重启 Jenkins。

### Q: `Invalid option type "timestamps"`
**A**: 没装 timestamper 插件。从 Jenkinsfile 的 options 删掉 `timestamps()`，或装该插件。

### Q: `Default Windows lifecycle does not support restart`
**A**: Windows 上 Jenkins 不支持 `safe-restart`。手动 `taskkill //PID <PID> //F` 后重新 `java -jar jenkins.war` 启动。

### Q: credentials 值在日志里显示为 `****`
**A**: Jenkins 自动 mask secret 值，正常现象，不影响环境变量注入。

### Q: 构建卡在"安装依赖"很久
**A**: 首次构建要创建 venv + pip install + playwright install chromium，约 3-5 分钟。后续构建复用 venv 会快很多。
