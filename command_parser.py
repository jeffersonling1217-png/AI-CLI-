import re

def clean_command(text: str) -> str:
    """从 AI 回复中提取代码块或清理 Markdown 标记"""
    # 移除 <think>...</think> 标签及其内容（DeepSeek R1 推理过程）
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    # 尝试提取 ```bash ... ``` 中的内容
    code_block_pattern = r"```(?:bash|sh|zsh|powershell|cmd)?\s*(.*?)\s*```"
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 如果没有代码块，直接清理可能存在的行内代码标记
    return text.strip().strip('`')
