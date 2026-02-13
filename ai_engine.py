import os
import platform
from typing import Tuple, List, Dict
from openai import OpenAI
from config import API_KEY, API_BASE, MODEL
from command_parser import clean_command
from logger import log_error

client = None

def get_client():
    global client
    if not client:
        client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    return client

# 对话历史
history: List[Dict[str, str]] = []

def get_ai_command(user_input: str, os_info: str, shell_info: str) -> Tuple[str, str]:
    """
    [COMMAND 模式]
    使用 AI 将自然语言转换为 CLI 命令
    """
    
    # 针对命令生成的 System Prompt
    system_prompt = f"""
你是一个专业的 CLI 助手。你的任务是将用户的自然语言描述转换为准确的命令行指令。
当前环境: OS={os_info}, Shell={shell_info}, CWD={os.getcwd()}

规则:
1. 直接输出命令，不要使用 Markdown 代码块格式。
2. 如果需要解释，请在命令后换行，用 "# EXPL: " 开头写一句话解释。
3. 确保命令在当前环境下可执行。
4. 即使有风险（如删除），也请输出命令，由用户确认。
5. 优先使用相对路径。
6. 【关键】对于耗时操作（如文件处理、网络请求、Excel操作），必须插入打印语句（使用 Write-Output 或 echo，严禁使用 Write-Host）来显示当前正在进行的步骤（例如 "正在打开 Excel...", "正在处理数据..."）。Write-Host 会导致输出乱码，绝对禁止。
7. 【路径处理】涉及到系统特殊文件夹（如桌面、文档、下载）时，严禁硬编码绝对路径（如 C:\\Users\\...）。必须使用 PowerShell 的动态获取方式：
   - 桌面: [Environment]::GetFolderPath("Desktop")
   - 文档: [Environment]::GetFolderPath("MyDocuments")
   - 用户目录: $env:USERPROFILE
    8. 【Excel/Word/PowerPoint 特别规则】
       - 对于 Excel: 
          $excel.DisplayAlerts = $false
          $excel.Visible = $true
       - 对于 Word:
          $word.DisplayAlerts = 0  # wdAlertsNone (必须是整数0，不是$false)
          $word.Visible = $true
          $filePath = [string]$filePath # 确保所有路径变量强制类型转换为 [string]
          保存时使用: $doc.SaveAs([ref]$filePath)
       - 错误处理:
          涉及 COM 操作的代码块必须用 try {{ ... }} catch {{ Write-Output "错误: $_"; exit 1 }} 包裹，防止输出 CLIXML 格式的错误堆栈。
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0
        )
        
        full_text = response.choices[0].message.content.strip()
        
        if "# EXPL: " in full_text:
            parts = full_text.split("# EXPL: ", 1)
            command = clean_command(parts[0])
            explanation = parts[1].strip()
        else:
            command = clean_command(full_text)
            explanation = "执行操作"

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_text})
        
        return command, explanation

    except Exception as e:
        log_error(f"AI Command 调用失败: {str(e)}")
        return "", ""

def get_ai_chat(user_input: str) -> str:
    """
    [CHAT 模式]
    纯对话模式，不生成命令
    """
    system_prompt = "你是一个智能助手。请用简洁、友好的语言回答用户的问题。不要生成代码或命令，除非用户明确要求代码示例（但不是为了执行）。"
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7 
        )
        
        reply = clean_command(response.choices[0].message.content.strip())
        
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})
        
        return reply

    except Exception as e:
        log_error(f"AI Chat 调用失败: {str(e)}")
        return "抱歉，我暂时无法回答。"
