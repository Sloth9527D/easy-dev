import shutil
import subprocess
import sys
import json
import re
import platform

# 定义需要检查的工具组件配置
COMPONENTS = {
    "git": {"cmd": "git", "args": ["--version"], "line_idx": 0},
    "cmake": {"cmd": "cmake", "args": ["--version"], "line_idx": 0},
    "python": {"type": "internal"},  # 特殊处理：使用内置模块获取
    "vscode": {
        "cmd": "code.cmd" if sys.platform == "win32" else "code",
        "args": ["--version"],
        "line_idx": 0,
    },
    "llvm": {"cmd": "clang", "args": ["--version"], "line_idx": 0},
}


def clean_version_string(raw_str: str) -> str:
    """从原始字符串中提取 x.y 或 x.y.z 格式的版本号"""
    match = re.search(r"(\d+\.\d+(?:\.\d+)?)", raw_str)
    return match.group(1) if match else raw_str


def get_tool_version(cmd: str, args: list, line_idx: int) -> str | None:
    """通过命令行获取工具版本号，如果未安装则返回 None"""
    try:
        # 优先获取可执行文件的绝对路径，避免别名问题
        path = shutil.which(cmd)
        if not path:
            return None

        result = subprocess.run(
            [path] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().split("\n")

        if lines and len(lines) > line_idx:
            raw_version = lines[line_idx].strip()
            return clean_version_string(raw_version)

        return "unknown_version"

    except subprocess.CalledProcessError:
        return "unknown_version"
    except Exception as e:
        print(f"[DEBUG] Error getting {cmd} version: {str(e)}", file=sys.stderr)
        return None


def main():
    additional_context = {}

    for key, info in COMPONENTS.items():
        # 1. 拦截特殊内部模块处理 (如 Python)
        if info.get("type") == "internal":
            if key == "python":
                # 直接通过内置模块获取 Python 版本，绕过 WindowsApps 商店别名陷阱
                additional_context[key] = (True, platform.python_version())
            continue

        # 2. 常规命令行工具版本检查
        cmd = info["cmd"]
        version = get_tool_version(cmd, info["args"], info["line_idx"])

        if version:
            additional_context[key] = (True, version)
        else:
            additional_context[key] = (False, "not_found")

    # 3. 检查核心工具，决定是否继续会话
    required_tools = ["git", "python", "vscode", "llvm"]
    continue_session = True

    for tool in required_tools:
        # 检查 additional_context 元组中的布尔值 (index 0)
        if tool in additional_context and not additional_context[tool][0]:
            continue_session = False
            break

    # 4. 构造结构化的 JSON Hook 响应
    response_payload = {
        "continue": continue_session,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        },
    }

    # 5. 根据继续状态重定向输出流
    output_json = json.dumps(response_payload, ensure_ascii=False, indent=2)

    if continue_session:
        print(output_json, file=sys.stdout)
        sys.exit(0)
    else:
        print(output_json, file=sys.stderr)
        sys.exit(1)  # 返回非 0 状态码，进一步确保主程序识别到异常并阻断


if __name__ == "__main__":
    main()
