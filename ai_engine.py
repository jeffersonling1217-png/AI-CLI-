import os
import platform
from typing import Tuple, List, Dict
from openai import OpenAI
from config import API_KEY, API_BASE, MODEL
from command_parser import clean_command
from logger import log_error

client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# 对话历史
history: List[Dict[str, str]] = []

def get_ai_command(user_input: str, os_info: str, shell_info: str) -> Tuple[str, str]:
    """使用 AI 将自然语言转换为 CLI 命令"""
    
    # 构造 System Prompt，包含可见性和防弹窗规则
    system_prompt = f"""
你是一个专业的 CLI 助手。你的任务是将用户的自然语言描述转换为准确的命令行指令。
当前环境: OS={os_info}, Shell={shell_info}, CWD={os.getcwd()}

规则:
1. 直接输出命令，不要使用 Markdown 代码块格式。
2. 如果需要解释，请在命令后换行，用 "# EXPL: " 开头写一句话解释。
3. 确保命令在当前环境下可执行。
4. 即使有风险（如删除），也请输出命令，由用户确认。
5. 优先使用相对路径。
6. 【关键】对于耗时操作（如文件处理、网络请求、Excel操作），必须插入打印语句（如 echo 或 Write-Host）来显示当前正在进行的步骤（例如 "正在打开 Excel...", "正在处理数据..."），以便用户知道程序在运行。
7. 【Excel/Word 特别规则】如果涉及 Office COM 对象操作：
   - 必须设置 $app.Visible = $true （让程序可见，防止后台假死）
   - 必须设置 $app.DisplayAlerts = $false （禁止弹窗，防止卡死）
   - 操作完成后必须恢复 DisplayAlerts = $true 并正确退出。
"""

    # 构建消息
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0
        )
        
        full_text = response.choices[0].message.content.strip()
        
        # 解析命令和解释
        if "# EXPL: " in full_text:
            parts = full_text.split("# EXPL: ", 1)
            command = clean_command(parts[0])
            explanation = parts[1].strip()
        else:
            command = clean_command(full_text)
            explanation = "执行操作"

        # 更新历史
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_text})
        
        return command, explanation

    except Exception as e:
        log_error(f"AI 调用失败: {str(e)}")
        return "", ""
