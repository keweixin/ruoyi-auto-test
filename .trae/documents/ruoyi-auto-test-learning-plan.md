# RuoYi-Vue-Pro 接口/UI 自动化测试项目 — 系统学习计划

> **目标读者**：基础较薄弱、希望把本项目真正跑通、看懂、讲清，并能在简历中自信描述的同学。
> **最终目标**：达到“能跑通、能看懂、能讲清、能改简单用例、能排查常见问题”的水平，并能在面试中深入讲解项目架构与技术细节。
> **学习方式**：先看再跑、先懂再改、每次只前进一小步。

---

## 0. 一句话讲清这个项目

本项目是一个用 **Python + pytest + requests + Playwright** 搭建的**综合自动化测试工程**，专门测试 RuoYi-Vue-Pro（若依）后台管理系统；它把接口测试、UI 测试、数据库校验、持续集成（Jenkins）、Allure 报告整合在一起，目的是让测试可以自动、稳定、可重复地运行。

---

## 1. 学习目标与验收标准

### 1.1 总体目标

| 能力维度 | 学完应达到 |
|---|---|
| 跑通 | 能独立启动被测系统，配置测试环境，运行 API/UI/Integration 三类测试并生成 Allure 报告 |
| 看懂 | 能说出任意一个用例从 fixture → client/page → base → common 的完整调用链 |
| 讲清 | 能用 5~10 分钟向面试官讲解项目架构、亮点、技术选型原因 |
| 改用例 | 能根据需求新增/修改一条简单接口或 UI 用例，并正确运行 |
| 排查问题 | 遇到连接失败、401、超时、数据残留等常见报错，能定位到原因并解决 |

### 1.2 验收标准（必须全部完成）

1. 本地执行 `pytest --collect-only -q` 能收集到约 205 个测试实例。
2. 本地执行 `pytest -q` 全量测试全部通过（需被测系统启动）。
3. 能独立画出项目四层架构图并标注关键文件。
4. 能逐行讲解 `api_auto/testcases/test_auth_api.py` 中任意一个用例。
5. 能逐行讲解 `conftest.py` 中 `token_manager`、`page`、`fresh_page` 三个 fixture 的作用。
6. 能口述 Jenkinsfile 每个 stage 的作用。
7. 能写出简历中本项目的技术描述（限 150 字以内）。

---

## 2. 项目全景：它测的是什么、怎么测的

### 2.1 被测系统 RuoYi-Vue-Pro 是什么

**人话解释**：RuoYi-Vue-Pro 是一个开源的“后台管理系统模板”，就像很多公司里的 OA、ERP、权限管理平台。它包含：
- 登录认证
- 部门管理
- 岗位管理
- 用户管理
- 角色管理
- 菜单权限
- 字典管理
- 日志/通知公告/个人中心

**为什么选它**：模块典型、接口完整、有真实前端页面，非常适合练习接口/UI/数据库/权限/CI/CD 等综合能力。

### 2.2 系统架构（真实环境）

```text
浏览器 / Playwright
   │  访问 http://localhost:80
   ▼
前端 Vue3 + Element Plus + Vite（yudao-admin-vue3）
   │  通过 /admin-api 调用后端接口
   ▼
后端 Spring Boot（端口 48080）
   │  JDBC 读写数据库；Redis 做缓存/验证码/token
   ▼
MySQL（端口 3306，库 ruoyi-vue-pro）   Redis（端口 6379）
```

**关键约定**（项目里到处用到，必须背熟）：

| 项 | 值 | 在哪里用到 |
|---|---|---|
| 后端地址 | `http://localhost:48080` | `common/config.py` 中 `base_url` |
| 管理端前缀 | `/admin-api` | `api_auto/base/base_api.py` 中 `ADMIN_API_PREFIX` |
| 前端地址 | `http://localhost:80` | `common/config.py` 中 `web_url` |
| 登录接口 | `POST /admin-api/system/auth/login` | `api_auto/clients/auth_client.py` |
| 成功业务码 | `code == 0` | `common/assert_utils.py` 中 `assert_api_ok` |
| Token 字段 | `data.accessToken` | `api_auto/auth/token_manager.py` |
| 鉴权头 | `Authorization: Bearer <accessToken>` | `api_auto/base/base_api.py` 中 `get_headers` |
| 租户头 | `tenant-id: 1` | `api_auto/base/base_api.py` 中 `get_headers` |

### 2.3 测试项目架构（核心）

```text
Testcases 测试用例层（api_auto/ui_auto/integration）
   │
   ▼
Clients / Pages 业务封装层（api_auto/clients / ui_auto/pages）
   │
   ▼
BaseApi / BasePage 基础封装层（api_auto/base / ui_auto/base）
   │
   ▼
Common 公共能力层（common/）
   │
   ▼
配置与基础设施（data/env.yaml、环境变量、TokenManager、AuthStateManager）
```

**分层职责**（面试必背）：

