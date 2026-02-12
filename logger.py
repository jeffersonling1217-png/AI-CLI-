from rich.console import Console
from rich.panel import Panel

console = Console()

def log_info(message: str):
    console.print(f"[bold blue]ℹ️ {message}[/bold blue]")

def log_success(message: str):
    console.print(f"[bold green]✅ {message}[/bold green]")

def log_warning(message: str):
    console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")

def log_error(message: str):
    console.print(f"[bold red]❌ {message}[/bold red]")

def log_ai_thinking():
    return console.status("[bold yellow]AI 正在思考...[/bold yellow]")

def log_ai_suggestion(explanation: str, command: str):
    console.print(f"\n[bold cyan]🤖 AI 建议:[/bold cyan] {explanation}")
    console.print(Panel(f"[bold white]{command}[/bold white]", border_style="cyan"))

def log_command_execution(original_cmd: str, actual_cmd: str):
    # console.print(f"\n[bold yellow]📝 原始命令:[/bold yellow] {original_cmd}") # 简化输出，避免刷屏
    pass 

def log_execution_error(original_cmd: str, actual_cmd: str, error_msg: str, exit_code: int):
    console.print("\n[bold red]════════════════════════════════════════[/bold red]")
    console.print("[bold red]❌ 命令执行失败[/bold red]")
    console.print(Panel(f"[white]{original_cmd}[/white]", title="原始命令", border_style="yellow"))
    console.print(Panel(f"[white]{actual_cmd}[/white]", title="实际执行", border_style="yellow"))
    if error_msg:
        console.print(Panel(f"[red]{error_msg}[/red]", title="错误原因", border_style="red"))
    else:
        console.print(f"[red]命令返回非零退出代码: {exit_code}[/red]")
    console.print(f"[dim]退出代码: {exit_code}[/dim]")
    console.print("[bold red]════════════════════════════════════════[/bold red]\n")
