import json
import logging
from typing import Literal, Generator, Optional, Union
import requests


class Chatbot:
    """Kimi 聊天基类"""
    api_base = "https://kimi.moonshot.cn/api"

    def __init__(
            self,
            cookies: dict = None,
            cookies_str: str = "",
    ):

        if cookies and cookies_str:
            raise ValueError("cookies和cookies_str不能同时存在")

        if cookies:
            self.cookies = cookies
            self.cookies_str = ""
            for key in cookies:
                self.cookies_str += "{}={}; ".format(key, cookies[key])
        elif cookies_str:
            self.cookies_str = cookies_str

            spt = self.cookies_str.split(";")

            self.cookies = {}

            for it in spt:
                it = it.strip()
                if it:
                    equ_loc = it.find("=")
                    key = it[:equ_loc]
                    value = it[equ_loc + 1:]
                    self.cookies[key] = value

        logging.debug(self.cookies)

        cookie_str_access=self.cookies["access_token"]

        self.headers={
            "user-agent":
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            "Content-Type": "application/json",
            "Referer": "https://kimi.moonshot.cn",
            "Origin": "https://kimi.moonshot.cn",
            "Authorization": f"Bearer {cookie_str_access}"
        }

    def __refresh_token(self):
        """刷新token"""
        resp = requests.get(
            url=self.api_base + "/auth/token/refresh",
            headers=self.cookies['refresh_token']
        ).json()
        self.cookies["access_token"] = resp["access_token"]
        self.cookies["refresh_token"] = resp["refresh_token"]

    def __request(
            self,
            method: str,
            url: str,
            stream: bool = False,
            **kwargs
    ) -> requests.Response:
        resp = requests.request(
            method=method,
            url=url,
            stream=stream,
            headers=self.headers,
            **kwargs
        )
        stat_code = resp.status_code
        if stat_code == 200:
            return resp
        resp_json = resp.json()
        if resp_json.get("error_type") == "auth.token.invalid":
            # token过期
            self.__refresh_token()
            return requests.request(
                method=method,
                url=url,
                stream=stream,
                headers=self.cookies["access_token"],
                **kwargs
            )
        else:
            raise BaseException(str(resp_json))

    def create_conversation(self, name: str = "未命名会话") -> dict:
        """创建会话"""
        resp = self.__request(
            method="POST",
            url=self.api_base + "/chat",
            json={
                "name": f"{name}",
                "is_example": False,
                "born_from": ""
            }
        ).json()
        return resp

    def delete_conversation(self, conversation_id: str) -> None:
        """删除会话"""
        self.__request(
            method="DELETE",
            url=self.api_base + f"/chat/{conversation_id}"
        )

    def get_conversations(self, size: int = 30) -> dict:
        """获取会话列表
        :param size: 最多获取条数（默认30）
        """
        resp = self.__request(
            method="POST",
            url=self.api_base + "/chat/list",
            json={
                "kimiplus_id": "",
                "offset": 0,
                "size": size
            }
        ).json()
        return resp

    def get_history(self, conversation_id: str, last: int = 50) -> dict:
        """获取会话历史
        :param conversation_id: 会话ID
        :param last: 历史条数（默认50）
        """
        resp = self.__request(
            method="POST",
            url=self.api_base + f"/chat/{conversation_id}/segment/scroll",
            json={
                "last": last
            }
        ).json()
        return resp

    def __stream_ask(
            self,
            prompt: str,
            conversation_id: Optional[str],
            timeout: int = 10,
            use_search: bool = False
    ) -> Generator[dict, None, None]:
        """流式提问

        :param prompt: 提问内容
        :param conversation_id: 会话id（若不填则会新建）
        :param timeout: 超时时间（默认10秒）
        :param use_search: 是否使用搜索

        """
        if not conversation_id:
            conversation_id = self.create_conversation()["id"]
        resp = self.__request(
            method="POST",
            url=self.api_base + f"/chat/{conversation_id}/completion/stream",
            timeout=timeout,
            stream=True,
            json={
                "kimiplus_id": "kimi",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "refs": [],
                "use_search": use_search
            }
        )
        reply_text = ""
        for chunk in resp.iter_lines():
            try:
                if chunk:
                    # 非空chunk
                    chunk = chunk.decode("utf-8")
                    if not chunk.endswith("}"):
                        # 不完整
                        continue
                    chunk_json = json.loads(chunk[6:])
                    if chunk_json.get("event") == "cmpl":
                        reply_text += chunk_json.get("text")
                        result = {
                            "conversation_id": conversation_id,
                            "text": reply_text
                        }
                        yield result
            except Exception as e:
                pass

    def ask(
            self,
            prompt: str,
            conversation_id: Optional[str],
            timeout: int = 10,
            use_search: bool = False,
            stream: bool = False
    ) -> Union[dict, Generator[dict, None, None]]:
        """流式提问

        :param prompt: 提问内容
        :param conversation_id: 会话id（若不填则会新建）
        :param timeout: 超时时间（默认10秒）
        :param use_search: 是否使用搜索
        :param stream: 是否为流式

        """
        resp_generator = self.__stream_ask(
                            prompt,
                            conversation_id,
                            timeout,
                            use_search
                        )
        if stream:
            return resp_generator
        else:
            result = None
            for chunk in resp_generator:
                result = chunk
            return result