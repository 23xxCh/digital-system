# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智能制造数字孪生系统 (Smart Manufacturing Digital Twin System) — 工业 4.0 架构参考设计项目。

**虚构生产线组成：**
- 3 台 CNC 数控机床
- 2 台六轴机器人
- 1 台 AGV 自动导引车
- 1 座自动化仓库
- 生产 2 种精密零件

**核心技术栈：**
- OPC UA 信息模型（设备建模、NodeId 设计）
- Python 数字孪生类定义
- MES-PLC 交互序列
- 强化学习 (DQN) 动态调度
- Purdue 模型工业安全架构

**项目状态：** 初创阶段，设计文档编写中

## Agent skills

### Backlog

GitHub Issues at [23xxCh/digital-system](https://github.com/23xxCh/digital-system). See `docs/agents/backlog.md`.

### Triage labels

Using default label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout with `CONTEXT.md` and `docs/adr/` at repo root. See `docs/agents/domain.md`.
