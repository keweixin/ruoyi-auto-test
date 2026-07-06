# RuoYi-Vue-Pro 测试项目 — 逐文件彻底讲解计划

> **目标**：把 `e:\ruoyi\test\ruoyi-auto-test` 项目中的**每一个文件**讲清楚：它是什么、为什么需要它、它在项目中的位置、关键代码怎么工作、你该怎么看/怎么用。
> **讲解风格**：先一句话人话 → 再讲基础知识 → 再指项目位置 → 最后给操作步骤。
> **适用对象**：基础较弱，希望真正看懂项目每一处代码的同学。

---

## 1. 项目与任务概述

### 1.1 项目是什么

本项目是 **RuoYi-Vue-Pro（若依）后台管理系统的接口 + UI 综合自动化测试工程**，使用 Python + pytest + requests + Playwright 实现，共约 **205 条测试实例**。

### 1.2 本次任务

不是改代码，而是**逐文件讲解代码**。讲解范围覆盖：

- 根目录全局配置（6 个文件）
- `common/` 公共层（15 个 `.py` + 1 `__init__.py`）
- `api_auto/` 接口自动化层（1 个 token_manager + 1 个 base_api + 1 个 crud_client + 10 个 client + 10 个 testcase + 2 个 conftest）
- `ui_auto/` UI 自动化层（1 个 auth_state_manager + 1 个 base_page + 8 个 page + 8 个 testcase + 2 个 conftest）
- `integration/` 接口联动层（5 个 test_*.py）
- `tests/` 框架单测层（2 个 test_*.py）
- `data/` 数据层（8 个 YAML）
- `scripts/` 脚本层（5 个 bat）
- `jmeter/` 性能层（2 个 jmx）
- `docs/` 文档层（18 个 md）

合计约 **79 个 `.py` 文件 + 41 个其他文件**。

### 1.3 讲解原则

- 每个文件遵循固定结构：**是什么 → 为什么需要 → 在哪里 → 关键代码 → 你怎么看/怎么用**。
- 代码讲解不会只念代码，会解释**每一行背后的设计意图**。
- 按依赖关系由浅入深讲解，先讲被依赖的，再讲依赖别人的。
- 每一批讲完后留作业和 checkpoint，确认理解再继续。

---

## 2. 当前项目结构梳理

基于实际代码梳理，项目分层如下：

```text
ruoyi-auto-test/
├── pytest.ini                  pytest 配置
├── requirements.txt            Python 依赖
├── Jenkinsfile                 CI/CD 流水线
├── conftest.py                 全局 fixture
├── README.md                   项目总览
├── .gitignore                  Git 忽略规则
│
├── common/                     公共能力层
│   ├── config.py               配置读取
│   ├── logger.py               日志
│   ├── yaml_utils.py           YAML 读取工具
│   ├── data_provider.py        YAML 数据驱动
│   ├── db_utils.py             数据库工具
│   ├── environment_utils.py    稳定基础数据查询
│   ├── assert_utils.py         通用断言
│   ├── schema_utils.py         JSON Schema 校验
│   ├── faker_utils.py          Faker 假数据
│   ├── random_utils.py         随机数据与前缀
│   ├── test_data.py            合法请求体与造数 helper
│   ├── cleanup_utils.py        数据清理
│   ├── security_utils.py       敏感信息脱敏
│   ├── token_registry.py       Token 登记与回收
│   └── allure_utils.py         Allure 附件
│
├── api_auto/                   接口自动化
│   ├── auth/token_manager.py   Token 生命周期
│   ├── base/base_api.py        HTTP 请求封装
│   ├── base/crud_client.py     声明式 CRUD 基类
│   ├── clients/                10 个业务 client
│   ├── testcases/              10 个接口测试文件
│   └── conftest.py             占位文件
│
├── ui_auto/                    UI 自动化
│   ├── auth/auth_state_manager.py  登录态快照管理
│   ├── base/base_page.py       页面公共操作
│   ├── pages/                  8 个页面对象
│   ├── testcases/              8 个 UI 测试文件
│   └── conftest.py             占位文件
│
├── integration/                接口联动 + DB 校验
│   └── test_*.py               5 个联动测试文件
│
├── tests/                      框架单测
│   ├── test_base_api_http_client.py
│   └── test_common_tools.py
│
├── data/                       测试数据与配置
│   ├── env.example.yaml
│   ├── login_data.yaml
│   ├── user_data.yaml
│   ├── dept_data.yaml
│   ├── role_data.yaml
│   ├── post_data.yaml
│   ├── dict_data.yaml
│   └── menu_data.yaml
│
├── scripts/                    一键脚本
│   ├── run_all.bat
│   ├── run_api.bat
│   ├── run_ui.bat
│   ├── run_collect.bat
│   └── open_allure.bat
│
├── jmeter/                     性能测试计划
│   ├── ruoyi_login_dict_perf.jmx
│   └── 登录+字典类型分页性能测试.jmx
│
└── docs/                       文档
    ├── 01_项目理解.md
    ├── 项目运行说明.md
    ├── 接口分析.md
    ├── 测试计划.md
    ├── 测试用例设计方法.md
    ├── 用例清单.md
    ├── 缺陷报告.md
    ├── 缺陷报告/*.md
    ├── Jenkins接入说明.md
    ├── JMeter性能测试操作文档.md
    ├── 测试总结.md
    ├── 面试讲解稿.md
    ├── 基础能力学习清单.md
    └── evidence/*.md
```

