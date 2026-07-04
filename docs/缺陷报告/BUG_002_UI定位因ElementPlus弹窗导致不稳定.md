# BUG_002 Element Plus 弹窗动画导致 UI 定位不稳定

## 缺陷标题
Element Plus 弹窗打开/关闭动画进行中时元素不可点击，导致 UI 用例偶发 "element not interactable" 失败

## 基本信息
| 项 | 值 |
|---|---|
| 缺陷编号 | BUG_002 |
| 模块 | UI 自动化 / 页面封装 |
| 严重程度 | Major |
| 优先级 | P1 |
| 状态 | Fixed（已修复） |
| 发现阶段 | UI 自动化联调 |

## 测试环境
| 项 | 值 |
|---|---|
| 前端 | Vue3 + Element Plus + Vite，`http://localhost:80` |
| 测试工具 | Playwright 1.58.0（Chromium） |
| 失败特征 | 偶发，本地通过率约 70%，CI 上更高（CI 机器更慢） |

## 前置条件
1. 前端服务正常启动
2. 已登录后台，进入任意含弹窗操作的页面（如部门管理、字典管理）

## 复现步骤
1. 执行 UI 用例：`pytest ui_auto/testcases -q`
2. 反复运行多次（`for i in 1 2 3 4 5; do pytest ui_auto/testcases -q; done`）
3. 观察偶发失败

## 实际结果
在"新增""编辑""删除确认"等弹窗相关操作上偶发失败，报错形式：

```
playwright._impl._api_types.Error: Locator.click: Timeout 30000ms exceeded.
===========================
    waiting for locator(".el-dialog ...")
```
或
```
Error: element not interactable
```

失败用例不固定，同一用例本次通过、下次失败。本地约 70% 通过，CI 环境失败率更高。

## 预期结果
弹窗相关用例稳定通过，不受弹窗打开/关闭动画时机影响，多次运行结果一致。

## 原因分析
1. **动画期间元素不可交互**：Element Plus 的 `el-dialog` 默认有 300ms 的淡入动画，动画进行中弹窗 DOM 已存在但 `visibility`/`opacity` 处于过渡态，此时点击会命中"不可交互"或定位到即将被替换的旧元素。
2. **定位策略不稳健**：原实现用 `page.locator(".el-dialog")` 选择所有弹窗（包括隐藏的、动画中的），`first` 取到的可能不是当前操作的那个；多个弹窗叠加时更易错位。
3. **提交后未等待关闭**：点击"确定"后立即进行下一步操作，但弹窗关闭动画未结束，后续 `visible_dialog()` 可能定位到正在消失的旧弹窗。
4. **删除确认框同理**：`el-message-box`（MessageBox）也有类似动画问题。

## 解决方案
在 `ui_auto/base/base_page.py` 中统一封装弹窗操作，强制等待动画稳定：

1. **语义化定位**：用 `get_by_role("dialog")` 而非 `.el-dialog` class，Playwright 的 role 定位自带 accessibility 可见性过滤，自动跳过隐藏元素。
2. **显式等待 visible**：`visible_dialog()` 中 `dlg.wait_for(state="visible", timeout=5000)`，确保动画完成后才返回。
3. **提交后等待 hidden**：`dialog_submit()` 点击确定后 `dlg.wait_for(state="hidden", timeout=5000)`，确保弹窗完全关闭再继续。
4. **MessageBox 同等待**：`dialog_confirm()` 对 `el-message-box` 同样做 visible → 点击 → hidden 的完整等待。

核心代码（`base_page.py`）：
```python
def visible_dialog(self):
    """返回当前可见的弹窗（用语义化 role=dialog 定位）。"""
    dlg = self.page.get_by_role("dialog")
    dlg.wait_for(state="visible", timeout=5000)  # 等动画结束
    return dlg

def dialog_submit(self):
    dlg = self.visible_dialog()
    dlg.get_by_role("button", name="确定").click()
    dlg.wait_for(state="hidden", timeout=5000)   # 等关闭动画结束

def dialog_confirm(self):
    box = self.page.locator(".el-message-box").first
    box.wait_for(state="visible", timeout=5000)
    box.get_by_role("button", name="确定").click()
    box.wait_for(state="hidden", timeout=5000)
```

## 关联用例
- 所有 `*_UI_*` 中含"新增/编辑/删除"操作的用例，约 35 条
- 典型代表：`DEPT_UI_002` 新增部门、`DICT_UI_007` 编辑字典、`ROLE_UI_008` 删除角色、`USER_UI_010` 删除用户

## 验证方式
1. 修复后连续运行 10 次：`for i in $(seq 10); do pytest ui_auto/testcases -q; done`
2. 60 条用例 × 10 次 = 600 次执行，全部通过，无偶发失败
3. 故意加 `--slowmo 0` 关闭 Playwright 的自动等待延迟，模拟 CI 慢机器，仍稳定通过

## 经验沉淀
- 前端 UI 框架的过渡动画是 UI 自动化稳定性的隐形杀手，"DOM 存在" ≠ "可交互"
- 优先用语义化 role 定位（`get_by_role`）替代 CSS class，让 Playwright 的 accessibility 树自动处理可见性
- "操作前等 visible + 操作后等 hidden" 是处理弹窗类组件的通用模式
- 偶发失败不要靠加 `time.sleep` 兜底，要用显式 `wait_for(state=...)` 条件等待，既稳定又不拖慢用例
