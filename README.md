# RuoYi-Vue-Pro 后台管理系统接口与 UI 自动化测试项目

> 基于 RuoYi-Vue-Pro 前后端分离后台管理系统，使用 Python + pytest + requests + Playwright 搭建综合自动化测试项目。  
> 设计/实现 149 个测试实例，覆盖登录认证、字典、部门、岗位、用户、角色、菜单权限等核心模块。  
> 注意：简历建议写“设计/实现 149 个测试实例”，不要写“149 条全部通过”；实际通过数量以本地 Allure 报告为准。

## 技术栈
Python · pytest · requests · Playwright · Page Object · YAML · pymysql · Allure · Jenkins · Git · JMeter

## 项目亮点
1. **接口和 UI 联动**：接口造数 → UI 验证展示 → 接口清理
2. **数据库校验**：验证数据真实落库与逻辑删除
3. **Page Object 分层**：用例只写业务流程，不暴露定位器
4. **权限场景设计**：接口建角色分配菜单 + UI 登录验证“授权菜单存在、未授权菜单不存在”
5. **失败定位**：UI 失败自动截图 + Playwright Trace 回放
6. **工程化**：环境变量配置、日志/Allure 脱敏、Jenkins 生成报告
7. **性能补充**：JMeter 登录取 token + 字典分页压测操作文档

## 项目目录
```
ruoyi-auto-test/
├── common/            公共工具（配置/日志/DB/断言/脱敏/清理）
├── api_auto/          接口自动化（base/clients/testcases）
├── ui_auto/           UI 自动化（base/pages/testcases）
├── integration/       接口+UI 联动用例
├── data/              env.example.yaml + 测试数据
├── docs/              测试计划/用例设计/缺陷报告/总结/面试稿/JMeter文档
├── reports/           Allure 报告
├── screenshots/       失败截图
├── traces/            Playwright Trace 文件
├── logs/              日志
├── pytest.ini  requirements.txt  Jenkinsfile  conftest.py
```

## 自动化范围
- **接口**：登录(9) + 字典(15) + 部门(10) + 岗位(9) + 用户(13) + 角色(12) + 菜单(6)
- **UI**：登录(8) + 字典(13) + 部门(7) + 岗位(7) + 用户(10) + 角色(8) + 菜单(6)
- **联动**：字典(4) + 用户(5) + 权限(4) + UI操作接口/DB校验(4)

## 配置方式（推荐环境变量）
```bash
set BASE_URL=http://localhost:48080
set WEB_URL=http://localhost:80
set TENANT_ID=1
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=你的密码
set DB_NAME=ruoyi-vue-pro
```

也可复制 `data/env.example.yaml` 为本地 `data/env.yaml`，但 `data/env.yaml` 已加入 `.gitignore`，不要提交真实密码。

## 运行方式
```bash
pip install -r requirements.txt
playwright install

# 启动若依后端/前端/MySQL/Redis，并关闭验证码：yudao.captcha.enable=false
pytest api_auto/testcases          # 只跑接口
pytest ui_auto/testcases           # 只跑 UI
pytest integration                 # 只跑联动
pytest                             # 全量
allure serve reports/allure-results
```

## 性能测试
JMeter 操作文档见：`docs/JMeter性能测试操作文档.md`

## 面试说明
- 面试稿：`docs/面试讲解稿.md`
- 测试计划：`docs/测试计划.md`
- 测试用例设计方法：`docs/测试用例设计方法.md`
- 缺陷报告：`docs/缺陷报告.md`
- 测试总结：`docs/测试总结.md`
- 基础能力学习清单：`docs/基础能力学习清单.md`
