import math
from typing import List
import config
from openai import OpenAI

# 预设的意图种子语句
SEEDS_COMMAND = [
    "帮我创建一个文件",
    "删除这个目录",
    "列出当前所有文件",
    "运行 git status",
    "把代码推送到远程",
    "修改 config.py",
    "重启电脑",
    "打开 Excel",
    "ping google.com",
    "写一个 python 脚本",
    "执行这个命令"
]

SEEDS_CHAT = [
    "你好",
    "你是谁",
    "今天天气怎么样",
    "解释一下什么是 Python",
    "讲个笑话",
    "谢谢你",
    "不仅如此",
    "我觉得这个工具很好用",
    "随便聊聊",
    "你觉得怎么样",
    "这个报错是什么意思"
]

class IntentRecognizer:
    def __init__(self):
        self._init_client()

    def _init_client(self):
        self.client = OpenAI(api_key=config.API_KEY, base_url=config.API_BASE)
        self.command_vectors = []
        self.chat_vectors = []
        self._initialized = False

    def reset(self):
        """配置变更后重置"""
        self._init_client()

    def _get_embedding(self, text: str) -> List[float]:
        """调用 API 获取文本的向量表示"""
        # 注意：需要模型支持 embedding 接口。如果 DeepSeek 不支持，会抛出异常触发 fallback
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small" 
        )
        return response.data[0].embedding

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def _initialize_vectors(self):
        """初始化种子向量（懒加载）"""
        if self._initialized:
            return
        try:
            # 尝试批量获取种子向量
            # 这里假设 API 支持 batch embedding，且 model 参数有效
            # 如果 API_BASE 是 deepseek，且它没有 embedding 接口，这里会报错
            resp_cmd = self.client.embeddings.create(input=SEEDS_COMMAND, model="text-embedding-3-small")
            self.command_vectors = [d.embedding for d in resp_cmd.data]
            
            resp_chat = self.client.embeddings.create(input=SEEDS_CHAT, model="text-embedding-3-small")
            self.chat_vectors = [d.embedding for d in resp_chat.data]
            
            self._initialized = True
        except Exception as e:
            # print(f"Vector initialization failed (API might not support embeddings): {e}")
            raise e

    def recognize(self, text: str) -> str:
        """
        识别文本意图
        返回: 'COMMAND' 或 'CHAT'
        """
        try:
            # 尝试初始化向量（如果失败会抛出异常，转入 except）
            self._initialize_vectors()
            
            user_vec = self._get_embedding(text)
            
            # 计算最大相似度
            max_cmd_score = max([self._cosine_similarity(user_vec, v) for v in self.command_vectors])
            max_chat_score = max([self._cosine_similarity(user_vec, v) for v in self.chat_vectors])
            
            # print(f"DEBUG: Cmd Score: {max_cmd_score:.4f}, Chat Score: {max_chat_score:.4f}")
            
            # 简单的逻辑判断：取分数高者
            # 可以加一个阈值，比如都低于 0.3 则认为是 CHAT
            if max_cmd_score > max_chat_score:
                return "COMMAND"
            else:
                return "CHAT"
                
        except Exception as e:
            # 发生任何错误（如 API 不支持 Embedding），回退到 LLM 语义判断
            # print(f"Embedding recognition failed, fallback to LLM: {e}")
            return self._recognize_via_llm(text)

    def _recognize_via_llm(self, text: str) -> str:
        """
        兜底方案：使用 LLM 进行意图分类
        """
        prompt = f"""
请判断以下用户输入的意图。
输入: "{text}"
类别: [CHAT, COMMAND]
CHAT: 闲聊、询问概念、请求解释、打招呼。
COMMAND: 要求执行具体操作、创建/修改/删除文件、运行命令、系统设置。

只返回类别名称，不要其他内容。
"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat", # 使用轻量模型分类（假设已配置的模型支持）
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10
            )
            intent = response.choices[0].message.content.strip().upper()
            if "COMMAND" in intent:
                return "COMMAND"
            return "CHAT"
        except:
            return "CHAT"

recognizer = IntentRecognizer()


def reset_recognizer():
    recognizer.reset()
