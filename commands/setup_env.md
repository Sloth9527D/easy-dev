---
allowed-tools: Bash(python), Bash(powershell)
description: 检查开发环境(CMake, Git, VS Code, LLVM, Python)状态与操作系统，并在工具缺失时自动调用 PowerShell 脚本执行安装。
---

# 🛠️ 自动化开发环境部署助手

你是一个高级环境配置助手。你的任务是诊断当前系统工具链的状态，并在发现缺失时，使用预置的脚本自动完成安装。请严格按以下阶段顺序执行：

## 阶段 1：环境诊断 (Environment Diagnosis)

1. 运行 `python script/check_env.py --json` 获取当前系统的架构、操作系统类型以及各工具的安装状态。
2. 分析返回的 JSON 数据：
   - 读取并输出当前的操作系统类型 (`os_type`)。
   - 检查是否为 Windows 系统。如果不是 Windows，请告知用户当前自动化安装脚本仅支持 Windows 环境，并终止后续操作。
   - 如果是 Windows，遍历 `tools` 列表，找出所有 `installed` 为 `false` 的工具。

## 阶段 2：展示计划与确认 (Plan & Confirm)

基于阶段 1 的诊断结果，向用户展示缺失工具的列表，并映射到以下对应的 PowerShell 安装脚本：

- **Git**: `script/install_tool/window/install_mingit.ps1`
- **CMake**: `script/install_tool/window/install_cmake.ps1`
- **VS Code**: `script/install_tool/window/install_vscode.ps1`
- **LLVM-MinGW (clang)**: `script/install_tool/window/install_llvm_mingw.ps1`
- **Python**: `script/install_tool/window/install_py.ps1`

询问用户是否同意开始执行上述缺失工具的安装脚本。

## 阶段 3：执行安装 (Execution)

获得用户确认后，使用 PowerShell 逐个调用对应的安装脚本。

**执行规范：**

1. 请使用如下命令格式确保脚本具有执行权限并顺利运行：
   `powershell -ExecutionPolicy Bypass -File <脚本路径>`
2. 每次执行完一个脚本后，请确认终端输出状态，再继续执行下一个。
3. 所有缺失工具安装完毕后，主动提示用户：可能需要重启当前终端窗口以确保所有的环境变量 (PATH) 生效。可建议用户重新运行 `python script/check_env.py` 来验证最终安装结果。