---

## 3. 分批次讲解路线

为了保证不遗漏、不跳跃，按以下 12 个批次进行。每一批都是“先讲底层公共工具，再讲上层用例”。

### 批次 1：入口与全局配置（6 个文件）

| 文件 | 讲解重点 |
|---|---|
| `README.md` | 项目定位、技术栈、架构图、运行命令 |
| `pytest.ini` | addopts、testpaths、markers |
| `requirements.txt` | 每个依赖包的作用 |
| `Jenkinsfile` | 流水线 stage、credentials、post 归档 |
| `conftest.py` | 所有 fixture 和 hook 的详细讲解 |
| `.gitignore` | 为什么忽略 venv、env.yaml、reports 等 |

**预期课时**：1 个session。
**checkpoint**：能口述每个入口文件的作用，能运行 `pytest --collect-only -q`。

---

### 批次 2：配置与公共工具基础（6 个文件）

| 文件 | 讲解重点 |
|---|---|
| `common/config.py` | 环境变量 vs YAML vs 默认值 |
| `common/logger.py` | logging 配置、分级、输出到文件 |
| `common/yaml_utils.py` | YAML 读取、case_id 去重检查 |
| `common/allure_utils.py` | attach_text / attach_json / attach_png |
| `common/security_utils.py` | 脱敏规则、为什么日志不能带密码 |
| `common/faker_utils.py` | Faker 生成中文姓名/手机号/邮箱 |

**预期课时**：1 个session。
**checkpoint**：能用 `cfg` 读取配置，能用 `log.info()` 写日志，能用 `allure_utils` 附加文本。

---

### 批次 3：数据库与断言（3 个文件）

| 文件 | 讲解重点 |
|---|---|
| `common/db_utils.py` | pymysql 连接、DictCursor、query_one/query_all/execute、防 SQL 注入 |
| `common/assert_utils.py` | assert_api_ok / assert_api_fail / assert_response_ok / assert_page_result |
| `common/environment_utils.py` | 查询稳定的部门/菜单 ID，避免硬编码 |

**预期课时**：1 个session。
**checkpoint**：能用 `db_utils.query_one` 查询 system_users，能写 `assert_api_ok`。

---

### 批次 4：数据构造与清理（3 个文件）

| 文件 | 讲解重点 |
|---|---|
| `common/random_utils.py` | TEST_RUN_PREFIX 生成规则、gen_name / gen_username / gen_mobile |
| `common/test_data.py` | valid_user_data / create_user / with_created_entity |
| `common/cleanup_utils.py` | 为什么先清关系表、逻辑删除、限定前缀 |

**预期课时**：1 个session。
**checkpoint**：能生成随机用户名，能用 `create_user` 创建测试数据，能理解 cleanup 的 SQL 顺序。

---

### 批次 5：认证与 Token 管理（2 个文件）

| 文件 | 讲解重点 |
|---|---|
| `common/token_registry.py` | 登记 token、从 storage_state 提取 token、session 结束统一 logout |
| `api_auto/auth/token_manager.py` | access token / refresh token、过期判断、自动刷新、401 恢复、RLock |

**预期课时**：1~1.5 个session（这是核心难点）。
**checkpoint**：能画出 TokenManager 的 get_access_token 流程图，能解释 RLock 作用。

---

### 批次 6：接口基础封装（2 个文件）

| 文件 | 讲解重点 |
|---|---|
| `api_auto/base/base_api.py` | Session 复用、Retry、超时、统一前缀、header 注入、401 重试、日志/Allure、上传下载 |
| `api_auto/base/crud_client.py` | resource 声明、create/update/delete/get/page/list_all_simple |

