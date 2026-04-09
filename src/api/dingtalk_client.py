"""
钉钉 API 统一客户端
封装 Token 获取、AI 表格 CRUD、消息推送等核心能力
"""
import os
import time
import hashlib
import hmac
import base64
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()


class DingTalkClient:
    """钉钉 API 统一封装"""

    BASE_URL = "https://oapi.dingtalk.com"
    API_URL = "https://api.dingtalk.com"

    def __init__(self):
        self.app_key = os.getenv("DINGTALK_APP_KEY")
        self.app_secret = os.getenv("DINGTALK_APP_SECRET")
        self.webhook_url = os.getenv("ROBOT_WEBHOOK_URL")
        self.robot_secret = os.getenv("ROBOT_SECRET")
        self._access_token = None
        self._token_expire_at = 0

    # ─── Token 管理 ───────────────────────────────────────────

    def get_access_token(self) -> str:
        """获取企业内部应用 AccessToken，自动刷新"""
        if self._access_token and time.time() < self._token_expire_at - 60:
            return self._access_token

        resp = requests.post(
            f"{self.BASE_URL}/gettoken",
            json={"appkey": self.app_key, "appsecret": self.app_secret},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") != 0:
            raise RuntimeError(f"获取 Token 失败: {data}")

        self._access_token = data["access_token"]
        self._token_expire_at = time.time() + data.get("expires_in", 7200)
        return self._access_token

    # ─── AI 表格操作 ──────────────────────────────────────────

    def aitable_list_records(self, base_id: str, table_id: str,
                              filter_formula: str = None, page_size: int = 100) -> list:
        """查询 AI 表格记录"""
        token = self.get_access_token()
        url = f"{self.API_URL}/v1.0/apaas/aitable/bases/{base_id}/tables/{table_id}/records"
        params = {"pageSize": page_size}
        if filter_formula:
            params["filterByFormula"] = filter_formula

        resp = requests.get(url, headers={"x-acs-dingtalk-access-token": token},
                            params=params, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        return result.get("data", {}).get("records", [])

    def aitable_create_record(self, base_id: str, table_id: str, fields: dict) -> str:
        """新增 AI 表格记录，返回 recordId"""
        token = self.get_access_token()
        url = f"{self.API_URL}/v1.0/apaas/aitable/bases/{base_id}/tables/{table_id}/records"
        resp = requests.post(
            url,
            headers={"x-acs-dingtalk-access-token": token, "Content-Type": "application/json"},
            json={"records": [{"fields": fields}]},
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        records = result.get("data", {}).get("records", [])
        return records[0]["id"] if records else None

    def aitable_update_record(self, base_id: str, table_id: str,
                               record_id: str, fields: dict) -> bool:
        """更新 AI 表格记录"""
        token = self.get_access_token()
        url = f"{self.API_URL}/v1.0/apaas/aitable/bases/{base_id}/tables/{table_id}/records/{record_id}"
        resp = requests.put(
            url,
            headers={"x-acs-dingtalk-access-token": token, "Content-Type": "application/json"},
            json={"fields": fields},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("success", False)

    # ─── 消息推送 ─────────────────────────────────────────────

    def send_robot_message(self, content: str, msg_type: str = "markdown",
                            title: str = "系统通知") -> bool:
        """通过 Webhook 机器人发送消息（支持 text / markdown）"""
        url = self._build_signed_webhook_url()

        if msg_type == "markdown":
            payload = {"msgtype": "markdown", "markdown": {"title": title, "text": content}}
        else:
            payload = {"msgtype": "text", "text": {"content": content}}

        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if result.get("errcode") != 0:
            print(f"[WARN] 消息发送失败: {result}")
            return False
        return True

    def send_work_notification(self, user_id: str, title: str, content: str) -> bool:
        """发送工作通知消息（点对点，到个人钉钉）"""
        token = self.get_access_token()
        agent_id = os.getenv("DINGTALK_AGENT_ID")
        resp = requests.post(
            f"{self.BASE_URL}/topapi/message/corpconversation/asyncsend_v2",
            params={"access_token": token},
            json={
                "agent_id": agent_id,
                "userid_list": user_id,
                "msg": {"msgtype": "markdown", "markdown": {"title": title, "text": content}},
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("errcode") == 0

    # ─── 内部工具 ─────────────────────────────────────────────

    def _build_signed_webhook_url(self) -> str:
        """为 Webhook URL 附加时间戳签名（安全模式）"""
        if not self.robot_secret:
            return self.webhook_url

        timestamp = str(round(time.time() * 1000))
        sign_str = f"{timestamp}\n{self.robot_secret}".encode("utf-8")
        hmac_code = hmac.new(self.robot_secret.encode("utf-8"), sign_str, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"


# 单例
client = DingTalkClient()
