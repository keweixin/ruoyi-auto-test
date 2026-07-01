# JMeter 性能测试操作文档

> 项目：RuoYi v3.9.2 后台管理系统接口与 UI 自动化测试项目  
> 性能测试工具：Apache JMeter  
> 目标：补充一个可讲解、可导入执行的 JMeter 性能测试方案。  
> 说明：当前已提供 `.jmx` 测试计划，但未产出真实 `.jtl` 或 HTML 性能报告；简历只能写“编写/设计 JMeter 性能测试方案”。

---

## 1. 为什么选择 JMeter

本项目主体是接口自动化和 UI 自动化，性能测试作为补充场景，不追求复杂压测平台，而是使用 JMeter 完成一个典型后台接口性能测试。

选择 JMeter 的原因：

```text
1. 测试行业常用，面试认可度高；
2. 适合接口压测、并发测试、稳定性测试；
3. 支持图形界面配置，初学者容易上手；
4. 支持命令行运行并生成 HTML 报告；
5. 可通过 JSON 提取器提取 token，适合若依这类登录鉴权系统。
```

---

## 2. 性能测试目标

本次性能测试选择若依后台系统的典型接口链路：

```text
登录接口
   ↓
提取 token
   ↓
携带 token 查询字典类型分页接口
```

测试目标：

```text
1. 验证登录接口在一定并发下是否稳定；
2. 验证携带 token 的业务查询接口是否稳定；
3. 观察平均响应时间、P95 响应时间、错误率、吞吐量；
4. 形成一份可放入项目文档和面试讲解的性能测试结果。
```

---

## 3. 被测接口信息

### 3.1 登录接口

```text
请求方法：POST
请求地址：http://localhost:8080/login
请求头：
  Content-Type: application/json
  请求体：
{
  "username": "admin",
  "password": "admin123"
}
返回字段：
  token
```

> 注意：原版若依默认开启验证码。为了接口自动化和 JMeter 压测方便，已在数据库 sys_config 中关闭 sys.account.captchaEnabled：

```yaml
sys.account.captchaEnabled=false
```

### 3.2 字典类型分页接口

```text
请求方法：GET
请求地址：http://localhost:8080/system/dict/type/list?pageNum=1&pageSize=10
请求头：
    Authorization: Bearer ${token}
```

---

## 4. 测试环境准备

### 4.1 启动被测系统

确保以下服务已启动：

```text
1. MySQL
2. Redis
3. RuoYi v3.9.2 后端服务，端口 8080
4. 前端可选，本次 JMeter 只测接口，不依赖前端
```

验证后端可访问：

```text
http://localhost:8080/
```

### 4.2 安装 JMeter

1. 下载 Apache JMeter：

```text
https://jmeter.apache.org/download_jmeter.cgi
```

2. 解压到本地目录，例如：

```text
D:\apache-jmeter
```

3. 配置 Java 环境，确认命令可用：

```bash
java -version
```

4. 启动 JMeter 图形界面：

```bash
D:\apache-jmeter\bin\jmeter.bat
```

---

## 5. JMeter 测试计划设计

### 5.1 新建测试计划

打开 JMeter 后，默认会有一个 `Test Plan`。

建议命名为：

```text
RuoYi 后台接口性能测试计划
```

---

## 6. 添加线程组

右键测试计划：

```text
添加 → 线程（用户）→ 线程组
```

线程组配置建议：

```text
线程数：20
Ramp-Up 时间：10 秒
循环次数：10
```

含义：

```text
线程数 20：模拟 20 个并发用户；
Ramp-Up 10 秒：10 秒内逐步启动 20 个用户，避免瞬间打满；
循环次数 10：每个用户执行 10 次请求链路。
```

第一阶段建议不要一开始设置太大并发，先从 10、20、50 逐步增加。

---

## 7. 添加 HTTP 请求默认值

右键线程组：

```text
添加 → 配置元件 → HTTP 请求默认值
```

配置：

```text
协议：http
服务器名称或 IP：localhost
端口号：48080
```

这样后续 HTTP 请求只需要写路径，不用重复写完整域名。

---

## 8. 添加 HTTP Header Manager

右键线程组：