| 层 | 代表文件 | 职责 |
|---|---|---|
| 用例层 | `api_auto/testcases/test_auth_api.py` | 只表达测试逻辑：准备 → 执行 → 断言 → 清理 |
| 业务封装层 | `api_auto/clients/auth_client.py` | 把业务动作封装成方法，如 `login()`、`create()` |
| 基础封装层 | `api_auto/base/base_api.py` | 统一处理请求头、Token、日志、重试、Allure 附件 |
| 公共能力层 | `common/config.py`、`common/db_utils.py` | 配置读取、日志、数据库、断言、数据清理 |
| 基础设施 | `api_auto/auth/token_manager.py` | Token 生命周期管理、UI 登录态快照 |

### 2.4 测试范围统计

| 类型 | 数量 | 目录 | 说明 |
|---|---|---|---|
| API 接口测试 | 103 | `api_auto/testcases/` | 10 个模块：登录/部门/字典/菜单/岗位/角色/用户/日志/个人中心/通知公告 |
| UI 自动化测试 | 70 | `ui_auto/testcases/` | 基于 Playwright + Page Object |
| 接口联动 / DB 校验 | 20 | `integration/` | 接口造数 → 接口查询 → 数据库校验 → 清理 |
| 框架单测 | 12 | `tests/` | BaseApi HTTP 客户端 + common 工具 |
| **合计** | **205** | | `pytest --collect-only -q` 验证 |

---

## 3. 基础知识补课清单（必须先补）

本项目涉及多个技术栈，如果以下概念完全陌生，需要先花 1~2 天补课。

### 3.1 HTTP / 接口基础

- **HTTP 方法**：GET、POST、PUT、DELETE 分别是什么含义。
- **HTTP 状态码**：200、401、403、404、500 分别代表什么。
- **Header / Body / Query Param**：请求由哪些部分组成。
- **JSON**：接口返回的数据格式，学会用 `response.json()` 取值。
- **Token 鉴权**：为什么登录后要拿到 token，后续请求要带 `Authorization: Bearer xxx`。

**项目里的学习位置**：
- `api_auto/clients/auth_client.py`：看登录、退出、刷新 token 的接口。
- `api_auto/base/base_api.py`：看 `get_headers()` 怎么把 token 塞进请求头。
- `api_auto/testcases/test_auth_api.py`：看登录成功/失败/未带 token 的用例。

**动手任务**：
1. 用 Postman 或 curl 调一次登录接口，拿到 `accessToken`。
2. 再用这个 token 调一次 `/admin-api/system/auth/get-permission-info`。

### 3.2 Python 基础

- 字典 `dict`、列表 `list`、字符串操作。
- 函数定义、类 `class`、`self` 的含义。
- `with` 上下文管理器。
- `pytest` 基本用法：`pytest -v`、`-k`、`-m`、`-q`。
- `pytest fixture`：理解 `@pytest.fixture`、`scope="session"`、`autouse=True`。

**项目里的学习位置**：
- `conftest.py`： fixture 大集合，逐个读。
- `common/assert_utils.py`：看简单的断言函数怎么写。

**动手任务**：
1. 写一个小脚本 `login_demo.py`：用 `requests.post` 登录并打印 token。
2. 写一个小测试 `test_demo.py`：用 `pytest` 跑一个 `assert 1 + 1 == 2`。

### 3.3 SQL 基础

- `SELECT / WHERE / ORDER BY / LIMIT`
- `INSERT / UPDATE / DELETE`
- `JOIN` 多表查询
- `COUNT / GROUP BY`

**项目里的学习位置**：
- `common/db_utils.py`：看怎么连 MySQL、查数据、断言字段。
- `common/cleanup_utils.py`：看清理 SQL 怎么写。
- `integration/test_role_permission_flow.py`：看数据库校验怎么用。

**动手任务**：
1. 用 mysql 客户端连上 `ruoyi-vue-pro` 库。
2. 执行 `SELECT * FROM system_users WHERE username = 'admin';`
3. 执行 `SELECT * FROM system_role_menu WHERE role_id = 1;`

### 3.4 Linux / 命令行基础

- `cd`、`ls`、`pwd`、`cp`、`mv`、`rm`、`mkdir`
- `grep`、`find`、`tail`、`head`
- `ps`、`netstat`、`lsof`
- 查看日志：`tail -f logs/test.log`

**项目里的学习位置**：
- `docs/项目运行说明.md`：所有启动命令都在这里。
- `scripts/run_*.bat`：Windows 批处理一键脚本。

### 3.5 Git 基础

- `git status`、`git log`、`git diff`
- 分支概念

**为什么需要**：项目用 Git 管理，Jenkins 从 GitHub 拉代码。

---

## 4. 分阶段学习计划（建议 3~4 周完成）

### Phase 0：环境准备（第 1 天）

**目标**：让被测系统和测试项目都能跑起来。

**步骤**：

1. **启动 MySQL**
   - 用 Docker 或本机 MySQL，确保 3306 端口可连。
   - 创建数据库 `ruoyi-vue-pro` 并导入初始化 SQL。
   - 验证：`mysql -uroot -p123456 -e "SELECT 1 FROM ruoyi-vue-pro.system_users LIMIT 1;"`

2. **启动 Redis**
   - 确保 6379 端口可连。
   - 验证：`redis-cli ping` 返回 `PONG`。

