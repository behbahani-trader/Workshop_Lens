from app import create_app, db
from app.models.order import Order
from app.utils.date_utils import to_jalali, format_jalali
from datetime import datetime

def update_dates():
    app = create_app()
    with app.app_context():
        orders = Order.query.all()
        print(f'Found {len(orders)} orders to update')
        
        for order in orders:
            print(f'\nOrder {order.id}:')
            print(f'  Created at: {order.created_at} -> {format_jalali(order.created_at)}')
            print(f'  Delivery date: {order.delivery_date} -> {format_jalali(order.delivery_date)}')
            
            # تاریخ‌ها در پایگاه داده به همان صورت میلادی باقی می‌مانند
            # فقط در نمایش به شمسی تبدیل می‌شوند
            print('  No database changes needed - dates are stored in Gregorian format')
            print('---')

if __name__ == '__main__':
    update_dates() 