**预期课时**：1.5 个session。
**checkpoint**：能手写 `BaseApi` 的简化版，能解释为什么 GET 重试而 POST 不重试。

---

### 批次 7：业务 Client 逐个讲解（10 个文件）

| 文件 | 讲解重点 |
|---|---|
| `api_auto/clients/auth_client.py` | login / logout / refresh-token / get-permission-info |
| `api_auto/clients/user_client.py` | 用户 CRUD + 状态/重置密码 |
| `api_auto/clients/dept_client.py` | 部门 CRUD + list |
| `api_auto/clients/role_client.py` | 角色 CRUD |
| `api_auto/clients/post_client.py` | 岗位 CRUD |
| `api_auto/clients/dict_client.py` | 字典类型/数据接口 |
| `api_auto/clients/menu_client.py` | 菜单 CRUD + treeselect |
| `api_auto/clients/permission_client.py` | assign_role_menu / assign_user_role |
| `api_auto/clients/log_client.py` | 操作日志/登录日志查询 |
| `api_auto/clients/profile_client.py` + `notice_client.py` | 个人中心/通知公告 |

**预期课时**：2 个session。
**checkpoint**：能说出任意 client 的继承关系和核心方法。

---

### 批次 8：接口测试用例（10 个文件）

| 文件 | 讲解重点 |
|---|---|
| `api_auto/testcases/test_auth_api.py` | 登录参数化、鉴权、退出、token 刷新、401 恢复 |
| `api_auto/testcases/test_user_api.py` | YAML 数据驱动、CRUD、DB 校验 |
| `api_auto/testcases/test_dept_api.py` | 部门 CRUD、树形结构、DB 校验 |
| `api_auto/testcases/test_role_api.py` | 角色 CRUD、分配菜单、数据范围 |
| `api_auto/testcases/test_post_api.py` | 岗位 CRUD、编码重复 |
| `api_auto/testcases/test_dict_api.py` | 字典类型/数据、参数校验 |
| `api_auto/testcases/test_menu_api.py` | 菜单查询、新增、按钮 |
| `api_auto/testcases/test_log_api.py` | 日志分页筛选 |
| `api_auto/testcases/test_profile_api.py` | 个人中心 |
| `api_auto/testcases/test_notice_api.py` | 通知公告 |

**预期课时**：2~3 个session。
**checkpoint**：能手写一条新的接口用例，能解释参数化和 YAML 驱动。

---

### 批次 9：UI 基础与登录态（3 个文件）

| 文件 | 讲解重点 |
|---|---|
| `ui_auto/base/base_page.py` | open / click / fill / wait / toast / table / dialog / form_item / messagebox |
| `ui_auto/pages/login_page.py` | 登录页元素定位、login_as_admin、wait_logged_in |
| `ui_auto/auth/auth_state_manager.py` | storage_state、create_state、new_authenticated_page、失效重登 |

**预期课时**：1.5 个session。
**checkpoint**：能解释 browser/context/page/locator 的关系，能解释 storage_state 复用。

---

### 批次 10：UI 页面对象（8 个文件）

| 文件 | 讲解重点 |
|---|---|
| `ui_auto/pages/home_page.py` | 首页、菜单、退出 |
| `ui_auto/pages/dept_page.py` | 部门管理页 |
| `ui_auto/pages/dict_page.py` | 字典管理页 |
| `ui_auto/pages/user_page.py` | 用户管理页 |
| `ui_auto/pages/role_page.py` | 角色管理页 |
| `ui_auto/pages/post_page.py` | 岗位管理页 |
| `ui_auto/pages/menu_page.py` | 菜单管理页 |
| `ui_auto/testcases/test_real_ui_ops.py` | 真实 UI 操作组合 |

**预期课时**：2 个session。
**checkpoint**：能手写一条简单 UI 用例，使用 Page Object 模式。

---

### 批次 11：UI 测试用例（8 个文件）

| 文件 | 讲解重点 |
|---|---|
| `ui_auto/testcases/test_login_ui.py` | 登录/退出/未登录跳转 |
| `ui_auto/testcases/test_dept_ui.py` | 部门页面验证 |
| `ui_auto/testcases/test_dict_ui.py` | 字典页面验证 |
| `ui_auto/testcases/test_user_ui.py` | 用户页面验证 |
| `ui_auto/testcases/test_role_ui.py` | 角色页面验证 |
| `ui_auto/testcases/test_post_ui.py` | 岗位页面验证 |
| `ui_auto/testcases/test_menu_ui.py` | 菜单页面验证 |
| `ui_auto/conftest.py` / `api_auto/conftest.py` | 为什么为空 |

