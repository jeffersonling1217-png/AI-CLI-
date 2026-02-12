import os
import sys
import subprocess
import platform
import base64
from rich.console import Console
from logger import log_error, log_execution_error

console = Console()

def handle_cd_command(command: str) -> bool:
    """
    特殊处理 cd 命令
    返回 True 表示已处理（不需要 subprocess 执行），False 表示是普通命令
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
            console.print(f"[green]已切换目录至: {os.getcwd()}[/green]")
            return True
        except Exception as e:
            log_error(f"切换目录失败: {str(e)}")
            return True # 即使失败也算处理过了
            
    return False

def execute_command(command: str, shell_info: str = None):
    """执行命令并打印输出"""
    # 先检查是否是 cd 命令
    if handle_cd_command(command):
        return

    # 保存原始命令（AI 生成的，处理前）
    original_command = command
    full_command = command  # 初始化，后续会被修改
    
    try:
        # 根据检测到的 shell 类型决定执行方式
        if platform.system() == "Windows":
            if shell_info and ("powershell" in shell_info.lower() or "pwsh" in shell_info.lower()):
                # PowerShell：使用 Base64 编码，避免引号转义问题
                # PowerShell 的 -EncodedCommand 需要 UTF-16 LE 编码的 Base64
                encoded_bytes = command.encode('utf-16-le')
                encoded_cmd = base64.b64encode(encoded_bytes).decode('ascii')
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
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd()
        )
        
        # 实时打印输出
        for line in process.stdout:
            console.print(line, end="")
            
        process.wait()
        
        if process.returncode != 0:
            # 读取错误输出
            stderr_output = process.stderr.read()
            
            # 使用 logger 模块输出错误信息
            log_execution_error(
                original_cmd=original_command,
                actual_cmd=full_command, 
                error_msg=stderr_output if stderr_output else "",
                exit_code=process.returncode
            )
            
    except Exception as e:
        # 捕获执行过程中的异常
        log_execution_error(
            original_cmd=original_command,
            actual_cmd=full_command,
            error_msg=str(e),
            exit_code=-1
        )