3. **启动后端**
   - 进入 RuoYi-Vue-Pro / yudao-server 目录。
   - 修改 `application-local.yaml` 中数据库连接。
   - 运行 `mvn spring-boot:run` 或在 IDEA 中启动。
   - **关键**：确保 `yudao.captcha.enable=false`（测试登录依赖验证码关闭）。
   - 验证：curl 登录接口返回 200 且包含 `accessToken`。

4. **启动前端**
   - 进入 `yudao-admin-vue3` 目录。
   - `pnpm install`、`pnpm dev`。
   - 验证：`curl http://localhost:80` 返回 200。

5. **安装测试项目依赖**
   ```bash
   cd E:/ruoyi/test/ruoyi-auto-test
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

6. **配置环境**
   - 复制 `data/env.example.yaml` 为 `data/env.yaml`，按本地环境修改。
   - 或设置环境变量（见 README）。

7. **一键自检**
   ```bash
   pytest --collect-only -q
   # 期望收集到约 205 个 tests
   ```

** checkpoint 0**：
- [ ] 后端 48080、前端 80、MySQL 3306、Redis 6379 全部可访问。
- [ ] `pytest --collect-only -q` 成功收集 205 个用例。

---

### Phase 1：项目骨架与入口（第 2~3 天）

**目标**：能说出项目每个目录/文件是干什么的，找到任意代码的位置。

**学习内容**：

1. **根目录文件**
   - `README.md`：项目总览、技术栈、运行方式。
   - `pytest.ini`：pytest 配置、markers 定义、测试路径。
   - `requirements.txt`：依赖包及版本。
   - `Jenkinsfile`：CI/CD 流水线定义。
   - `conftest.py`：全局 fixture。

2. **目录结构**
   - `api_auto/`：接口自动化。
   - `ui_auto/`：UI 自动化。
   - `integration/`：接口联动 + 数据库校验。
   - `common/`：公共工具。
   - `data/`：YAML 测试数据。
   - `docs/`：文档、缺陷报告、面试稿。
   - `jmeter/`：性能测试计划。
   - `scripts/`：Windows 一键脚本。

3. **关键配置**
   - `pytest.ini` 中 `markers` 的含义：smoke、api、ui、flow、db、framework。
   - `pytest.ini` 中 `addopts` 的含义：`-v`、`--strict-markers`、`--alluredir`。

**动手任务**：
1. 打开 `pytest.ini`，用中文解释每一行的作用。
2. 打开 `requirements.txt`，逐个查这些包是干什么的（如 requests、Playwright、allure-pytest、pymysql）。
3. 用 `pytest -m api` 跑一次只含 API 的用例，观察输出。

**Checkpoint 1**：
- [ ] 能不看文档说出 8 个以上目录/文件的作用。
- [ ] 能用 `-m` 参数按标记运行用例。

---

### Phase 2：公共层 Common 深度理解（第 4~6 天）

**目标**：理解所有“底层工具”是怎么被上层调用的。

**学习内容**：

1. **配置读取** `common/config.py`
   - 什么是环境变量？为什么 CI 环境优先用环境变量？
   - 本地开发为什么用 `data/env.yaml`？
   - `os.getenv` 与 YAML 回退逻辑。
   - 敏感信息（密码）为什么不提交 Git？`.gitignore` 怎么配置？

2. **日志** `common/logger.py`
   - `logging` 与 `print` 的区别。
   - 日志级别：INFO、WARNING、ERROR。
   - 日志输出到控制台和 `logs/test.log`。

3. **数据库工具** `common/db_utils.py`
   - `pymysql.connect` 怎么建立连接。
   - `DictCursor` 是什么意思（返回字典而不是元组）。
   - `%s` 占位符防止 SQL 注入。
   - `query_one`、`query_all`、`execute`、`assert_db_record` 四个函数的区别。

4. **断言工具** `common/assert_utils.py`
   - 为什么 RuoYi 的接口不能只看 HTTP 200，要看 `code == 0`。
   - `assert_api_ok`、`assert_api_fail`、`assert_response_ok`、`assert_page_result` 的用法。

5. **Allure 附件** `common/allure_utils.py`
   - 什么是 Allure？它是测试报告工具。
   - `attach_text`、`attach_json`、`attach_png` 分别附加什么。

6. **随机数据** `common/random_utils.py` + `common/test_data.py`
   - 为什么测试数据要随机？避免重名、支持并发、便于清理。
   - `TEST_RUN_PREFIX` 是什么？为什么每轮运行前缀唯一？
   - `gen_name`、`gen_username`、`gen_mobile` 怎么用。
   - `CreatedEntity` 是什么？`with_created_entity` 上下文管理器怎么用。

7. **数据清理** `common/cleanup_utils.py`
   - 为什么清理要先清关系表再清主表？
   - `deleted=1` 是什么意思？（逻辑删除，不是物理删除）
   - 为什么范围限制在 `TEST_RUN_PREFIX` 内？

8. **安全/脱敏** `common/security_utils.py`（选读）
   - 为什么日志里不能打印明文密码？
   - `mask_dict`、`mask_headers` 的作用。

**动手任务**：
1. 在 `common/config.py` 的 `Config` 类里加一行 `print`，看启动时读到了哪些配置（用完删掉）。
2. 用 `common/db_utils.py` 中的 `query_one` 查询 admin 用户的 `username` 和 `nickname`。
3. 用 `common/random_utils.py` 生成 5 个随机用户名，观察规律。

**Checkpoint 2**：
- [ ] 能解释环境变量与 YAML 配置的优先级。
- [ ] 能用 `db_utils.query_one` 写一条查询并拿到结果。
- [ ] 能解释 `TEST_RUN_PREFIX` 的作用和生成规则。

---

### Phase 3：接口自动化层 API Auto（第 7~11 天）

**目标**：能独立看懂/修改/新增一条接口测试用例。

#### 3.1 Token 管理（核心难点）

**学习文件**：
- `api_auto/auth/token_manager.py`
- `api_auto/clients/auth_client.py`
- `common/token_registry.py`

**必须理解的概念**：

1. **access token 与 refresh token**
   - 登录后拿到两个 token：`accessToken`（短期有效）和 `refreshToken`（长期有效）。
   - 后续请求带 `accessToken`。
   - `accessToken` 快过期时，用 `refreshToken` 换一个新的，避免频繁登录。

2. **TokenManager 做了什么**
   - 整轮测试共享一个 token。
   - `get_access_token()`：如果 token 没过期直接返回；快过期则刷新；刷新失败则重新登录。
   - 用 `threading.RLock` 保证多线程安全（xdist 并行时多个 worker）。
   - `invalidate_access_token()`：标记失效，下次请求会刷新。

3. **401 自动恢复**
   - `BaseApi._is_unauthorized()`：兼容 HTTP 401 和业务码 401（RuoYi 用 HTTP 200 + code=401 包装鉴权失败）。
   - 当接口返回 401 时，`BaseApi.request()` 会让 TokenManager 刷新并重试一次。

4. **TokenRegistry**
   - 记录本轮测试产生的所有 token。
   - session 结束时调用 logout 回收，避免 Redis/MySQL 里残留大量测试 token。

**动手任务**：
1. 在 `test_auth_api.py` 里找到 `test_refresh_token` 和 `test_retry_after_unauthorized`，逐行看懂。
2. 手动模拟：把 `token_manager.access_token` 改成错误值，看测试能不能自动恢复。

#### 3.2 BaseApi 请求封装

**学习文件**：`api_auto/base/base_api.py`

**关键知识点**：

1. **Session 复用**：`requests.Session()` 复用 TCP 连接，提高性能。
2. **重试机制**：只对 GET/HEAD/OPTIONS 等安全方法重试；POST/PUT/DELETE 不重试，避免重复提交。
3. **超时设置**：`DEFAULT_TIMEOUT = (3.05, 15)`，3.05 秒连接超时，15 秒读取超时。
4. **统一前缀**：构造时自动补 `/admin-api`。
5. **日志 + Allure 附件**：每次请求和响应都记录到日志和 Allure（脱敏后）。
6. **文件上传/下载**：`upload()`、`download()` 方法。

**动手任务**：
1. 在 Python 交互式环境里创建一个 `AuthClient` 并调用 `login()`，观察返回的 response。
2. 阅读 `_send()` 和 `request()`，画出调用流程图。

#### 3.3 Client 业务封装

**学习文件**：
- `api_auto/clients/auth_client.py`
- `api_auto/clients/user_client.py`
- `api_auto/clients/role_client.py`
- `api_auto/clients/dept_client.py`
- `api_auto/clients/dict_client.py`

**关键知识点**：
- 每个 Client 继承 `BaseApi`。
- 每个 Client 封装一个业务模块的接口，如 `UserClient.create()`、`RoleClient.delete()`。
- Client 构造时传入 `token_manager`，无需每个方法都传 token。

**动手任务**：
1. 打开 `user_client.py`，列出它封装了哪些接口方法。
2. 对比 `test_user_api.py`，看用例怎么调用 client。

#### 3.4 接口测试用例

**学习文件**：`api_auto/testcases/test_auth_api.py`、`test_user_api.py`、`test_role_api.py`

**关键知识点**：
- `@allure.feature` / `@allure.story` / `@allure.title`：Allure 报告里的层级。
- `@pytest.mark.api`：pytest marker。
- `@pytest.mark.parametrize`：参数化，一条用例跑多组数据。
- `assert_schema()`：JSON Schema 校验响应结构。
- YAML 数据驱动：`data/login_data.yaml`。

**动手任务**：
1. 逐行讲解 `test_auth_api.py` 中的 `test_login_success`。
2. 在 `data/login_data.yaml` 里加一条自己的测试数据，重新运行看效果。
3. 仿照 `test_user_api.py` 新增一条“创建用户后查询”的用例。

**Checkpoint 3**：
- [ ] 能解释 TokenManager 的刷新与重试机制。
- [ ] 能手写一条新的接口测试用例（使用 client + assert_api_ok）。
- [ ] 能解释 `@pytest.mark.parametrize` 和 YAML 数据驱动。

---

### Phase 4：UI 自动化层 UI Auto（第 12~16 天）

**目标**：理解 Page Object 模式，能看懂并修改 UI 用例。

#### 4.1 Playwright 基础

**先补概念**：
- 什么是浏览器自动化？用代码模拟人的点击、输入、截图。
- `browser`：浏览器进程。
- `context`：浏览器上下文，类似“隐身窗口”，隔离 cookie/localStorage。
- `page`：一个标签页。
- `locator`：元素定位器。

#### 4.2 BasePage 公共能力

**学习文件**：`ui_auto/base/base_page.py`

**关键方法**：
- `open(url)`：打开页面。
- `click()` / `fill()`：点击、输入。
- `wait_visible()` / `wait_url()` / `wait_path()`：等待元素或页面状态。
- `toast_text()` / `expect_toast()`：Element Plus 的消息提示。
- `click_menu()`：点击左侧菜单。
- `table_row_count()` / `table_has_row()` / `table_row_by_keyword()`：表格操作。
- `dialog_submit()` / `messagebox_confirm()`：处理弹窗。
- `click_and_wait_response()`：点击并等待某个接口返回。

**关键知识点**：
- 为什么不能用 `time.sleep()`？因为等待时间不确定，会拖慢测试。
- Playwright 的 `expect` 是什么？自动轮询直到条件满足或超时。
- 语义化定位：`get_by_role`、`get_by_text`、`get_by_placeholder`，比 CSS/XPath 更稳定。

#### 4.3 登录态管理

**学习文件**：
- `ui_auto/auth/auth_state_manager.py`
- `ui_auto/pages/login_page.py`
- `conftest.py` 中 `browser`、`auth_state_manager`、`page`、`fresh_page` fixture。

**关键知识点**：
- 什么是 `storage_state`？Playwright 把登录后的 cookie/localStorage 存成 JSON 文件，后续用例直接复用，不用每次都登录。
- `AuthStateManager.create_state()`：登录一次并保存状态。
- `new_authenticated_page()`：用状态文件创建已登录页面；如果失效自动重新登录。
- `fresh_page`：没有登录态的页面，专门用于测试登录流程。

#### 4.4 Page 业务封装

**学习文件**：
- `ui_auto/pages/login_page.py`
- `ui_auto/pages/home_page.py`
- `ui_auto/pages/user_page.py` / `dept_page.py` / `dict_page.py`

**关键知识点**：
- Page Object 模式：把每个页面的元素定位和业务动作封装成类。
- 用例层只写流程：打开页面 → 调用 page 方法 → 断言。
- Vue3 + Element Plus 常见组件：`.el-table`、`.el-dialog`、`.el-form-item.is-error`、`.el-message`。

#### 4.5 UI 测试用例

**学习文件**：`ui_auto/testcases/test_login_ui.py`、`test_user_ui.py`

**动手任务**：
1. 用 `pytest ui_auto/testcases/test_login_ui.py -v --headed` 看浏览器实时操作。
2. 用 `--slowmo 500` 放慢操作，观察每一步。
3. 在 `login_page.py` 中找一个 locator，改成另一种定位方式（如 `get_by_placeholder` 改为 `get_by_label`），看是否还能跑通。
4. 新增一条 UI 用例：登录后点击“系统管理”菜单，断言某个子菜单存在。

**Checkpoint 4**：
- [ ] 能解释 browser / context / page / locator 的关系。
- [ ] 能解释 storage_state 登录态复用的意义。
- [ ] 能手写一条简单的 UI 用例（使用 Page Object）。

---

### Phase 5：接口联动与数据库校验 Integration（第 17~19 天）

**目标**：理解“接口造数 + 数据库校验 + 清理”的闭环。

**学习文件**：
- `integration/test_role_permission_flow.py`
- `integration/test_user_api_ui_flow.py`
- `integration/test_dept_ui_api_db_flow.py`

**关键知识点**：
1. **为什么做数据库校验**：接口返回成功不等于数据正确落库。
2. **联动流程**：
   - 接口创建数据（造数）
   - 接口查询验证
   - 数据库 `system_*` 表校验
   - 接口删除 / 逻辑删除（清理）
3. **权限关系表**：
   - `system_role`：角色主表。
   - `system_role_menu`：角色菜单关系。
   - `system_user_role`：用户角色关系。
   - `system_users`：用户主表。

**动手任务**：
1. 逐行讲解 `test_role_permission_flow.py::test_api_create_role_with_menus`。
2. 手动在 MySQL 里查询 `system_role_menu`，对比用例中断言是否一致。
3. 新增一条联动用例：创建部门 → 数据库校验 `system_dept` → 删除。

**Checkpoint 5**：
- [ ] 能说出 4 张以上 `system_*` 表的作用。
- [ ] 能手写一条“接口造数 + DB 校验 + 清理”的用例。

---

### Phase 6：报告与失败定位（第 20~21 天）

**目标**：能生成并解读 Allure 报告，能利用截图和 trace 定位失败。

**学习文件**：
- `common/allure_utils.py`
- `conftest.py` 中 `pytest_runtest_makereport` hook。
- `scripts/open_allure.bat`

**关键知识点**：
1. **Allure 是什么**：开源测试报告框架，能展示用例层级、步骤、附件、趋势。
2. **结果目录**：`reports/allure-results/` 是 pytest 生成的原始 JSON；`reports/allure-report/` 是 Allure 命令行生成的 HTML。
3. **失败截图**：用例失败时，`pytest_runtest_makereport` 自动截图并 attach 到 Allure。
4. **Playwright Trace**：失败时保存 `.zip` 文件，可用 `playwright show-trace trace.zip` 回放操作。
5. **为什么成功用例不保存 Trace**：避免产物太大。

**动手任务**：
1. 运行 `pytest api_auto/testcases/test_auth_api.py -q --alluredir=reports/allure-results`。
2. 运行 `allure serve reports/allure-results` 查看报告。
3. 故意改错一个断言，运行后观察失败截图和 trace。

**Checkpoint 6**：
- [ ] 能独立生成并打开 Allure 报告。
- [ ] 能根据 Allure 报告和 trace 定位一条失败用例。

---

### Phase 7：CI/CD 与 DevOps（第 22~25 天）

**目标**：理解 Jenkinsfile 每个阶段，能在简历中讲清持续集成。

#### 7.1 什么是 CI/CD（大白话）

- **CI（Continuous Integration，持续集成）**：每次代码提交后，自动拉代码、编译、跑测试，尽早发现错误。
- **CD（Continuous Delivery/Deployment，持续交付/部署）**：测试通过后自动打包、发布到测试环境或生产环境。
- **Pipeline（流水线）**：把拉代码、安装依赖、跑测试、生成报告这些步骤串起来，像工厂流水线一样自动执行。
- **Agent**：Jenkins 执行任务的机器（可以是本机、服务器、容器）。
- **Artifact（产物）**：构建完成后保存的文件，如 Allure 报告、截图、日志。

#### 7.2 Jenkinsfile 逐阶段讲解

**学习文件**：`Jenkinsfile`

| 阶段 | 作用 | 对应命令 |
|---|---|---|
| `agent any` | 任意可用 agent 执行 |
| `options` | 保留最近 10 次构建、产物保留 5 次、超时 30 分钟 |
| `environment` | 通过 Jenkins credentials 注入环境变量（密码不外露） |
| `拉取代码` | `checkout scm` 从 Git 拉代码 |
| `清理历史产物` | 删除旧的 Allure 结果、截图、trace、日志，避免干扰 |
| `安装依赖` | 创建/复用 `.venv`，安装 requirements，安装 chromium |
| `静态检查` | `compileall` 检查语法，`pytest --collect-only` 检查用例可加载 |
| `执行全量测试` | 跑 API + UI + Integration |
| `生成 Allure 报告` | 用 `allure.bat` 生成静态 HTML 报告 |
| `post always` | 归档截图、trace、日志、Allure 报告 |
| `post success/failure` | 打印构建结果 |

**关键细节**：
- 为什么用 `credentials('ruoyi-base-url')`？避免密码明文写在代码里。
- 为什么设置 `CI = '1'`？触发代码里的 CI 宽松超时分支（Vite dev server 首编慢）。
- 为什么 `allure-jenkins-plugin` 没装？与 Jenkins 2.541 不兼容，所以改用命令行 `allure.bat`。

#### 7.3 Jenkins 接入实操

**学习文件**：`docs/Jenkins接入说明.md`

**动手任务**：
1. 阅读 `docs/Jenkins接入说明.md` 全篇。
2. 在本地启动 Jenkins（如果已安装），新建一个 Pipeline 任务，指向本项目的 Jenkinsfile。
3. 点击“立即构建”，观察每个 stage 的执行结果。
4. 下载构建产物中的 Allure 报告并打开。

**Checkpoint 7**：
- [ ] 能口述 Jenkinsfile 的 6 个 stage。
- [ ] 能解释为什么用 credentials 注入环境变量。
- [ ] 能解释 `CI='1'` 在项目里的作用。

---

### Phase 8：性能测试与简历包装（第 26~28 天）

#### 8.1 JMeter 性能测试

**学习文件**：
- `docs/JMeter性能测试操作文档.md`
- `jmeter/ruoyi_login_dict_perf.jmx`

**关键知识点**：
- JMeter 是 Apache 的性能测试工具，可以模拟多用户并发请求。
- 本项目性能测试场景：登录 → 提取 `accessToken` → 携带 token 查询字典类型分页。
- **注意**：当前只提供了方案和脚本，未做真实压测；简历中只能写“设计/编写 JMeter 性能测试方案”，不能写“完成压测并达标”。

**动手任务**：
1. 安装 JMeter，导入 `jmeter/ruoyi_login_dict_perf.jmx`。
2. 理解 Thread Group、HTTP Request、JSON Extractor、HTTP Header Manager 的作用。
3. 跑一次小并发（如 10 线程）观察结果，但不要对被测环境造成过大压力。

#### 8.2 简历包装指导

**项目简历写法（参考）**：

> 基于 RuoYi-Vue-Pro 前后端分离后台管理系统，使用 Python + pytest + requests + Playwright 搭建综合自动化测试框架；覆盖登录、用户、角色、菜单权限、部门、岗位、字典等 10 个模块；实现 205 条测试实例（接口 103 + UI 70 + 联动/DB 20 + 框架单测 12）；采用 Page Object、Token 生命周期管理、数据自清理、数据库校验、Allure 报告、Jenkins 流水线等工程化手段。

**可提炼的技术亮点**（面试时挑 3~4 个讲）：

| 亮点 | 对应文件/位置 | 适合表达的能力 |
|---|---|---|
| 接口/UI 分层覆盖 | `api_auto/`、`ui_auto/` | 自动化测试设计能力 |
| Token 生命周期管理 | `api_auto/auth/token_manager.py`、`api_auto/base/base_api.py` | 复杂鉴权场景处理 |
| 数据库校验 | `common/db_utils.py`、`integration/` | 数据一致性验证 |
| UI 登录态复用 | `ui_auto/auth/auth_state_manager.py` | UI 稳定性优化 |
| 失败定位 | `conftest.py` 中 screenshot + trace | 可观测性/排障 |
| Jenkins CI/CD | `Jenkinsfile` | DevOps/工程化 |
| 数据自清理 | `common/cleanup_utils.py`、`conftest.py` | 测试数据管理 |

**面试常问问题准备**（结合 `docs/面试讲解稿.md`）：
1. 为什么选择 RuoYi-Vue-Pro？
2. 接口自动化框架怎么设计？
3. UI 自动化框架怎么设计？
4. 接口和 UI 怎么配合？
5. 怎么处理 token？
6. 怎么处理测试数据？
7. 为什么要做数据库校验？
8. UI 自动化不稳定怎么办？
9. JMeter 性能测试怎么做？

**Checkpoint 8**：
- [ ] 能写出 150 字以内的项目简历描述。
- [ ] 能回答上述 9 个面试问题中的至少 6 个。
- [ ] 能用 JMeter 打开并理解 `.jmx` 文件结构。

---

## 5. 关键技术概念详解

### 5.1 pytest fixture

**人话**：fixture 是 pytest 的“测试工具人”，用例需要什么，fixture 就准备好什么。

**项目里的例子**：
- `token_manager`（session 级）：整轮测试只登录一次，所有 client 共享 token。
- `auth_client`（function 级）：每个用例开始时新建一个带 token 的 AuthClient。
- `page`（function 级）：每个用例给一个已登录的浏览器页面。
- `cleanup_after_test`（autouse=True）：每条用例结束后自动清理数据。

### 5.2 Page Object 模式

**人话**：把页面元素定位和操作封装成类，用例里不写裸定位代码，便于维护。

**项目里的例子**：
- `LoginPage` 封装了用户名输入框、密码输入框、登录按钮、登录方法。
- 用例里只写 `lp.login_as_admin()`，不用关心具体 selector。

### 5.3 数据驱动

**人话**：把测试数据放到 YAML/Excel/数据库里，用例代码只写一次，数据可以换多组。

**项目里的例子**：
- `data/login_data.yaml` 里有多组登录数据。
- `test_auth_api.py` 用 `@pytest.mark.parametrize` 读取这些数据。

### 5.4 逻辑删除

**人话**：不是真的从数据库删掉，而是把 `deleted` 字段从 0 改成 1；查询时默认不显示。

**项目里的例子**：
- `common/cleanup_utils.py` 中所有清理都是 `UPDATE ... SET deleted=1`。
- 断言时常常要查 `deleted + 0 AS deleted` 并断言为 0。

### 5.5 Token 鉴权

**人话**：登录后服务端给你一个“通行证”（token），你之后每次请求都要带上，服务端才知道你是谁。

**项目里的例子**：
- `BaseApi.get_headers()` 把 token 放到 `Authorization: Bearer xxx` 头里。
- `TokenManager` 负责在 token 过期前刷新。

### 5.6 DevOps / CI/CD

**人话**：
- **DevOps**：开发（Dev）和运维（Ops）紧密协作，让软件交付更快更稳。
- **CI**：每次提交代码自动构建、跑测试。
- **CD**：测试通过后自动部署。

**项目里的例子**：
- `Jenkinsfile` 就是 CI 的实践：代码提交 → 自动拉取 → 安装依赖 → 跑测试 → 生成报告 → 归档产物。

### 5.7 Allure 报告

**人话**：Allure 让测试结果更好看、更易懂。它能把用例分组、显示步骤、附加截图和日志。

**项目里的例子**：
- `common/allure_utils.py` 封装附件。
- 用例上的 `@allure.feature`、`@allure.story`、`@allure.title` 控制报告结构。

---

## 6. 实践任务清单（必须动手）

### 6.1 入门级任务

- [ ] 用 curl/Postman 调通登录接口。
- [ ] 用 Python 写 10 行脚本：登录并打印 token。
- [ ] 运行 `pytest api_auto/testcases/test_auth_api.py -v`。
- [ ] 查看 `logs/test.log` 里的请求日志。

### 6.2 进阶级任务

- [ ] 给 `api_auto/testcases/test_dept_api.py` 新增一条“创建部门后数据库校验”的用例。
- [ ] 修改 `data/login_data.yaml`，加一条自己的测试数据，运行验证。
- [ ] 用 `--headed` 运行一条 UI 用例，观察浏览器行为。
- [ ] 故意让一条 UI 用例失败，查看截图和 trace。

### 6.3 综合级任务

- [ ] 在 Jenkins 上手动触发一次构建，观察 Pipeline 执行。
- [ ] 修改 Jenkinsfile 增加一个“只跑 smoke 用例”的 stage（高风险，先备份）。
- [ ] 用 JMeter 跑一次登录+字典查询脚本。
- [ ] 整理一份自己的“项目讲解稿”，限时 8 分钟讲清楚。

---

## 7. 知识检查点安排

| 检查点 | 时间 | 内容 | 通过标准 |
|---|---|---|---|
| CP0 | 第 1 天 | 环境跑通 | 被测系统 4 个服务 + pytest collect 成功 |
| CP1 | 第 3 天 | 项目骨架 | 能说出 8+ 目录/文件作用，会用 marker 跑用例 |
| CP2 | 第 6 天 | Common 层 | 会用 db_utils 查数据，理解配置和随机前缀 |
| CP3 | 第 11 天 | API 层 | 能手写接口用例，理解 TokenManager |
| CP4 | 第 16 天 | UI 层 | 能手写 UI 用例，理解 Page Object 和 storage_state |
| CP5 | 第 19 天 | Integration | 能手写“接口+DB+清理”联动用例 |
| CP6 | 第 21 天 | 报告 | 能生成 Allure 报告并定位失败 |
| CP7 | 第 25 天 | CI/CD | 能口述 Jenkinsfile 各 stage，理解 credentials |
| CP8 | 第 28 天 | 简历/面试 | 能写出简历描述并回答 6/9 个面试题 |

**建议**：每到一个 checkpoint，自己给自己讲一遍，录音或写笔记；讲不清楚的地方回炉重学。

---

## 8. 常见问题排查手册

### 8.1 后端连接失败

- 现象：`ConnectionRefusedError: 48080`
- 检查：后端是否启动？端口是否正确？
- 命令：`curl http://localhost:48080/admin-api/system/auth/login -X POST ...`

