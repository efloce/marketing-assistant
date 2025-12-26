import requests
import json

# Сначала проверяем доступность сервера
test_url = "http://localhost:11434/api/tags"

try:
    print("Проверяем доступность Ollama...")
    response = requests.get(test_url, timeout=10)

    if response.status_code == 200:
        print("✅ Ollama доступен!")
        print(f"Доступные модели: {response.text}")

        # Теперь тестируем генерацию
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "tinyllama",
            "prompt": "Привет! Как дела? Ответь коротко.",
            "stream": False
        }

        response = requests.post(url, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Генерация успешна! Ответ: {result['response']}")
        else:
            print(f"❌ Ошибка генерации: {response.status_code}")
            print(f"Тело ответа: {response.text}")

    else:
        print(f"❌ Ollama не отвечает: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ Не могу подключиться к Ollama. Убедитесь что:")
    print("1. Ollama установлена и запущена")
    print("2. Сервер работает: 'ollama serve'")
    print("3. Порт 11434 не заблокирован брандмауэром")

except Exception as e:
    print(f"❌ Неожиданная ошибка: {str(e)}")