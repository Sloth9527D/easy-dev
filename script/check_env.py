#!/usr/bin/env python3
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
    # 用于临时存储检查结果的字典
    check_res = {}
    for key, info in COMPONENTS.items():
        # 1. 拦截特殊内部模块处理 (如 Python)
        if info.get("type") == "internal":
            if key == "python":
                check_res[key] = platform.python_version()
            continue

        # 2. 常规命令行工具版本检查
        cmd = info["cmd"]
        version = get_tool_version(cmd, info["args"], info["line_idx"])
        check_res[key] = version  # 成功是版本号字符串，失败是 None

    # # 3. 检查核心工具是否存在，决定 continue 状态
    continue_session = not any(
        check_res.get(tool) is None for tool in COMPONENTS.keys()
    )

    # 4. 构建上下文字符串
    context_segments = []
    for key in ["git", "cmake", "python", "vscode", "llvm"]:
        val = check_res.get(key)
        val_str = val if val else "not_found"
        context_segments.append(f"{key}: {val_str}")

    additional_context = ", ".join(context_segments)

    # 5. 构造最终的响应负载
    response_payload = {
        "continue": continue_session,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        },
    }

    output_json = json.dumps(response_payload, ensure_ascii=False)

    # 6. 根据 continue_session 选择输出流和退出码
    if continue_session:
        # 成功：输出到 stdout，退出码 0
        sys.stdout.write(output_json)
        sys.stdout.flush()
        sys.exit(0)
    else:
        # 失败：输出到 stderr，退出码 1
        sys.stderr.write(output_json)
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