### 8.2 前端连接失败

- 现象：`page.goto: net::ERR_CONNECTION_REFUSED`
- 检查：前端是否启动？`http://localhost:80` 是否可访问？

### 8.3 登录失败 code != 0

- 检查：验证码是否关闭？账号密码是否正确？
- 位置：后端 `application-local.yaml` 中 `yudao.captcha.enable=false`。

### 8.4 数据库连接失败

- 现象：`pymysql.err.OperationalError`
- 检查：`data/env.yaml` 中密码、端口、库名是否正确？MySQL 是否启动？

### 8.5 Allure 报告空白

- 原因：直接用 `file://` 打开 `index.html` 会被浏览器安全策略阻止。
- 解决：用 `allure serve reports/allure-results` 或 `allure open reports/allure-report`。

### 8.6 测试数据残留

- 解决：手动执行 SQL 清理 `auto_%` 前缀数据。
- 长期：检查 `cleanup_after_test` fixture 是否生效。

---

## 9. 学习资源与下一步

### 9.1 项目内必读文档

| 文档 | 作用 |
|---|---|
| `README.md` | 项目总览 |
| `docs/项目运行说明.md` | 环境搭建与运行 |
| `docs/01_项目理解.md` | 被测系统与测试范围 |
| `docs/面试讲解稿.md` | 面试问题参考答案 |
| `docs/基础能力学习清单.md` | 前置知识查漏 |
| `docs/Jenkins接入说明.md` | Jenkins 实操 |
| `docs/JMeter性能测试操作文档.md` | JMeter 实操 |

