import os
import platform
import re
from typing import Tuple, List, Dict
from openai import OpenAI
import config
from command_parser import clean_command
from logger import log_error

client = None


def reset_client():
    """配置变更后重置客户端"""
    global client
    client = None


def get_client():
    global client
    if not client:
        client = OpenAI(api_key=config.API_KEY, base_url=config.API_BASE)
    return client

# 对话历史
history: List[Dict[str, str]] = []


def _get_platform_rules(os_info: str) -> str:
    """根据操作系统返回平台专用规则"""
    if os_info == "Windows":
        return """
6. 【关键】对于耗时操作，必须插入 Write-Output 显示进度（严禁 Write-Host）。
7. 【路径】涉及到桌面、文档、下载时，使用 PowerShell 动态获取：
   - 桌面: [Environment]::GetFolderPath("Desktop")
   - 文档: [Environment]::GetFolderPath("MyDocuments")
   - 用户目录: $env:USERPROFILE
8. 【Excel/Word/PowerPoint】使用 COM 对象，$excel.DisplayAlerts=$false、$word.Visible=$true；错误处理用 try {{ }} catch {{ Write-Output "错误: $_"; exit 1 }}
"""
    else:
        return """
6. 【关键】使用 bash/zsh 语法，用 echo 显示进度。严禁使用 PowerShell 语法。
7. 【路径】使用 $HOME、~/Desktop、~/Documents、~/Downloads，严禁硬编码 /Users/xxx。
8. 【macOS 应用】打开应用用 open -a "应用名"；操作 Office 用 open 打开文件，或 osascript 调用 AppleScript。macOS 无 COM 对象，严禁生成 PowerShell 代码。
"""


def get_ai_command(user_input: str, os_info: str, shell_info: str) -> Tuple[str, str]:
    """
    [COMMAND 模式]
    使用 AI 将自然语言转换为 CLI 命令
    """
    
    platform_rules = _get_platform_rules(os_info)
    system_prompt = f"""
你是一个专业的 CLI 助手。你的任务是将用户的自然语言描述转换为准确的命令行指令。
当前环境: OS={os_info}, Shell={shell_info or "sh"}, CWD={os.getcwd()}

【重要】必须根据 OS 生成对应平台的命令：Darwin/Linux 用 bash/zsh，Windows 用 PowerShell。

规则:
1. 直接输出命令，不要使用 Markdown 代码块格式。
2. 如果需要解释，请在命令后换行，用 "# EXPL: " 开头写一句话解释。
3. 确保命令在当前环境下可执行。
4. 即使有风险（如删除），也请输出命令，由用户确认。
5. 优先使用相对路径。
{platform_rules}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = get_client().chat.completions.create(
            model=config.MODEL,
            messages=messages,
            temperature=0
        )
        
        full_text = response.choices[0].message.content.strip()
        
        # 移除所有 "# EXPL: ..." 行（每行一个），保留完整命令（支持多行多命令）
        command_text = re.sub(r'\n\s*# EXPL: [^\n]*', '', full_text)
        command_text = re.sub(r'^\s*# EXPL: [^\n]*\n?', '', command_text).strip()
        command_text = re.sub(r'\n{3,}', '\n\n', command_text)  # 合并多余空行
        command = clean_command(command_text)
        # 取第一个 # EXPL: 作为简要说明
        expl_match = re.search(r'# EXPL:\s*([^\n]+)', full_text)
        explanation = expl_match.group(1).strip() if expl_match else "执行操作"

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
            model=config.MODEL,
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
