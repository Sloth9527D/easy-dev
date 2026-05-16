import platform
import shutil
import subprocess
import sys


# 控制台输出颜色配置 (ANSI 转义码)
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def check_command(tool_name, cmd_name, version_flag="--version", get_version=True):
    """
    检查指定命令是否在 PATH 中。
    :param get_version: 是否执行命令获取版本号。如果是容易弹窗的 GUI 软件，建议设为 False
    """
    path = shutil.which(cmd_name)

    if path:
        if not get_version:
            # 针对 VS Code 这种图形化软件，只验证安装路径，不执行命令以免弹窗
            print(f"{Colors.GREEN}[✓] {tool_name}{Colors.RESET}")
            print(f"    - 路径: {path}")
            print(f"    - 状态: 已安装\n")
            return

        try:
            # 针对纯 CLI 工具，静默执行获取版本
            creationflags = 0
            if platform.system() == "Windows":
                creationflags = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(
                f"{cmd_name} {version_flag}",
                capture_output=True,
                text=True,
                shell=True,
                timeout=5,
                creationflags=creationflags,
            )

            output = result.stdout.strip() or result.stderr.strip()
            version_info = output.split("\n")[0] if output else "获取成功，但无输出"

            print(f"{Colors.GREEN}[✓] {tool_name}{Colors.RESET}")
            print(f"    - 路径: {path}")
            print(f"    - 版本: {version_info}\n")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}[!] {tool_name}{Colors.RESET}")
            print(f"    - 路径: {path}")
            print(f"    - 状态: 获取版本信息超时\n")
        except Exception as e:
            print(f"{Colors.YELLOW}[!] {tool_name}{Colors.RESET}")
            print(f"    - 路径: {path}")
            print(f"    - 状态: 无法执行命令 ({e})\n")
    else:
        print(f"{Colors.RED}[✗] {tool_name}{Colors.RESET}")
        print(f"    - 状态: 未安装，或其路径未添加到系统环境变量 (PATH) 中\n")


def main():
    print(
        f"\n{Colors.CYAN}============== 开发环境自检脚本 =============={Colors.RESET}"
    )

    os_type = platform.system()
    print(f"系统架构: {platform.machine()}")
    print(f"系统类型: {Colors.CYAN}{os_type} {platform.release()}{Colors.RESET}")
    print(f"执行脚本的 Python: v{sys.version.split(' ')[0]}")
    print(
        f"{Colors.CYAN}----------------------------------------------{Colors.RESET}\n"
    )

    if os_type == "Windows":
        print(f"开始安静检测 Windows 核心 C++ 及交叉编译工具链...\n")

        # 纯命令行工具，正常获取版本
        check_command("Git", "git")
        check_command("CMake", "cmake")

        # 【核心修改点】VS Code 是图形化界面，关闭 get_version 防止唤醒弹窗！
        check_command("Visual Studio Code", "code", get_version=False)

        check_command("LLVM-MinGW (C 编译器 clang)", "clang")
        check_command("LLVM-MinGW (C++ 编译器 clang++)", "clang++")
        check_command("Python", "python")

    else:
        print(
            f"{Colors.YELLOW}当前为 {os_type} 环境，跳过 Windows 专属工具链检查。{Colors.RESET}\n"
        )

    print(
        f"{Colors.CYAN}=============================================={Colors.RESET}\n"
    )


if __name__ == "__main__":
    main()
