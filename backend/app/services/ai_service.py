"""AI Service for image recognition, OCR, and grading"""

import base64
from typing import Optional
import logging
from openai import OpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

client = OpenAI(api_key=settings.openai_api_key)


class AIService:
    """AI Service for handling image processing and grading"""
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.standard_b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    @staticmethod
    def extract_answer_from_image(image_url: str, image_base64: Optional[str] = None) -> str:
        """
        Extract answer text from homework image using GPT-4V
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image (alternative to URL)
            
        Returns:
            Extracted answer text
        """
        try:
            if image_base64:
                message = client.messages.create(
                    model=settings.openai_model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image_base64,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "请识别这张图片中的数学答案。只返回答案内容，不要返回其他信息。"
                                }
                            ],
                        }
                    ],
                )
            else:
                message = client.messages.create(
                    model=settings.openai_model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "url",
                                        "url": image_url,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "请识别这张图片中的数学答案。只返回答案内容，不要返回其他信息。"
                                }
                            ],
                        }
                    ],
                )
            
            extracted_text = message.content[0].text
            logger.info(f"Successfully extracted answer from image")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting answer from image: {e}")
            raise
    
    @staticmethod
    def grade_answer(
        student_answer: str,
        standard_answer: str,
        explanation: str,
        knowledge_point: Optional[str] = None
    ) -> dict:
        """
        Grade student answer against standard answer using GPT-4
        
        Args:
            student_answer: Student's answer text
            standard_answer: Standard/correct answer
            explanation: Standard explanation
            knowledge_point: Knowledge point for context
            
        Returns:
            Dictionary with grading results
        """
        try:
            prompt = f"""
你是一位数学教师。请评批学生的答案。

知识点：{knowledge_point or '数学'}

标准答案：{standard_answer}

标准解析：{explanation}

学生答案：{student_answer}

请根据以下格式返回评批结果（用JSON格式）：
{{
    "is_correct": true/false,  # 是否正确
    "score": 0.0-1.0,  # 得分（0-1之间的浮点数）
    "feedback": "评批意见",  # 简短评价
    "ai_explanation": "详细解析",  # 为学生生成的详细解析
    "error_analysis": "错误分析",  # 如果错误，分析错误原因
    "suggestions": "改进建议"  # 学习建议
}}

注意：
1. 对于答案形式不同但数学上正确的答案，应该判定为正确
2. 如果学生答案部分正确，给予相应的部分分数
3. 生成的解析应该清晰易懂，适合学生理解
            """
            
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
            )
            
            # Parse response
            import json
            response_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If response is not pure JSON, try to extract it
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    result = json.loads(response_text[start_idx:end_idx+1])
                else:
                    raise ValueError("Could not parse AI response")
            
            logger.info(f"Successfully graded answer")
            return result
            
        except Exception as e:
            logger.error(f"Error grading answer: {e}")
            # Return a default response on error
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "评批失败，请重试",
                "ai_explanation": "系统出错，请稍后重试",
                "error_analysis": str(e),
                "suggestions": "请联系技术支持"
            }


ai_service = AIService()
