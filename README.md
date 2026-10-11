# ResearchPilot

科研实验数据管理与大模型 Agent 辅助分析系统。

## 1. 项目简介

ResearchPilot 是一个面向科研实验场景的智能辅助系统，旨在解决实验数据分散、科研资料繁杂，以及实验结果难以与相关科研知识关联分析的问题。

系统支持 MATLAB 实验数据导入、SQLite 数据管理、科研知识 RAG 检索，并通过基于 Qwen Tool Calling 的多轮 Agent Loop，完成实验查询与科研辅助问答。

## 2. 核心功能

- **实验数据管理**：解析 MATLAB 实验文件，记录 KF、KINJ 等实验参数及不同读出方式的准确率。
- **数据库查询**：基于 SQLite，实现实验 ID 和参数组合查询。
- **科研知识检索**：利用文本切分、Embedding、余弦相似度及 Top-K 检索获取相关科研资料。
- **Agent 多轮工具调用**：根据用户问题选择数据库工具或 RAG 工具，并结合工具结果生成回答。
- **FastAPI 接口**：提供实验查询、分析与 Agent 问答等 HTTP API。
- **日志与自动化测试**：使用 Python logging 记录运行状态，使用 pytest 测试数据库和 API 功能。

## 3. 系统架构

**实验数据处理链路**

MATLAB 实验文件 → `importer.py` → `db.py` → SQLite

**科研知识处理链路**

科研文本文档 → `rag.py` → 文本切分与 Embedding → 持久化知识索引

**Agent 问答链路**

用户 → FastAPI (`api.py`) → Agent (`tools.py`) → Qwen

Agent 根据问题选择工具：

- 数据库工具：通过 `db.py` 查询结构化实验数据。
- RAG 工具：通过 `rag.py` 检索科研知识片段。

工具结果返回给 Qwen，模型继续判断是否调用其他工具，或生成最终回答。系统设置最大执行轮数，避免无限循环。

## 4. 技术栈

Python、FastAPI、Pydantic、SQLite、Qwen API、Embedding、RAG、Tool Calling、pytest、Git。

## 5. API 示例

启动开发服务：

`uvicorn api:app --reload`

打开 `/docs` 查看自动生成的 API 文档。

Agent 问答接口：`POST /agent/ask`

请求示例：

`{"question": "实验1的 IQ accuracy 为什么比 I accuracy 低？"}`

响应结构：

`{"answer": "Agent 生成的回答内容"}`

## 6. 运行环境

依赖安装、环境变量配置、科研数据准备步骤将在核对项目实际配置后补充。