```text
添加 → 配置元件 → HTTP 信息头管理器
```

添加默认请求头：

| 名称 | 值 |
|------|----|
| Content-Type | application/json |

> 业务接口需要 `Authorization`，后面在业务请求里单独加。

---

## 9. 添加登录接口请求

右键线程组：

```text
添加 → 取样器 → HTTP 请求
```

命名为：

```text
01_登录获取token
```

配置：

```text
方法：POST
路径：/login
```

在 `Body Data` 中填写：

```json
{
  "username": "admin",
  "password": "admin123"
}
```

---

## 10. 添加 JSON 提取器提取 token

右键登录请求 `01_登录获取token`：

```text
添加 → 后置处理器 → JSON 提取器
```

配置：

```text
名称：提取 token
变量名：token
JSONPath 表达式：$.token
匹配编号：1
默认值：TOKEN_NOT_FOUND
```

作用：

```text
从登录响应中提取 token，保存到变量 ${token}。
后续请求可以用 ${token} 作为 token。
```

---

## 11. 添加登录响应断言

右键登录请求：

```text
添加 → 断言 → 响应断言
```

配置：

```text
要测试的响应字段：响应文本
模式匹配规则：包含
测试模式："code":0
```

也可以断言响应中包含：

```text
token
```

意义：

```text
不能只看 HTTP 200，还要确认若依业务 code 为 0，并成功返回 token。
```

---

## 12. 添加业务接口请求：查询字典分页

右键线程组：

```text
添加 → 取样器 → HTTP 请求
```

命名为：

```text
02_查询字典类型分页
```

配置：

```text
方法：GET
路径：/system/dict/type/list
```

参数：

| 名称 | 值 |
|------|----|
| pageNum | 1 |
| pageSize | 10 |

---

## 13. 给业务接口添加 Authorization 请求头

右键 `02_查询字典类型分页`：

```text
添加 → 配置元件 → HTTP 信息头管理器
```

添加：

| 名称 | 值 |
|------|----|
| Authorization | Bearer ${token} |

说明：

```text
${token} 是第 10 步 JSON 提取器提取出来的变量。
业务接口必须携带 Authorization，否则会返回 401。
```

---

## 14. 添加业务接口响应断言

右键 `02_查询字典类型分页`：

```text
添加 → 断言 → 响应断言
```

配置：

```text
响应文本包含："code":0
响应文本包含："list"
响应文本包含："total"
```

意义：

```text
验证接口不只是 HTTP 成功，还要业务成功，并返回分页结构。
```

---

## 15. 添加查看结果树（调试用）

右键线程组：

```text
添加 → 监听器 → 查看结果树
```

用途：

```text
调试阶段查看请求、响应、断言失败原因。
```

注意：

```text
正式压测时不要开启“查看结果树”，它会消耗大量内存，影响性能结果。
```

---

## 16. 添加聚合报告

右键线程组：

```text
添加 → 监听器 → 聚合报告
```

重点关注指标：

| 指标 | 含义 |
|------|------|
| Samples | 请求总数 |
| Average | 平均响应时间 |
| Median | 中位数响应时间 |
| 90% Line | 90% 请求响应时间低于该值 |
| 95% Line | 95% 请求响应时间低于该值 |
| Error % | 错误率 |
| Throughput | 吞吐量，每秒请求数 |

---

## 17. 建议压测梯度

不要一开始直接压很大并发。建议分三轮：

### 第一轮：冒烟压测

```text
线程数：5
Ramp-Up：5 秒
循环次数：5
目标：确认脚本可跑、token 可提取、断言正常。
```

### 第二轮：基础并发

```text
线程数：20
Ramp-Up：10 秒
循环次数：10
目标：观察接口在小并发下的稳定性。
```

### 第三轮：压力观察

```text
线程数：50
Ramp-Up：20 秒
循环次数：10
目标：观察响应时间、错误率、吞吐量变化。
```

如果出现大量错误，不要继续加压，先分析瓶颈。

---

## 18. 建议性能指标

本项目作为学习和简历项目，不建议写过于夸张的指标。可以设置如下目标：