### 9.2 推荐外部资源

- pytest 官方文档（学习 fixture、marker、parametrize）
- Playwright 官方文档（学习 locator、trace、storage_state）
- requests 官方文档（学习 Session、重试）
- 菜鸟教程 / 廖雪峰 Python 教程（补 Python 基础）
- W3Cschool SQL 教程（补 SQL 基础）

### 9.3 提问清单（学到这里应该能问出好问题）

- 为什么 `TokenManager` 用 `RLock` 而不是 `Lock`？
- 为什么 `BaseApi` 只对 GET 做重试？
- `cleanup_after_test` 是 function 级还是 session 级？为什么这样设计？
- UI 用例中 `page` 和 `fresh_page` 的区别是什么？
- Jenkinsfile 中 `archiveArtifacts` 和 `allure` 产物有什么区别？

---

## 10. 总结：学习路径图

```text
环境跑通 → 项目骨架 → Common 公共层 → API 自动化 → UI 自动化
                                            ↓
Integration 联动/DB 校验 → Allure 报告 → Jenkins CI/CD → JMeter/简历
```

**最重要的三件事**：
1. **先跑通，再理解**：不要一开始就逐行精读，先让测试跑起来，建立信心。
2. **每次只改一点点**：改一个参数、加一个断言、跑一条用例，观察结果。
3. **多讲多写**：把学到的东西用自己的话讲出来，是检验是否真懂的最好方式。

---

> 本计划基于项目当前实际代码生成，所有文件路径均可在 `e:\ruoyi\test\ruoyi-auto-test` 下找到。学习过程中有任何具体代码看不懂，随时可以截取片段继续深入讲解。
