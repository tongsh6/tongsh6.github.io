---
layout: post
title: "我给 DSH 写了个插件，专治 AI「空等」：Mac/Win 双环境实测安装前后的效率变化"
date: 2026-11-06 10:00:00 +0800
categories: [技术, 项目]
tags: ["DSH", "DeepSeek Harness", "插件", "wait_until", "事件驱动", "等待", "卡住检测", "AI Agent"]
---

> 让 Agent 跑后台任务、等队友、等文件、等日志，是 DeepSeek Harness（dsh）里最常见的场景，也是最容易「白等」的场景。我写了个叫 `wait_until` 的小插件，在 macOS 和 Windows 两个环境都装上用了。这篇文章用实测数据讲清楚：安装前 Agent 是怎么空等的，安装后到底变快了多少。

## 先说结论

`dsh-tool-wait-until` 给模型一个**事件驱动**的等待原语 `wait_until`：目标完成、失败、或者连续没进展（卡住）时，**立刻返回一个结构化结果**，一次调用就能下结论。需要说明的是：**事件唤醒只适用于作业条件**（订阅 `jobs.events`，作业 settle / 输出增长时唤醒），**文件、日志、队友条件按 `poll_interval_sec` 采样**（默认 2 秒），不是所有条件都由事件即刻唤醒。同时它**主动堵死**模型最爱走的空等路径——前台 `sleep` 轮询、超长的 `job_output` / `wait_agent` 等待。

三个最值得关注的改进（口径见下文「关键数字」）：

1. **卡住从「无法识别」变成「有明确的 `stalled` 判定」**；
2. **失败判定从「超时后二次查询」变成「`fail_fast` 命中即返回 `failed` + 原因」**；
3. **决策从「两轮调用」变成「一轮调用」**。

## 一、安装前，Agent 是怎么空等的

我先把原生工具的真实行为测了个底朝天（存档在仓库 `docs/baseline.md`，macOS + Node 24，逐秒时间线）：

| 现象 | 原生工具的实际行为 |
| --- | --- |
| 等 teammate | `wait_agent` 最小等待粒度 **10 秒**，无变化窗口等满超时后只返回 `{"timedOut":true}`，一个布尔值，谁在跑、谁卡住、最后产出是啥，一概不知道 |
| 等后台脚本 | `job_output(wait:true)` 运行中调用会阻塞到超时或结束，中间输出只在「超时」或「结束」两个时机才交付 |
| 手工轮询 | `sleep 90` → 查文件 → 再估时间 → 再 sleep，一轮往返一分半 |
| 超时 ≠ 失败 | 超时返回后还得再查一轮，才知道是超时、失败还是成功 |

实测里最扎心的一条：`wait_agent(timeout_ms=10000)` 在无变化窗口里，墙钟 `14.66s`（含模型生成下一步工具调用的延迟），返回就一句 `{"timedOut":true}`——**它甚至分不清「队友卡死」和「队友正常但暂时没进展」**。

## 二、关键洞察：光给工具没用

这一点决定了整个设计。

一开始我也觉得「写个带超时的等待工具」就完了。但很快发现一个更隐蔽的问题：**模型在思考阶段就会自己决定「等 180 秒再查」**。这个念头不变，工具写得再好它也不会去用。

所以这个插件不是只做了一个工具，而是三层：

1. **决策前给规则**：往系统提示词注入「等待纪律」——等待一律用 `wait_until`，不许 `sleep` 空等。
2. **决策落地时硬拦截**：注册 `tools.guard`，把 `sleep ≥ 20s` 的前台 bash、超过 120s 的 `job_output` / `wait_agent` 等待直接拒绝，拒绝原因里附可复制的替代调用。
3. **替代原语本身**：`wait_until` 工具，条件满足、目标失败或连续无进展时，立即返回结构化结果。

一句话：**改行为比造工具更重要。**

## 三、`wait_until` 怎么用

```js
wait_until({
  conditions: [
    { kind: 'job',   id: '<job_id>' },                 // 等后台作业结束
    { kind: 'agent', target: 'worker' },               // 等队友空闲
    { kind: 'file',  path: '/tmp/out.zip', until: 'exists' },
    { kind: 'log',   path: '/tmp/build.log', matches: '/EXIT=0/' },
  ],
  fail_fast: true,          // 或 ['job_failed', 'stderr_matches:/error|failed|Traceback/']
  stall_after_sec: 120,     // 连续 120s 无任何进展 → 立刻返回 stalled
  timeout_sec: 900,         // 总兜底，不是主要判定手段
  poll_interval_sec: 2,
})
```

返回是一次调用就能下结论的：

```json
{
  "status": "failed",
  "elapsed": "1.2s",
  "failure_reason": "后台作业失败：退出码 3",
  "output_tail": "BOOM: intentional failure\n",
  "hint": "目标已失败，不必再等……"
}
```

