#!/usr/bin/env python3
"""
اسکریپت انتقال پیش‌پرداخت‌ها به سیستم تسویه جدید
"""

import sqlite3
from datetime import datetime

def migrate_prepayments():
    """انتقال پیش‌پرداخت‌های موجود به فیلد paid_amount"""
    
    try:
        # اتصال به دیتابیس
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        print("🔄 شروع انتقال پیش‌پرداخت‌ها...")
        
        # دریافت تمام سفارشاتی که پیش‌پرداخت دارند اما paid_amount آن‌ها صفر است
        cursor.execute("""
            SELECT id, order_number, payment, paid_amount 
            FROM orders 
            WHERE payment > 0 AND (paid_amount IS NULL OR paid_amount = 0)
        """)
        
        orders = cursor.fetchall()
        
        if not orders:
            print("✅ هیچ سفارشی برای انتقال پیش‌پرداخت وجود ندارد")
            return True
        
        print(f"📋 {len(orders)} سفارش برای انتقال پیش‌پرداخت یافت شد")
        
        # انتقال پیش‌پرداخت‌ها
        for order_id, order_number, payment, paid_amount in orders:
            print(f"  🔄 انتقال پیش‌پرداخت سفارش {order_number}: {payment:,.0f} تومان")
            
            # بروزرسانی paid_amount با مقدار payment
            cursor.execute("""
                UPDATE orders 
                SET paid_amount = ?, 
                    settlement_notes = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                payment,
                f"{datetime.now().strftime('%Y/%m/%d %H:%M')}: انتقال پیش‌پرداخت به سیستم تسویه جدید",
                datetime.now(),
                order_id
            ))
            
            # بررسی تسویه کامل
            cursor.execute("SELECT total_amount FROM orders WHERE id = ?", (order_id,))
            total_amount = cursor.fetchone()[0]
            
            if payment >= total_amount:
                cursor.execute("""
                    UPDATE orders 
                    SET is_settled = 1, settlement_date = ?
                    WHERE id = ?
                """, (datetime.now(), order_id))
                print(f"    ✅ سفارش {order_number} به طور کامل تسویه شد")
        
        # ذخیره تغییرات
        conn.commit()
        print(f"✅ انتقال {len(orders)} پیش‌پرداخت با موفقیت انجام شد")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در انتقال پیش‌پرداخت‌ها: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 شروع انتقال پیش‌پرداخت‌ها به سیستم تسویه جدید")
    print("=" * 60)
    
    success = migrate_prepayments()
    
    print("=" * 60)
    if success:
        print("🎉 انتقال پیش‌پرداخت‌ها با موفقیت انجام شد!")
    else:
        print("❌ انتقال پیش‌پرداخت‌ها با خطا مواجه شد!")
