# VocabPill 💊

[English](README.md) | **中文**

**一天一粒单词丸，遗忘绕着走：CET-4 / CET-6 桌面弹窗单词卡。** 零依赖，完全离线，内置 1,150+ 词条。

[![CI](https://github.com/yund229/VocabPill/actions/workflows/ci.yml/badge.svg)](https://github.com/yund229/VocabPill/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)

![demo](https://cdn.jsdelivr.net/gh/yund229/VocabPill@main/assets/demo.gif)

## 为什么做它

背单词 App 想要你的注意力、你的账号和你的打卡焦虑。VocabPill 只做一件事：你学习/打游戏的时候，每隔 N 分钟安静地弹一张卡——单词 → 音标 → 释义 → 例句，点一下「认识 / 不认识」，卡片自己消失。剩下的交给间隔重复。

## 安装

```bash
pip install git+https://github.com/yund229/VocabPill.git
```

没装 Python 的 Windows 用户：去 [Releases](https://github.com/yund229/VocabPill/releases) 下载 `vocabpill.exe`。

## 快速上手

```bash
vocabpill --level cet4 --interval 30m   # 每 30 分钟弹一张四级卡
vocabpill --level cet6 --interval 1h    # 六级，每小时一张
vocabpill --once --level cet4           # 终端里打印一张卡
vocabpill --stats --level cet4          # 今日 12 词 | 已见 58/790 | 已掌握 9
vocabpill --reset --level cet4          # 清空进度
```

## 调度原理

- **莱特纳盒子 0–5** — 每个词从盒子 0 出发；点「认识」升一盒，点「不认识」打回盒子 0
- **最低盒优先** — 弹卡永远从掌握最差的组里抽，新词和忘掉的词回来得更快
- **进度本地持久化** — 状态存在 `~/.vocabpill/state_<level>.json`；没有账号，没有云端
- **偷看不花钱** — `--once` 只打印卡片，不动调度状态

## 内置词库

| 词库 | 词数 | 内容 |
|------|------|------|
| `cet4` | 790 | 单词 / 音标 / 释义 / 例句 |
| `cet6` | 366 | 同格式，已对四级词去重 |

两个词库都是 `vocabpill/data/` 下的纯 JSON，随意编辑替换。

## 设计说明

- **零依赖** — GUI 用的是 Python 自带的 tkinter，无需安装任何东西
- **42 个测试，零 mock** — 调度器、持久化、CLI 全部跑在真实临时文件上
- **无头环境友好** — `--once` / `--stats` / `--reset` 不导入 tkinter，SSH 里也能用

## 对比

| | VocabPill | 背单词 App | Anki |
|---|-----------|-----------|------|
| 离线 | ✅ | 多数 ❌ | ✅ |
| 上手成本 | 零 | 注册 + 导入 | 建牌组 + 导入 |
| 弹窗打扰式复习 | ✅ | ❌ | ❌ |
| 依赖 | 0 | App 本体 | 很重 |

## 更多自研小工具

- [DeskPet](https://github.com/yund229/DeskPet) — Java 桌面宠物
- [SnapOCR](https://github.com/yund229/SnapOCR) — 热键截图 → 离线 OCR
- [DirTidy](https://github.com/yund229/DirTidy) — 自动整理下载文件夹，支持撤销
- [RectGif](https://github.com/yund229/RectGif) — 框选屏幕区域，直接生成 GIF
- [PdfLoft](https://github.com/yund229/PdfLoft) — 一个 CLI 搞定所有 PDF 杂活

## 许可证

MIT