`status` 五态：`completed` / `failed` / `stalled` / `timeout` / `cancelled`。**超时不是失败**，单独一态——因为「超时」和「失败」要走的处理逻辑完全不同。

条件语义：

| kind | 必填 | until | 说明 |
| --- | --- | --- | --- |
| `job` | `id` | `settled`（默认）/ `failed` | 作业结束（含失败）或仅失败 |
| `agent` | — | `inactive`（默认）/ `failed` / `status_changed` | 成员全部空闲 / 任一失败 / 任意状态变化 |
| `file` | `path` | `exists`（默认）/ `changed` | 文件出现 / 版本变化 |
| `log` | `path`, `matches` | `matches` | 日志尾部或新增内容命中正则 |

## 四、两个值钱的点：事件驱动 + 卡住检测

**事件驱动**是它和「轮询」的本质区别——但只针对**作业条件**：插件订阅作业事件，作业 settle、输出增长、进度更新时立刻唤醒主循环，**不受 `poll_interval_sec` 限制**；文件、日志、队友条件仍按 `poll_interval_sec` 采样。最硬的证据：

> 对一个**已经启动的 10 秒作业**（`sleep 10; echo EXIT=0 ok`）发起等待，`poll_interval_sec:10`（10 秒才轮询一次）下，等待调用内部 elapsed **4.4 秒**就返回了 `completed`——如果纯轮询，最早也得等到 10 秒那个整数边界。口径说明：4.4 秒是**等待调用内部的耗时**（调用发起时作业已运行约 5.6 秒），它证明事件唤醒不必等下一个轮询边界，**不代表作业运行时间被缩短**，也不能据此得出相对原生工具的提速倍数。

**卡住检测**是原生工具完全没有的能力。`stall_after_sec` 表示：连续 N 秒没有任何进展信号，就立刻返回 `stalled`，而不是干等满整个 timeout：

> `stall_after_sec:5, timeout_sec:60`，等一个 `sleep 300` 的作业，**5.0 秒**就返回 `stalled`，并附「可能已卡死」提示，而不是等满 60 秒。

## 五、硬拦截：把空等的路堵死

规则很克制，只拦「空等」，不误伤正常用法：

| 拦截对象 | 条件 | 处理 |
| --- | --- | --- |
| `bash` | 前台命令含 `sleep ≥ 20s`（不含后台、不含 `&`） | 拒绝，并给 5 条 `wait_until` 替代示例 |
| `job_output` | `wait:true` 且 `timeout_ms > 120000` | 拒绝，要求改用 `wait_until` 分段等待 |
| `wait_agent` | `timeout_ms > 120000` | 拒绝，要求改用 agent 条件 |

`sleep 3`、后台 `sleep`、普通命令都不受影响——验收里专门测了 `sleep 3 && echo SLEEP3_DONE`，正常放行。

## 六、双环境实测：安装前 vs 安装后的效率变化

我在两个环境都装上了：**macOS（Node 24）**做的是完整基线 + 交叉验收（`docs/baseline.md`、`docs/acceptance.md`），**Windows 桌面版（DSH 0.2.2-rc.1，Node 24）**做的是日常安装 + 冒烟。两边数据互相对得上。

### 总对比表

| 场景 | 安装前（原生工具实测） | 安装后（wait_until） | 变化 |
| --- | --- | --- | --- |
| 卡住检测 | **没有这个能力**。`wait_agent` 等满 10s 只回 `{"timedOut":true}`，分不清「卡死」还是「正常无进展」 | `stall_after_sec:5` → 等待调用内部 elapsed **5.0s** 返回 `stalled`（不等满 60s） | 从「只能等满超时且语义空洞」到「有明确的 stalled 判定」 |
| 发现失败 | `job_output` 能返回退出码与 stderr，但「进程退出码非零」被记为 `completed`，需要自己识别；`wait_agent` 对队友失败完全无感知 | `fail_fast` 识别退出码 / `EXIT=N` 文本，等待调用立即返回 `failed` + 原因（等待调用内部毫秒级 elapsed，非作业总时长） | 从「自己识别退出码」到「插件直接判 failed」 |
| 等后台作业完成 | `job_output(wait:true)` 在作业完成/失败时也会被事件唤醒（基线实验 1c），但只在「超时」或「结束」两个时机交付，且返回增量输出；运行中调用要等满 timeout 才交付中间输出（实验 2） | 作业事件即时唤醒并返回结构化五态 + `output_tail`；**4.4s** 是等待调用内部 elapsed（调用时作业已运行约 5.6s） | 从「超时/结束才交付」到「事件唤醒 + 结构化结果」 |
| 等队友 | `wait_agent` 最小粒度 10s，等满回布尔，事后还得 `list_agents` | `agent` 条件，结构化返回谁空闲/谁失败/状态变化（按 poll_interval 采样） | 从「两轮调用」到「一轮判定」 |
| 手工 sleep 轮询 | `sleep 90 → 查 → 再 sleep`，一轮约 1.5 分钟 | 前台 `sleep ≥ 20s` 被 guard **即时拒绝**并给替代 | 从源头杜绝空等 |
| 超长等待 | `job_output` / `wait_agent` 可设到十几分钟等满 | guard **即时拒绝 > 120s**，强制分段 | 不再干烧超时 |

