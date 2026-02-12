import os
import sys
import platform
import shellingham
from rich.prompt import Confirm
from rich.panel import Panel
from rich.console import Console
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

# 导入模块
from config import check_env
from ai_engine import get_ai_command
from executor import execute_command
from logger import log_ai_suggestion, log_ai_thinking, log_error, log_info

console = Console()
# 历史记录管理器
history = InMemoryHistory()

# 定义 prompt_toolkit 样式
prompt_style = Style.from_dict({
    'cwd': 'bold #00ff00',  # 对应 [bold green]
    'arrow': '',
})

def get_shell_info() -> tuple[str, str]:
    """获取当前操作系统和 Shell 信息"""
    os_name = platform.system()
    try:
        shell_name, _ = shellingham.detect_shell()
    except Exception:
        shell_name = "unknown"
    return os_name, shell_name

def read_user_input(cwd_display: str) -> str:
    """读取用户输入 (使用 prompt_toolkit)。
    
    说明：使用 prompt_toolkit 接管输入，彻底解决中文输入法光标错位、
    字符截断、无法退格等终端兼容性问题。同时支持历史记录（上下键）。
    """
    try:
        # 使用 HTML 格式的 prompt，模拟之前的 rich 样式
        # 这里的格式是 prompt_toolkit 特有的 HTML 类似语法，或者直接使用 fragments
        # 简单起见，我们构造一个带样式的 prompt 列表
        from prompt_toolkit.formatted_text import HTML
        
        return pt_prompt(
            HTML(f"\n<cwd>{cwd_display} ></cwd> "),
            style=prompt_style,
            history=history
        )
    except EOFError:
        return "exit"
    except KeyboardInterrupt:
        return ""

def main():
    # 检查环境变量
    check_env()

    os_info, shell_info = get_shell_info()
    
    console.print(Panel.fit(
        f"AI CLI 助手已启动 (v2.0)\n环境: [bold blue]{os_info}[/bold blue] | Shell: [bold blue]{shell_info}[/bold blue]",
        title="Welcome",
        border_style="green"
    ))

    while True:
        try:
            # 显示当前目录
            cwd_display = os.getcwd()
            user_input = read_user_input(cwd_display)
            
            if user_input.lower() in ["exit", "quit", "退出"]:
                break
                
            if not user_input.strip():
                continue

            # 获取 AI 建议
            with log_ai_thinking():
                command, explanation = get_ai_command(user_input, os_info, shell_info)

            if not command:
                continue

            # 显示 AI 建议
            log_ai_suggestion(explanation, command)

            # 确认执行
            if Confirm.ask("执行吗？"):
                console.print("[bold yellow]Running...[/bold yellow]\n")
                execute_command(command, shell_info)
            else:
                console.print("[dim]已取消[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]程序已中断。[/yellow]")
            break
        except Exception as e:
            log_error(f"System Error: {str(e)}")

if __name__ == "__main__":
    main()