```text
1. 登录接口平均响应时间 < 1000ms；
2. 字典分页接口平均响应时间 < 500ms；
3. P95 响应时间 < 1500ms；
4. 错误率 = 0%；
5. 20 并发下系统无明显异常。
```

> 注意：这些只是学习项目的建议指标，实际结果要以你的本地机器配置、数据库配置、Redis 配置为准。

---

## 19. 命令行执行 JMeter

图形界面适合调试，正式压测建议用命令行。

假设测试计划保存为：

```text
E:\ruoyi\test\jmeter\ruoyi_dict_perf.jmx
```

执行命令：

```bash
jmeter -n -t E:\ruoyi\test\jmeter\ruoyi_dict_perf.jmx -l E:\ruoyi\test\jmeter\result.jtl -e -o E:\ruoyi\test\jmeter\html-report
```

参数说明：

```text
-n：非 GUI 模式运行
-t：指定 jmx 测试计划
-l：保存结果文件 jtl
-e：执行完成后生成 HTML 报告
-o：HTML 报告输出目录
```

注意：

```text
html-report 目录必须不存在或为空，否则 JMeter 会报错。
```

---

## 20. 性能测试报告保存建议

建议保存以下内容：

```text
jmeter/
├── ruoyi_dict_perf.jmx       # JMeter 测试计划
├── result.jtl                # 执行结果
├── html-report/              # JMeter HTML 报告
└── README.md                 # 执行说明
```

如果要放入 Git：

```text
建议提交：jmx 文件、README、测试结论文档
不建议提交：大体积 html-report、jtl 原始结果
```

---

## 21. 结果分析模板

执行完成后，在 `docs/测试总结.md` 中记录：

```text
性能测试场景：登录 + 查询字典类型分页
并发用户数：20
循环次数：10
总请求数：400
平均响应时间：xxx ms
P95 响应时间：xxx ms
错误率：0%
吞吐量：xxx req/s
结论：在 20 并发下，系统接口响应稳定，未出现错误；随着并发提升到 50，响应时间有所增加，但错误率仍为 0%。
```

---

## 22. 常见问题与排查

### 22.1 登录接口返回验证码错误

原因：若依验证码未关闭。

解决：在本地环境配置中加入：

```yaml
sys.account.captchaEnabled=false
```

重启后端。

### 22.2 业务接口返回 401

原因：token 未提取成功或 Authorization 请求头格式错误。

检查：

```text
1. JSON 提取器变量名是否是 token；
2. JSONPath 是否是 $.token；
3. Authorization 是否写成 Bearer ${token}；
4. 登录请求是否成功。
```

### 22.3 响应断言失败

原因：接口业务失败，返回 code 非 0。

检查：

```text
1. 查看结果树中的响应体；
3. 检查 token 是否有效；
4. 检查后端日志。
```

### 22.4 命令行生成 HTML 报告失败

原因：输出目录已存在且不为空。

解决：删除旧目录后重新执行：

```bash
rmdir /s /q E:\ruoyi\test\jmeter\html-report
```

---

## 23. 简历中怎么描述性能测试

建议写法：

```text
补充使用 JMeter 对登录和字典分页接口设计性能测试场景，通过 JSON 提取器获取 token 并传递给后续业务接口，观察并发下平均响应时间、P95 响应时间、错误率和吞吐量，形成性能测试报告。
```

不要写：

```text
系统支持高并发、性能优秀、压测全部通过
```

除非你有真实数据支撑。

---

## 24. 面试时怎么讲

可以这样说：

```text
我在自动化测试项目之外，补充了一个 JMeter 性能测试场景。场景是先调用登录接口获取 token，通过 JSON 提取器提取 token，再把 token 放到 Authorization 请求头里访问字典分页接口。测试时我关注平均响应时间、P95、错误率和吞吐量。这样既能体现我了解接口性能测试流程，也能说明我知道带鉴权接口如何做压测。
```

如果面试官追问“为什么不用 UI 做性能测试”，回答：

```text
性能测试主要关注服务端接口在并发下的响应能力，UI 自动化受浏览器渲染、网络、机器性能影响较大，不适合做大规模并发压测。因此我选择用 JMeter 直接压后端接口。
```