### 关键数字（都有逐秒时间线存档）

> **计时口径**：下面的「秒数」都是**等待调用内部的 `elapsed`**（从 `wait_until` 调用开始到返回），不是作业运行总时长，也不是与原生工具同口径的提速倍数。原生基线报告的墙钟窗口包含模型生成下一步工具调用的延迟（实测约 2–7 秒），不能直接与插件内部计时比较。

- **事件唤醒（等待窗口）**：对一个已启动的 `sleep 10` 作业发起等待，`poll_interval_sec:10` 下等待调用内部 elapsed **4.4s** 返回 completed（macOS 验收，用例 3；调用时作业已运行约 5.6s）。
- **卡住检测**：`stall_after_sec:5` 下等待调用内部 elapsed **5.0s** 返回 stalled（macOS 验收，用例 2）。
- **失败判定**：立即失败的作业（`exit 3` + `EXIT=3` 输出），等待调用内部 elapsed **3ms** 返回 failed（macOS 验收，用例 1b）——这是等待调用耗时，不是从作业启动到失败的总耗时。
- **批量等待**：file + job 两条件 wait_all，等待调用内部 elapsed **5.5s** 返回，字段齐全（macOS 验收，用例 5）。
- **安装与冒烟**（Windows 桌面版）：安装 **9 秒**、包体 **约 54KB**、**零运行时依赖**、装完 **热生效无需重启**；等已存在文件 **2ms**、等 2 秒后台作业 **3ms** 返回 completed（条件早已满足的立即返回）。

### 三点解读（避免被误读成「吹」）

1. 冒烟的 **2ms / 3ms** 是「条件早已满足、立即返回」，证明的是**不会空等**；真正等待窗口里的表现看 4.4s / 5.0s 那几个才是关键，而且它们都是等待调用内部耗时，不是作业总时长。
2. **9 秒装完、54KB、零依赖**，几乎不拖慢 DSH 启动，也不拉一堆依赖进来。
3. 装完 `application: applied` 之后，`wait_until` 立刻出现在当前会话工具列表，**不用重启应用**——这对桌面用户很友好。

## 七、工程细节（含一个诚实的坑）

- **零依赖**：插件跑在宿主进程里，profile 的 `node_modules` 不保证提供 `@deepseek-ai/*` 包，import 它们会解析失败。所以工具 schema 是手写的标准 JSON Schema，整个插件只有一个 `index.js`。
- **非零退出码识别**：平台把「进程退出但 exit code 非零」也记为 `completed`，插件会识别退出码并自行判定为 `failed`。**这个点我第一版没做对**——v1.0.0 交叉验收里 `exit 3` 的作业被判成 `completed`（报告如实标了「未通过」），1.0.3 才修掉并在线上验证通过。
- **日志正则提前失败**：进程还没退出、但日志已打出 `EXIT=3`，也能提前返回 `failed`。

## 八、验证方式

没靠「感觉能用」，而是两份存档报告 + 单测：

- `docs/baseline.md`：改造前基线，先测清原生工具真实行为。
- `docs/acceptance.md`：独立交叉验收，5 组用例、逐秒时间线。
- `test/unit.mjs`：**251 条断言**（v1.0.5 时点；v1.1.0 起为 274 条），覆盖立即失败、非零退出码、事件唤醒、卡住、超时、取消、wait_all 语义、文件/日志/队友条件、guard 规则。

验收里「未通过」和「描述与实现不一致」的条目也原样留在了报告里，没删。

## 九、已知限制（不藏着）

- 模型在**思考阶段**是否萌生「等 180 秒」的念头无法直接干预；插件只保证这个念头一旦落成工具调用，就被拦下并改道。
- `agent` 条件依赖 Agent Teams 服务，非 Team 会话调用会立即返回 `failed` 并说明原因，不会空等。
- 多 `conditions` 是 **wait_all** 语义（全部满足才 `completed`），想「任一完成就返回」要拆成多次调用。

## 十、安装

```sh
dsh plugin --profile web add dsh-tool-wait-until
```

桌面应用里，直接在插件管理器搜索 `dsh-tool-wait-until` 安装即可。要求 dsh 0.2.1 或更高（`engines.dsh`），实测 0.2.1-rc.5。

---

仓库：<https://github.com/tongsh6/dsh-tool-wait-until>
npm：<https://www.npmjs.com/package/dsh-tool-wait-until>

如果你也在被 Agent 的空等折磨，欢迎装上试试；发现问题直接开 issue，好用的话顺手点个 star，谢谢。
