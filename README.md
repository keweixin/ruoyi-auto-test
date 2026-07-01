# RuoYi v3.9.2 后台管理系统接口与 UI 自动化测试项目

> 基于 Docker 中的 **RuoYi v3.9.2 原版** 后台管理系统，使用 Python + pytest + requests + Playwright 搭建综合自动化测试项目。  
> 当前真实环境：后端 `http://localhost:8080`，前端 `http://localhost:8081`，数据库 `ry-vue`。  
> 设计/实现 **152 个测试实例**，最终真实执行结果：**152 passed, 0 failed, 0 skipped**。

## 技术栈
Python · pytest · requests · Playwright · Page Object · YAML · pymysql · Allure · Jenkins · Git · JMeter

## 项目亮点
1. **接口与 UI 分层覆盖**：接口验证业务逻辑和数据，UI 验证真实页面操作
2. **数据库校验**：验证数据真实落库、状态变化和逻辑删除
3. **Page Object 分层**：页面元素与业务动作封装，测试用例只写流程
4. **权限场景设计**：角色菜单关系通过接口和数据库双重验证
5. **失败定位**：失败截图 + Playwright Trace 回放
6. **工程化**：环境变量配置、日志/Allure 脱敏、Jenkins 报告生成
7. **性能补充**：已编写 JMeter 登录取 token + 字典分页压测方案和 .jmx 测试计划；未提交真实压测结果

## 项目目录
```
ruoyi-auto-test/
├── common/            公共工具（配置/日志/DB/断言/脱敏/清理）
├── api_auto/          接口自动化（base/clients/testcases）
├── ui_auto/           UI 自动化（base/pages/testcases）
├── integration/       接口联动与数据库校验用例
├── data/              env.example.yaml + 测试数据
├── docs/              测试计划/用例设计/缺陷报告/总结/面试稿/JMeter文档
├── jmeter/            JMeter .jmx 测试计划
├── reports/           Allure 报告
├── screenshots/       失败截图
├── traces/            Playwright Trace 文件
├── logs/              日志
├── pytest.ini  requirements.txt  Jenkinsfile  conftest.py
```

## 自动化范围
- **API 接口**：73 条
- **UI 自动化**：59 条
- **接口联动 / DB 校验**：20 条
- **合计**：152 条测试实例，真实执行 `152 passed`

## 配置方式（推荐环境变量）
```bash
set BASE_URL=http://localhost:8080
set WEB_URL=http://localhost:8081
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123
set DB_HOST=127.0.0.1
set DB_PORT=13306
set DB_USER=root
set DB_PASSWORD=password
set DB_NAME=ry-vue
```

也可复制 `data/env.example.yaml` 为本地 `data/env.yaml`；`data/env.yaml` 已加入 `.gitignore`，不要提交真实密码。

## 运行方式
```bash
pip install -r requirements.txt
playwright install

# 启动 Docker 后端/前端/MySQL/Redis，并关闭验证码 sys.account.captchaEnabled=false
pytest api_auto/testcases          # 只跑接口
pytest ui_auto/testcases           # 只跑 UI
pytest integration                 # 只跑联动
pytest                             # 全量
allure serve reports/allure-results
```

## JMeter 性能测试
文档：`docs/JMeter性能测试操作文档.md`  
测试计划：`jmeter/ruoyi_login_dict_perf.jmx`

说明：当前已提供可导入 JMeter 的测试计划和操作步骤，但**未产出真实性能报告**，简历应写“编写/设计 JMeter 性能测试方案”，不要写“完成性能测试并达标”。

## 面试说明
- 面试稿：`docs/面试讲解稿.md`
- 测试计划：`docs/测试计划.md`
- 测试用例设计方法：`docs/测试用例设计方法.md`
- 缺陷报告：`docs/缺陷报告.md`
- 测试总结：`docs/测试总结.md`
- 基础能力学习清单：`docs/基础能力学习清单.md`
