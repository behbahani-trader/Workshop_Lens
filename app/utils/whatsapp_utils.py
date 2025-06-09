import requests
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'whatsapp_config.txt')

def get_ultramsg_config():
    if not os.path.exists(CONFIG_PATH):
        return '', ''
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        if len(lines) >= 2:
            return lines[0], lines[1]
        return '', ''

def send_whatsapp_message(phone, message):
    """
    ارسال پیام واتساپ با UltraMsg
    phone: شماره موبایل به فرمت 98**********
    message: متن پیام
    """
    instance_id, token = get_ultramsg_config()
    if not instance_id or not token:
        print('تنظیمات UltraMsg وارد نشده است.')
        return None
    url = f'https://api.ultramsg.com/instance{instance_id}/messages/chat'
    payload = {
        'token': token,
        'to': phone,
        'body': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print('خطا در ارسال پیام واتساپ:', e)
        return None 