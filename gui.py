# -*- coding: utf-8 -*-
"""
AI CLI 小工具 - 图形界面
提供对话窗口，记录用户输入与 AI 返回（建议命令、执行结果）。
"""
import os
import sys
import platform
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import check_env, reload_config
from ai_engine import get_ai_command, get_ai_chat, reset_client
from executor import execute_command
from intent_recognizer import recognizer, reset_recognizer
from user_config import load_config, save_config

# 当前待执行的命令（AI 返回后用户可选择执行或取消）
_pending_command = None
_pending_shell_info = None


def show_config_dialog(parent=None) -> bool:
    """显示配置窗口，返回 True 表示保存成功"""
    dlg = tk.Toplevel(parent) if parent else tk.Tk()
    dlg.title("AI 模型配置")
    dlg.geometry("500x220")
    dlg.resizable(True, False)
    dlg.minsize(420, 220)
    if parent:
        dlg.transient(parent)
        dlg.grab_set()

    cfg = load_config()
    ttk.Label(dlg, text="API Key:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    key_var = tk.StringVar(value=cfg.get("OPENAI_API_KEY", ""))
    ttk.Entry(dlg, textvariable=key_var, width=45, show="*").grid(row=0, column=1, padx=10, pady=8, sticky="ew")

    ttk.Label(dlg, text="API Base URL:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
    base_var = tk.StringVar(value=cfg.get("OPENAI_API_BASE", "https://api.openai.com/v1"))
    ttk.Entry(dlg, textvariable=base_var, width=45).grid(row=1, column=1, padx=10, pady=8, sticky="ew")

    ttk.Label(dlg, text="模型名称:").grid(row=2, column=0, padx=10, pady=8, sticky="w")
    model_var = tk.StringVar(value=cfg.get("MODEL", "gpt-4o"))
    ttk.Entry(dlg, textvariable=model_var, width=45).grid(row=2, column=1, padx=10, pady=8, sticky="ew")

    dlg.columnconfigure(1, weight=1)

    ok_result = [False]

    def on_ok():
        if not key_var.get().strip():
            messagebox.showerror("错误", "请填写 API Key", parent=dlg)
            return
        save_config(key_var.get().strip(), base_var.get().strip(), model_var.get().strip())
        reload_config()
        reset_client()
        reset_recognizer()
        ok_result[0] = True
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    btn_frame = ttk.Frame(dlg)
    btn_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="w")
    ttk.Button(btn_frame, text="保存", command=on_ok).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="取消", command=on_cancel).grid(row=0, column=1, padx=5)

    if parent:
        dlg.wait_window()
    else:
        dlg.mainloop()
    return ok_result[0]


def get_shell_info():
    """获取当前操作系统和 Shell 信息"""
    os_name = platform.system()
    try:
        import shellingham
        shell_name, _ = shellingham.detect_shell()
    except Exception:
        shell_name = "unknown"
    return os_name, shell_name


def append_chat(chat: scrolledtext.ScrolledText, text: str, tag: str = None):
    """线程安全：向对话区域追加文本"""
    def _do():
        chat.configure(state=tk.NORMAL)
        if tag:
            chat.insert(tk.END, text, tag)
        else:
            chat.insert(tk.END, text)
        chat.see(tk.END)
        chat.configure(state=tk.DISABLED)
    chat.after(0, _do)


