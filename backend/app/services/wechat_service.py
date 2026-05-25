"""WeChat Service for authentication and messaging"""

import logging
import requests
import json
from typing import Optional, Dict, Any
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WeChatService:
    """WeChat API integration service"""
    
    JSCODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"
    SEND_MESSAGE_URL = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"
    
    @staticmethod
    def code_to_session(code: str) -> Dict[str, Any]:
        """
        Exchange WeChat auth code for session info
        
        Args:
            code: WeChat authorization code from mini program
            
        Returns:
            Session info containing openid and session_key
        """
        try:
            params = {
                "appid": settings.wechat_appid,
                "secret": settings.wechat_secret,
                "js_code": code,
                "grant_type": "authorization_code"
            }
            
            response = requests.get(WeChatService.JSCODE2SESSION_URL, params=params)
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"WeChat error: {data.get('errmsg')}")
                raise Exception(f"WeChat error: {data.get('errmsg')}")
            
            logger.info(f"Successfully exchanged code for session")
            return data
            
        except Exception as e:
            logger.error(f"Error exchanging code to session: {e}")
            raise
    
    @staticmethod
    def send_template_message(
        openid: str,
        template_id: str,
        data: Dict[str, Any],
        page: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> bool:
        """
        Send WeChat template message
        
        Args:
            openid: User's WeChat openid
            template_id: Template message ID
            data: Message data
            page: Mini program page to navigate to
            access_token: WeChat access token
            
        Returns:
            True if message sent successfully
        """
        try:
            if not access_token:
                access_token = WeChatService.get_access_token()
            
            payload = {
                "touser": openid,
                "template_id": template_id,
                "data": data
            }
            
            if page:
                payload["page"] = page
            
            url = f"{WeChatService.SEND_MESSAGE_URL}?access_token={access_token}"
            response = requests.post(url, json=payload)
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"Successfully sent template message to {openid}")
                return True
            else:
                logger.error(f"Failed to send message: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return False
    
    @staticmethod
    def get_access_token() -> str:
        """
        Get WeChat access token
        Note: In production, this should be cached and refreshed
        """
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": settings.wechat_appid,
                "secret": settings.wechat_secret
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "access_token" in data:
                return data["access_token"]
            else:
                raise Exception(f"Failed to get access token: {data}")
                
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise


wechat_service = WeChatService()