**预期课时**：1.5 个session。
**checkpoint**：能用 `--headed` 和 `--slowmo` 跑 UI 用例并观察行为。

---

### 批次 12：Integration、单测、脚本、JMeter、文档（16 个文件）

| 文件 | 讲解重点 |
|---|---|
| `integration/test_role_permission_flow.py` | 角色+菜单+用户+DB 校验 |
| `integration/test_api_flow.py` | 纯接口联动 |
| `integration/test_dict_api_ui_flow.py` | 字典联动 |
| `integration/test_user_api_ui_flow.py` | 用户联动 |
| `integration/test_dept_ui_api_db_flow.py` | 部门岗位联动 |
| `tests/test_base_api_http_client.py` | BaseApi 单测 |
| `tests/test_common_tools.py` | common 工具单测 |
| `scripts/run_*.bat` | 一键运行脚本 |
| `jmeter/*.jmx` | JMeter 性能测试计划 |
| `docs/*.md` | 文档的阅读顺序和重点 |

**预期课时**：2 个session。
**checkpoint**：能解释 Integration 的“造数 → 校验 → 清理”闭环，能口述 Jenkinsfile 流程。

---

## 4. 讲解形式与互动方式

### 4.1 每批次的固定结构

对每一个文件，按下面 5 步讲：

1. **一句话讲人话**：这个文件是干嘛的。
2. **为什么需要它**：没有它会怎样。
3. **项目位置**：文件路径、被谁调用、调用谁。
4. **关键代码逐行/逐函数讲解**：重点讲设计意图，不是念代码。
5. **你该怎么做**：怎么看、怎么改、怎么验证、常见坑。

### 4.2 你的学习任务

每批讲完后，你需要完成：

1. **打开文件自己看一遍**。
2. **回答我提出的 2~3 个 checkpoint 问题**。
3. **完成一个小作业**（如运行某条用例、修改一个参数、手写一个小脚本）。
4. **把不理解的地方标出来问我**。

### 4.3 节奏控制

- 每次讲解 1~2 个批次，避免信息过载。
- 遇到核心难点（如 TokenManager、BaseApi、conftest）会放慢，多举例子。
- 你可以随时喊停，要求某一行代码再讲一遍。

---

## 5. 假设与决策

### 5.1 假设

- 你已具备基础 Python 语法知识（if/for/class/function）。
- 你了解 HTTP 请求的基本概念（GET/POST、Header/Body、200/401）。
- 你正在使用 Windows 环境，项目路径为 `e:\ruoyi\test\ruoyi-auto-test`。
- 被测系统（RuoYi-Vue-Pro）可以在本地启动。

### 5.2 决策

- **不改动代码**：本次任务是“讲解”，除非作业需要，否则不修改项目文件。
- **按依赖顺序讲**：先公共层，再接口/UI 基础层，最后用例层。
- **不讲 Java/Vue 源码**：只讲测试项目代码，被测系统的前后端源码不在本次范围内。
- **代码会贴片段**：但只贴关键部分，完整代码需要你打开文件对照看。

---

## 6. 验证方式

### 6.1 过程验证

每个批次结束后，通过以下方式确认理解：

- 你用自己的话复述文件作用。
- 你能指出关键函数在文件中的位置。
- 你能运行相关命令并解释输出。

### 6.2 最终验证

全部批次讲完后，你需要独立完成：

1. 画出项目四层架构图，并标注至少 10 个关键文件。
2. 逐行讲解 `conftest.py` 中的 `token_manager`、`page`、`cleanup_after_test`。
3. 逐行讲解 `api_auto/base/base_api.py` 中的 `request()` 方法。
4. 新增一条简单接口用例或 UI 用例，并成功运行。
5. 口述 Jenkinsfile 每个 stage 的作用。

---

## 7. 预计总课时

| 内容 | 预计 session 数 |
|---|---|
| 入口与全局配置 | 1 |
| 配置与公共工具基础 | 1 |
| 数据库与断言 | 1 |
| 数据构造与清理 | 1 |
| 认证与 Token 管理 | 1~1.5 |
| 接口基础封装 | 1.5 |
| 业务 Client | 2 |
| 接口测试用例 | 2~3 |
| UI 基础与登录态 | 1.5 |
| UI 页面对象 | 2 |
| UI 测试用例 | 1.5 |
| Integration、单测、脚本、JMeter、文档 | 2 |
| **总计** | **18~21 个 session** |

---

## 8. 下一步

确认本计划后，我将从**批次 1：入口与全局配置**开始讲解，逐个文件彻底讲透。
