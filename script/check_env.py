# import platform
# import shutil
# import subprocess
# import sys
# import json
# import argparse

# # 控制台输出颜色配置 (ANSI 转义码)
# class Colors:
#     GREEN = "\033[92m"
#     RED = "\033[91m"
#     YELLOW = "\033[93m"
#     CYAN = "\033[96m"
#     RESET = "\033[0m"

# def check_command(tool_name, cmd_name, version_flag="--version", get_version=True):
#     """
#     检查指定命令并返回结构化的字典数据。
#     """
#     path = shutil.which(cmd_name)

#     # 基础结构化数据
#     result = {
#         "tool_name": tool_name,
#         "command": cmd_name,
#         "installed": False,
#         "path": None,
#         "version": None,
#         "status": "未安装，或其路径未添加到系统环境变量 (PATH) 中"
#     }

#     if not path:
#         return result

#     result["installed"] = True
#     result["path"] = path

#     if not get_version:
#         result["status"] = "已安装 (跳过版本检查以防弹窗)"
#         return result

#     try:
#         creationflags = 0
#         if platform.system() == "Windows":
#             creationflags = subprocess.CREATE_NO_WINDOW

#         process_result = subprocess.run(
#             f"{cmd_name} {version_flag}",
#             capture_output=True,
#             text=True,
#             shell=True,
#             timeout=5,
#             creationflags=creationflags,
#         )

#         output = process_result.stdout.strip() or process_result.stderr.strip()
#         version_info = output.split("\n")[0] if output else "获取成功，但无输出"

#         result["version"] = version_info
#         result["status"] = "正常"

#     except subprocess.TimeoutExpired:
#         result["status"] = "获取版本信息超时"
#     except Exception as e:
#         result["status"] = f"无法执行命令 ({e})"

#     return result

# def print_human_readable(env_info, tools_data):
#     """打印适合人类阅读的彩色控制台输出"""
#     print(f"\n{Colors.CYAN}============== 开发环境自检脚本 =============={Colors.RESET}")
#     print(f"系统架构: {env_info['architecture']}")
#     print(f"系统类型: {Colors.CYAN}{env_info['os_type']} {env_info['os_release']}{Colors.RESET}")
#     print(f"执行脚本的 Python: v{env_info['python_version']}")
#     print(f"{Colors.CYAN}----------------------------------------------{Colors.RESET}\n")

#     if env_info['os_type'] == "Windows":
#         print(f"开始安静检测 Windows 核心 C++ 及交叉编译工具链...\n")

#         for tool in tools_data:
#             if not tool["installed"]:
#                 print(f"{Colors.RED}[FAIL] {tool['tool_name']}{Colors.RESET}")
#                 print(f"    - 状态: {tool['status']}\n")
#             elif tool["status"] == "正常":
#                 print(f"{Colors.GREEN}[OK] {tool['tool_name']}{Colors.RESET}")
#                 print(f"    - 路径: {tool['path']}")
#                 print(f"    - 版本: {tool['version']}\n")
#             elif tool["status"].startswith("已安装"):
#                 print(f"{Colors.GREEN}[OK] {tool['tool_name']}{Colors.RESET}")
#                 print(f"    - 路径: {tool['path']}")
#                 print(f"    - 状态: {tool['status']}\n")
#             else:
#                 print(f"{Colors.YELLOW}[WARN] {tool['tool_name']}{Colors.RESET}")
#                 print(f"    - 路径: {tool['path']}")
#                 print(f"    - 状态: {tool['status']}\n")
#     else:
#          print(f"{Colors.YELLOW}当前为 {env_info['os_type']} 环境，跳过 Windows 专属工具链检查。{Colors.RESET}\n")

#     print(f"{Colors.CYAN}=============================================={Colors.RESET}\n")

# def main():
#     # 1. 解析命令行参数
#     parser = argparse.ArgumentParser(description="开发环境自检脚本")
#     parser.add_argument("--json", action="store_true", help="输出结构化的 JSON 格式数据")
#     args = parser.parse_args()

#     # 2. 收集系统环境信息
#     env_info = {
#         "architecture": platform.machine(),
#         "os_type": platform.system(),
#         "os_release": platform.release(),
#         "python_version": sys.version.split(' ')[0]
#     }

#     # 3. 收集工具信息
#     tools_data = []
#     if env_info["os_type"] == "Windows":
#         tools_data.extend([
#             check_command("Git", "git"),
#             check_command("CMake", "cmake"),
#             check_command("Visual Studio Code", "code", get_version=False),
#             check_command("LLVM-MinGW (C 编译器 clang)", "clang"),
#             check_command("LLVM-MinGW (C++ 编译器 clang++)", "clang++"),
#             check_command("Python", "python")
#         ])

#     # 4. 根据参数决定输出格式
#     if args.json:
#         # 输出结构化 JSON
#         final_output = {
#             "system_info": env_info,
#             "tools": tools_data
#         }
#         # indent=4 保证打印出来的 JSON 带有缩进，ensure_ascii=False 保证中文正常显示
#         print(json.dumps(final_output, indent=4, ensure_ascii=False))
#     else:
#         # 默认输出彩色文本
#         print_human_readable(env_info, tools_data)

# if __name__ == "__main__":
#     main()
#     exit(0)


# # import sys
# # import json


# # def main():
# #     # ...
# #     # 构造 JSON 响应
# #     # response = {"additionalContext": "环境检查未通过：需要 Python 3.12 或更高版本。"}
# #     # print(json.dumps(response))

# #     with open('hook_debug.log', 'w') as f:
# #         f.write('SessionStart hook executed!\n')

# #     condition_met = False

# #     if not condition_met:
# #         response = {
# #             "continue": True,
# #             "hookSpecificOutput": {
# #                 "hookEventName": "SessionStart",
# #                 "additionalContext": "环境检查未通过：需要 Python 3.12 或更高版本。"
# #             }
# #         }
# #         # 关键：这里用 print 输出到 stdout
# #         print(json.dumps(response))
# #         sys.exit(0)

# #     sys.exit(0)


import sys, json


def main():
    # 模拟环境检查结果
    condition_met = False

    if not condition_met:
        # 构造符合 Claude Code 规范的上下文注入消息
        response = {
            "continue": True,  # 会话继续
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "环境检查未通过：需要 Python 3.12 或更高版本。",
            },
        }
        # 将 JSON 响应打印到 stdout
        print(json.dumps(response))
        sys.exit(0)  # 成功退出
    # ...


if __name__ == "__main__":
    main()