def run_app():
    # 首次运行或无配置时弹出配置窗口（.env 或 user_config 任一有 key 则跳过）
    if not os.getenv("OPENAI_API_KEY"):
        if not show_config_dialog():
            return
    check_env()
    os_info, shell_info = get_shell_info()
    if os_info == "Windows" and not ("powershell" in shell_info.lower() or "pwsh" in shell_info.lower()):
        shell_info = "powershell.exe" # 在 Windows 打包环境下强制使用 PowerShell

    root = tk.Tk()
    root.title("AI CLI 小工具")
    root.geometry("700x520")
    root.minsize(500, 400)

    # 标题栏：设置按钮
    title_frame = ttk.Frame(root, padding=5)
    title_frame.pack(fill=tk.X)
    ttk.Button(title_frame, text="⚙ 设置", command=lambda: show_config_dialog(root)).pack(side=tk.RIGHT)

    # 对话区域（只读，用于展示记录）
    chat_frame = ttk.Frame(root, padding=5)
    chat_frame.pack(fill=tk.BOTH, expand=True)
    chat = scrolledtext.ScrolledText(
        chat_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        state=tk.DISABLED,
        height=20,
    )
    chat.pack(fill=tk.BOTH, expand=True)
    chat.tag_configure("user", foreground="#0066cc")
    chat.tag_configure("ai", foreground="#228b22")
    chat.tag_configure("cmd", foreground="#b8860b")
    chat.tag_configure("out", foreground="#333333")
    chat.tag_configure("err", foreground="#cc0000")

    # 欢迎信息
    append_chat(chat, f"环境: {os_info} | Shell: {shell_info}\n当前目录: {os.getcwd()}\n", "ai")
    append_chat(chat, "在下方输入你想做的事，按发送即可。\n\n")

    # 待执行命令时的操作按钮区域
    pending_frame = ttk.Frame(root)
    pending_frame.pack(fill=tk.X, padx=5, pady=2)

    btn_exec = ttk.Button(pending_frame, text="执行命令")
    btn_cancel = ttk.Button(pending_frame, text="取消")
    btn_exec.pack(side=tk.LEFT, padx=2)
    btn_cancel.pack(side=tk.LEFT, padx=2)
    # 默认先隐藏，等 AI 返回后再显示
    pending_frame.pack_forget()

    def show_pending_buttons(show: bool):
        if show:
            pending_frame.pack(fill=tk.X, padx=5, pady=2)
        else:
            pending_frame.pack_forget()

    def on_execute():
        global _pending_command, _pending_shell_info
        if not _pending_command:
            return
        cmd, sh = _pending_command, _pending_shell_info
        _pending_command, _pending_shell_info = None, None
        show_pending_buttons(False)
        append_chat(chat, "\n--- 执行输出 ---\n", "cmd")

        def output_callback(text: str):
            append_chat(chat, text, "out")

        def run():
            try:
                execute_command(cmd, sh, output_callback=output_callback)
            except Exception as e:
                append_chat(chat, f"\n[异常] {e}\n", "err")
            root.after(0, lambda: append_chat(chat, "\n--- 结束 ---\n\n", "cmd"))

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def on_cancel():
        global _pending_command, _pending_shell_info
        _pending_command, _pending_shell_info = None, None
        show_pending_buttons(False)
        append_chat(chat, "已取消\n\n", "ai")

    btn_exec.configure(command=on_execute)
    btn_cancel.configure(command=on_cancel)

    # 输入区域
    input_frame = ttk.Frame(root, padding=5)
    input_frame.pack(fill=tk.X)
    input_var = tk.StringVar()
    entry = ttk.Entry(input_frame, textvariable=input_var, font=("Consolas", 11))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    entry.focus_set()

    def send():
        global _pending_command, _pending_shell_info
        raw = input_var.get().strip()
        if not raw:
            return
        if raw.lower() in ("exit", "quit", "退出"):
            root.quit()
            return
        input_var.set("")
        append_chat(chat, f"用户: {raw}\n", "user")
        # 用标记记录“正在思考”起始位置，便于之后替换为真实回复
        chat.configure(state=tk.NORMAL)
        chat.mark_set("think_start", tk.END)
        chat.insert(tk.END, "AI 正在思考...\n", "ai")
        chat.configure(state=tk.DISABLED)

        def work():
            try:
                # 1. 意图识别
                intent = recognizer.recognize(raw)
                
                # 2. 根据意图分发
                if intent == "COMMAND":
                    command, explanation = get_ai_command(raw, os_info, shell_info)
                    chat_response = None
                else:
                    command = None
                    chat_response = get_ai_chat(raw)
                    
            except Exception as e:
                root.after(0, lambda: append_chat(chat, f"AI 调用失败: {e}\n\n", "err"))
                return

            def update_ui():
                # 删掉 "AI 正在思考..." 并写入真实回复
                chat.configure(state=tk.NORMAL)
                try:
                    chat.delete("think_start", tk.END)
                except tk.TclError:
                    pass
                
                if command:
                    # COMMAND 模式：显示解释 + 命令 + 按钮
                    chat.insert(tk.END, f"AI (指令): {explanation}\n", "ai")
                    append_chat(chat, f"建议命令:\n{command}\n", "cmd")
                    global _pending_command, _pending_shell_info
                    _pending_command, _pending_shell_info = command, shell_info
                    show_pending_buttons(True)
                else:
                    # CHAT 模式：只显示回复，不显示按钮
                    chat.insert(tk.END, f"AI: {chat_response}\n", "ai")
                    show_pending_buttons(False)
                
                append_chat(chat, "\n")
                chat.configure(state=tk.DISABLED)
            root.after(0, update_ui)

        t = threading.Thread(target=work, daemon=True)
        t.start()

    btn_send = ttk.Button(input_frame, text="发送", command=send)
    btn_send.pack(side=tk.RIGHT)
    entry.bind("<Return>", lambda e: send())

    root.mainloop()


if __name__ == "__main__":
    run_app()
