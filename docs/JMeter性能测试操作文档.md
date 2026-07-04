# JMeter 性能测试操作文档

> 项目：RuoYi-Vue-Pro / yudao 后台管理系统接口与 UI 自动化测试项目
>
> 性能测试工具：Apache JMeter
>
> 目标：补充一个可讲解、可导入执行的 JMeter 性能测试方案。
>
> 说明：当前已提供 `.jmx` 测试计划，但未产出真实 `.jtl` 或 HTML 性能报告；简历只能写“编写/设计 JMeter 性能测试方案”。

---

## 1. 被测链路

```text
登录接口
  ↓ 提取 data.accessToken
携带 tenant-id + Authorization
  ↓
查询字典类型分页接口
```

## 2. 当前环境

| 项 | 值 |
|---|---|
| 后端根地址 | `http://localhost:48080` |
| 管理端前缀 | `/admin-api` |
| 登录接口 | `POST /admin-api/system/auth/login` |
| 字典类型分页 | `GET /admin-api/system/dict-type/page?pageNo=1&pageSize=10` |
| 成功业务码 | `code == 0` |
| token 字段 | `data.accessToken` |
| 租户 Header | `tenant-id: 1` |

## 3. 登录接口配置

```text
请求方法：POST
请求地址：http://localhost:48080/admin-api/system/auth/login
请求头：
  Content-Type: application/json
  tenant-id: 1
请求体：
{
  "tenantName": "芋道源码",
  "username": "admin",
  "password": "admin123"
}
响应重点：
  code = 0
  data.accessToken
```

JSON Extractor：

```text
变量名：accessToken
JSONPath：$.data.accessToken
默认值：TOKEN_NOT_FOUND
```

## 4. 字典类型分页接口配置

```text
请求方法：GET
请求地址：http://localhost:48080/admin-api/system/dict-type/page?pageNo=1&pageSize=10
请求头：
  tenant-id: 1
  Authorization: Bearer ${accessToken}
```

断言：

```text
响应包含："code":0
响应包含："list"
响应包含："total"
```

## 5. 线程组建议

第一轮调试：

```text
线程数：1
Ramp-Up：1 秒
循环次数：1
```

确认脚本正确后再做小并发：

```text
线程数：10 / 20 / 50
Ramp-Up：10 秒
循环次数：10
```

## 6. 非 GUI 执行命令

```bash
jmeter -n -t jmeter/ruoyi_login_dict_perf.jmx \
  -l reports/jmeter/result.jtl \
  -e -o reports/jmeter/html
```

Windows 示例：

```bat
jmeter -n -t jmeter\ruoyi_login_dict_perf.jmx -l reports\jmeter\result.jtl -e -o reports\jmeter\html
```

## 7. 性能报告看什么

| 指标 | 含义 | 面试表达 |
|---|---|---|
| Samples | 请求样本数 | 样本太少结论不稳定 |
| Average | 平均响应时间 | 只看平均值不够 |
| 90/95/99% | 分位响应时间 | 95% 更接近大多数用户体验 |
| Throughput | 吞吐量/TPS | 并发增加但 TPS 不增长，可能到瓶颈 |
| Error % | 错误率 | 响应时间和错误率要一起看 |

## 8. 常见问题排查

| 问题 | 排查方向 |
|---|---|
| token 提取失败 | 确认 JSONPath 为 `$.data.accessToken`，登录响应 `code=0` |
| 业务接口 401 | 确认 Header 为 `Authorization: Bearer ${accessToken}` |
| 租户错误 | 确认 Header 带 `tenant-id: 1`，登录体含 `tenantName` |
| 404 | 确认路径带 `/admin-api` |
| 断言失败 | RuoYi-Vue-Pro 成功码是 `code=0`，不是 `code=200` |

## 9. 简历边界

可以写：

```text
设计 JMeter 登录取 token + 字典分页查询链路性能脚本，掌握 JSON Extractor、Header Manager、断言、非 GUI 执行和 HTML 报告生成流程。
```

不要写：

```text
完成性能压测并发现系统瓶颈。
```

除非已经真实执行并产出 `.jtl`、HTML 报告和性能分析结论。
