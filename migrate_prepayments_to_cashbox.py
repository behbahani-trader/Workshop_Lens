#!/usr/bin/env python3
"""
اسکریپت انتقال پیش‌پرداخت‌های موجود به صندوق اصلی
"""

import sqlite3
from datetime import datetime

def migrate_prepayments_to_cashbox():
    """انتقال پیش‌پرداخت‌های موجود به صندوق اصلی"""
    
    try:
        # اتصال به دیتابیس
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        print("🔄 شروع انتقال پیش‌پرداخت‌ها به صندوق اصلی...")
        
        # اطمینان از وجود صندوق اصلی
        cursor.execute("SELECT id, balance FROM cashboxes WHERE name = 'اصلی'")
        cashbox_main = cursor.fetchone()
        
        if not cashbox_main:
            cursor.execute("INSERT INTO cashboxes (name, balance) VALUES ('اصلی', 0.0)")
            cursor.execute("SELECT id, balance FROM cashboxes WHERE name = 'اصلی'")
            cashbox_main = cursor.fetchone()
            print("✅ صندوق اصلی ایجاد شد")
        
        cashbox_main_id, current_balance = cashbox_main
        print(f"📦 صندوق اصلی: موجودی فعلی = {current_balance:,.0f} تومان")
        
        # دریافت تمام سفارشاتی که پیش‌پرداخت دارند
        cursor.execute("""
            SELECT id, order_number, payment, customer_id, created_at
            FROM orders 
            WHERE payment > 0
        """)
        
        orders = cursor.fetchall()
        
        if not orders:
            print("✅ هیچ سفارشی با پیش‌پرداخت وجود ندارد")
            return True
        
        print(f"📋 {len(orders)} سفارش با پیش‌پرداخت یافت شد")
        
        # بررسی اینکه آیا تراکنش‌های پیش‌پرداخت قبلاً ثبت شده‌اند
        cursor.execute("""
            SELECT COUNT(*) FROM cashbox_transactions 
            WHERE reference_type = 'prepayment'
        """)
        existing_prepayment_transactions = cursor.fetchone()[0]
        
        if existing_prepayment_transactions > 0:
            print(f"⚠️ {existing_prepayment_transactions} تراکنش پیش‌پرداخت قبلاً ثبت شده")
            response = input("آیا می‌خواهید دوباره انتقال انجام دهید؟ (y/N): ")
            if response.lower() != 'y':
                print("❌ انتقال لغو شد")
                return False
        
        total_prepayments = 0
        
        # انتقال پیش‌پرداخت‌ها
        for order_id, order_number, payment, customer_id, created_at in orders:
            # دریافت نام مشتری
            cursor.execute("SELECT first_name, last_name FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            customer_name = f"{customer[0]} {customer[1]}" if customer else "نامشخص"
            
            print(f"  🔄 انتقال پیش‌پرداخت سفارش {order_number}: {payment:,.0f} تومان - {customer_name}")
            
            # ثبت تراکنش پیش‌پرداخت در صندوق اصلی
            cursor.execute("""
                INSERT INTO cashbox_transactions 
                (cashbox_id, amount, transaction_type, description, reference_type, reference_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cashbox_main_id,
                payment,
                'income',
                f'پیش‌پرداخت سفارش {order_number} - {customer_name}',
                'prepayment',
                order_id,
                created_at or datetime.now()
            ))
            
            total_prepayments += payment
        
        # بروزرسانی موجودی صندوق اصلی
        new_balance = current_balance + total_prepayments
        cursor.execute("UPDATE cashboxes SET balance = ? WHERE id = ?", (new_balance, cashbox_main_id))
        
        # ذخیره تغییرات
        conn.commit()
        
        print(f"✅ انتقال {len(orders)} پیش‌پرداخت با موفقیت انجام شد")
        print(f"💰 کل پیش‌پرداخت‌ها: {total_prepayments:,.0f} تومان")
        print(f"📦 موجودی جدید صندوق اصلی: {new_balance:,.0f} تومان")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در انتقال پیش‌پرداخت‌ها: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 شروع انتقال پیش‌پرداخت‌ها به صندوق اصلی")
    print("=" * 60)
    
    success = migrate_prepayments_to_cashbox()
    
    print("=" * 60)
    if success:
        print("🎉 انتقال پیش‌پرداخت‌ها با موفقیت انجام شد!")
    else:
        print("❌ انتقال پیش‌پرداخت‌ها با خطا مواجه شد!")
