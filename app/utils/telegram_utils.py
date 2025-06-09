import requests
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'telegram_config.txt')

def get_telegram_config():
    if not os.path.exists(CONFIG_PATH):
        return '', 'سفارش شما آماده تحویل است.'
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        if len(lines) >= 2:
            return lines[0], '\n'.join(lines[1:])
        elif len(lines) == 1:
            return lines[0], 'سفارش شما آماده تحویل است.'
        return '', 'سفارش شما آماده تحویل است.'

def send_telegram_message(chat_id, lens_count=None, order_info=None):
    token, default_message = get_telegram_config()
    if not token:
        print('توکن ربات تلگرام وارد نشده است.')
        return None
    
    message = default_message
    # lens_count حالا باید مجموع quantity باشد
    if order_info and 'lenses' in order_info:
        total_quantity = sum([int(lens.get('quantity', 0)) for lens in order_info['lenses']])
        message = message.replace('{total_lens_count}', str(total_quantity))
    elif lens_count is not None:
        message = message.replace('{total_lens_count}', str(lens_count))
    if lens_count is not None:
        message = message.replace('{lens_count}', str(lens_count))
    # جایگزینی اطلاعات سفارش
    if order_info:
        for key, value in order_info.items():
            if key == 'lenses':
                continue
            tag = '{' + key + '}'
            message = message.replace(tag, str(value))
    
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print('خطا در ارسال پیام تلگرام:', e)
        return None 