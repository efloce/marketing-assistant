import os
import requests
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain


# Загружаем переменные окружения
load_dotenv()


class MarketingTextGenerator:
    def __init__(self):
        print("Инициализация генератора с Ollama...")

        # История диалога
        self.history = []
        print("✓ Генератор готов к работе!")

    def generate_text(self, product, audience, platform, tone):
        """Генерация рекламного текста через прямой API-вызов"""
        try:
            if not product or not audience:
                return "❌ Ошибка: Пожалуйста, укажите продукт и целевую аудиторию."

            print(f"Генерация текста для: {product}, {audience}, {platform}, {tone}")

            # Подготовка промпта
            prompt = f"""
            Ты опытный маркетолог. Сгенерируй рекламный текст на основе параметров:

            Продукт: {product}
            Целевая аудитория: {audience}
            Платформа: {platform}
            Тон сообщения: {tone}

            Сгенерируй:
            1. Заголовок (1-2 строки)
            2. Основной текст (3-4 предложения)
            3. Призыв к действию

            Текст должен быть креативным и соответствовать платформе {platform}.

            Ответ на русском языке:
            """

            # Вызов Ollama API
            url = "http://localhost:11434/api/generate"
            data = {
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }

            response = requests.post(url, json=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '')

                # Сохраняем в историю
                self.history.append({
                    "type": "user",
                    "content": f"Запрос на генерацию текста: {product}, {audience}, {platform}, {tone}"
                })
                self.history.append({
                    "type": "ai",
                    "content": text
                })

                return text
            else:
                error_msg = f"❌ Ошибка API: {response.status_code} - {response.text}"
                self.history.append({
                    "type": "error",
                    "content": error_msg
                })
                return error_msg

        except requests.exceptions.ConnectionError:
            error_msg = "❌ Не удается подключиться к Ollama. Убедитесь, что Ollama запущен: 'ollama serve'"
            self.history.append({
                "type": "error",
                "content": error_msg
            })
            return error_msg
        except Exception as e:
            error_msg = f"❌ Ошибка при генерации: {str(e)}"
            self.history.append({
                "type": "error",
                "content": error_msg
            })
            return error_msg

    def generate_idea(self, product, audience):
        """Генерация маркетинговой идеи"""
        try:
            if not product or not audience:
                return "❌ Ошибка: Пожалуйста, укажите продукт и целевую аудиторию."

            idea_prompt = PromptTemplate(
                input_variables=["product", "audience"],
                template="""
                Придумай 3 креативные маркетинговые идеи для продукта '{product}' для аудитории '{audience}'. 
                Представь в виде нумерованного списка.

                Ответ на русском языке:
                """
            )

            idea_chain = LLMChain(
                llm=self.llm,
                prompt=idea_prompt
            )

            result = idea_chain.run({"product": product, "audience": audience})
            return result
        except Exception as e:
            return f"❌ Ошибка при генерации идей: {str(e)}"

    def clear_memory(self):
        """Очистка памяти диалога"""
        self.history = []
        return "✅ История диалога очищена!"

    @property
    def memory(self):
        """Свойство для совместимости с Streamlit интерфейсом"""

        class MemoryWrapper:
            def __init__(self, history):
                self.history = history

            def load_memory_variables(self, inputs):
                return {"chat_history": self.history}

        return MemoryWrapper(self.history)