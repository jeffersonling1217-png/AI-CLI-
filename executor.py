import os
import sys
import subprocess
import platform
import base64
from rich.console import Console
from logger import log_error, log_execution_error

console = Console()

def handle_cd_command(command: str, output_callback=None):
    """
    特殊处理 cd 命令
    返回 True 表示已处理（不需要 subprocess 执行），False 表示是普通命令
    output_callback: 可选，用于 GUI 等场景输出信息，签名为 (text: str) -> None
    """
    cmd = command.strip()
    
    # 检查是否以 cd 开头
    if cmd.startswith("cd ") or cmd == "cd":
        try:
            target_dir = ""
            if cmd == "cd":
                target_dir = os.path.expanduser("~")
            else:
                # 简单解析：去除 "cd " 前缀
                path_part = cmd[3:].strip()
                # 去除可能的引号
                if (path_part.startswith('"') and path_part.endswith('"')) or \
                   (path_part.startswith("'") and path_part.endswith("'")):
                    target_dir = path_part[1:-1]
                else:
                    target_dir = path_part
            
            # 执行切换目录
            os.chdir(target_dir)
            msg = f"已切换目录至: {os.getcwd()}\n"
            if output_callback:
                output_callback(msg)
            else:
                console.print(f"[green]{msg}[/green]")
            return True
        except Exception as e:
            err_msg = f"切换目录失败: {str(e)}\n"
            if output_callback:
                output_callback(err_msg)
            else:
                log_error(err_msg)
            return True # 即使失败也算处理过了
            
    return False

def execute_command(command: str, shell_info: str = None, output_callback=None):
    """执行命令并打印输出。output_callback(text) 可选，用于 GUI 等场景接收输出。"""
    # 先检查是否是 cd 命令
    if handle_cd_command(command, output_callback):
        return

    # 保存原始命令（AI 生成的，处理前）
    original_command = command
    full_command = command  # 初始化，后续会被修改
    encoded_command = None  # Base64 编码后的命令（仅用于错误显示）
    
    try:
        # 根据检测到的 shell 类型决定执行方式
        if platform.system() == "Windows":
            if shell_info and ("powershell" in shell_info.lower() or "pwsh" in shell_info.lower()):
                # PowerShell：使用 Base64 编码，避免引号转义问题
                # 强制设置输出编码为 UTF-8，防止中文乱码
                pre_cmd = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                full_cmd_str = pre_cmd + command
                encoded_bytes = full_cmd_str.encode('utf-16-le')
                encoded_cmd = base64.b64encode(encoded_bytes).decode('ascii')
                encoded_command = encoded_cmd  # 保存用于错误显示
                full_command = f'powershell.exe -EncodedCommand {encoded_cmd}'
            elif shell_info and ("cmd" in shell_info.lower() or "command" in shell_info.lower()):
                # cmd：直接使用原命令
                full_command = command
            else:
                # 默认使用 cmd（向后兼容）
                full_command = command
        else:
            # Linux/Mac 使用默认 shell
            full_command = command
        
        # 统一使用 shell=True 执行
        process = subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 【修复】合并错误输出到标准输出，防止死锁
            text=True,
            encoding='utf-8',          # 【修复】强制使用 UTF-8 读取
            errors='replace',          # 【修复】遇到编码错误替换为 ?，防止崩溃
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd()
        )
        
        # 实时打印输出
        for line in process.stdout:
            if output_callback:
                output_callback(line if line.endswith('\n') else line + '\n')
            else:
                console.print(line, end="")
            
        process.wait()
        
        if process.returncode != 0:
            # 错误信息已经在 stdout 中输出了，这里只报告状态
            err_msg = f"命令执行退出，代码: {process.returncode}"
            
            if output_callback:
                output_callback(f"\n[ERROR] {err_msg}\n")
            else:
                log_execution_error(
                    original_cmd=original_command,
                    actual_cmd=full_command, 
                    error_msg=err_msg,
                    exit_code=process.returncode
                )
            
    except Exception as e:
        # 捕获执行过程中的异常
        err_block = f"\n[执行异常] {str(e)}\n"
        if output_callback:
            output_callback(err_block)
        else:
            log_execution_error(
                original_cmd=original_command,
                actual_cmd=full_command,
                error_msg=str(e),
                exit_code=-1
            )
