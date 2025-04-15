import requests
import json

API_USER = '686204544' 
API_SECRET = 'GhywajuQhiv7JuC4SPU55sjkQpGbKS2Q' 

# Счётчик изображений (глобальный)
image_counter = {}

def is_image_clean(image_file, username):
    # Увеличиваем счётчик пользователя
    count = image_counter.get(username, 0) + 1
    image_counter[username] = count

    print(f"\n👤 Пользователь: {username}")
    print(f"📸 Проверка {count}-го изображения...")

    params = {
        'models': 'nudity-2.1,weapon,alcohol,recreational_drug,medical,offensive-2.0,scam,text-content,gore-2.0,qr-content,tobacco',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    files = {
        'media': image_file
    }

    try:
        response = requests.post(
            'https://api.sightengine.com/1.0/check.json',
            files=files,
            data=params
        )
        result = response.json()

        print("\n🔍 Анализ изображения:")
        for category, value in result.items():
            if isinstance(value, dict):
                print(f"\n🔹 {category.upper()}:")
                for subcat, prob in value.items():
                    if isinstance(prob, (int, float)):
                        print(f"  - {subcat}: {round(prob * 100, 2)}%")
                    elif isinstance(prob, dict):
                        for subsub, p in prob.items():
                            if isinstance(p, (int, float)):
                                print(f"    * {subcat} → {subsub}: {round(p * 100, 2)}%")

        # Вычисляем риски
        def get_score(value):
            if isinstance(value, dict):
                return value.get("prob", value.get("confidence", 0))
            return value

        nudity_score = get_score(result.get("nudity", {}).get("sexual_activity", 0))
        weapon_score = get_score(result.get("weapon", {}).get("classes", {}).get("firearm", 0))
        alcohol_score = get_score(result.get("alcohol", {}).get("prob", 0))
        drug_score = get_score(result.get("recreational_drug", {}).get("prob", 0))

        if any(score > 0.5 for score in [nudity_score, weapon_score, alcohol_score, drug_score]):
            print("\n🚫 Обнаружен нежелательный контент!")
            return False

        print("\n✅ Изображение чистое.")
        return True

    except Exception as e:
        print("❗ Ошибка при проверке изображения:", e)
        return True  # Безопасный fallback