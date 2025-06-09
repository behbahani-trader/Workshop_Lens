#!/usr/bin/env python3
"""
اسکریپت بروزرسانی دیتابیس
این اسکریپت جدول‌ها و ستون‌های جدید را به دیتابیس اضافه می‌کند
"""

import sqlite3
import os

def update_database():
    """بروزرسانی دیتابیس با جدول‌ها و ستون‌های جدید"""
    
    # اتصال به دیتابیس
    db_path = 'app.db'
    if not os.path.exists(db_path):
        print(f"فایل دیتابیس {db_path} یافت نشد!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("شروع بروزرسانی دیتابیس...")
        
        # 1. اضافه کردن ستون is_vip به جدول customers
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN is_vip BOOLEAN DEFAULT 0 NOT NULL;")
            print("✅ ستون is_vip به جدول customers اضافه شد")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️ ستون is_vip قبلاً وجود دارد")
            else:
                print(f"❌ خطا در اضافه کردن ستون is_vip: {e}")
        
        # 2. ایجاد جدول cashboxes
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cashboxes (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    balance FLOAT NOT NULL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ جدول cashboxes ایجاد شد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جدول cashboxes: {e}")
        
        # 3. ایجاد جدول cashbox_transactions
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cashbox_transactions (
                    id INTEGER PRIMARY KEY,
                    cashbox_id INTEGER NOT NULL,
                    amount FLOAT NOT NULL,
                    transaction_type VARCHAR(20) NOT NULL,
                    description TEXT,
                    reference_type VARCHAR(50),
                    reference_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cashbox_id) REFERENCES cashboxes (id)
                );
            """)
            print("✅ جدول cashbox_transactions ایجاد شد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جدول cashbox_transactions: {e}")
        
        # 4. ایجاد جدول expenses
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    amount FLOAT NOT NULL,
                    description TEXT,
                    expense_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ جدول expenses ایجاد شد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جدول expenses: {e}")
        
        # 5. ایجاد جدول partners
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS partners (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(120),
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ جدول partners ایجاد شد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جدول partners: {e}")
        
        # 6. ایجاد جدول partner_transactions
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS partner_transactions (
                    id INTEGER PRIMARY KEY,
                    partner_id INTEGER NOT NULL,
                    amount FLOAT NOT NULL,
                    transaction_type VARCHAR(20) NOT NULL,
                    description TEXT,
                    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partner_id) REFERENCES partners (id)
                );
            """)
            print("✅ جدول partner_transactions ایجاد شد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جدول partner_transactions: {e}")
        
        # 7. ایجاد صندوق‌های اصلی، A و B اگر وجود ندارند
        try:
            # صندوق اصلی
            cursor.execute("SELECT COUNT(*) FROM cashboxes WHERE name = 'اصلی'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO cashboxes (name, balance) VALUES ('اصلی', 0.0)")
                print("✅ صندوق اصلی ایجاد شد")
            else:
                print("⚠️ صندوق اصلی قبلاً وجود دارد")

            # صندوق A
            cursor.execute("SELECT COUNT(*) FROM cashboxes WHERE name = 'A'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO cashboxes (name, balance) VALUES ('A', 0.0)")
                print("✅ صندوق A ایجاد شد")
            else:
                print("⚠️ صندوق A قبلاً وجود دارد")

            # صندوق B
            cursor.execute("SELECT COUNT(*) FROM cashboxes WHERE name = 'B'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO cashboxes (name, balance) VALUES ('B', 0.0)")
                print("✅ صندوق B ایجاد شد")
            else:
                print("⚠️ صندوق B قبلاً وجود دارد")
        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد صندوق‌ها: {e}")

        # 8. اضافه کردن فیلدهای تسویه به جدول orders
        try:
            # بررسی وجود ستون‌های تسویه
            cursor.execute("PRAGMA table_info(orders)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'paid_amount' not in columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN paid_amount FLOAT DEFAULT 0.0")
                print("✅ ستون paid_amount اضافه شد")

            if 'is_settled' not in columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN is_settled BOOLEAN DEFAULT 0")
                print("✅ ستون is_settled اضافه شد")

            if 'settlement_date' not in columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN settlement_date DATETIME")
                print("✅ ستون settlement_date اضافه شد")

            if 'settlement_notes' not in columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN settlement_notes TEXT")
                print("✅ ستون settlement_notes اضافه شد")

        except sqlite3.Error as e:
            print(f"❌ خطا در اضافه کردن فیلدهای تسویه: {e}")

        # ذخیره تغییرات
        conn.commit()
        print("✅ تمام تغییرات با موفقیت ذخیره شد")
        
        return True
        
    except Exception as e:
        print(f"❌ خطای کلی: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("🔒 اتصال دیتابیس بسته شد")

if __name__ == "__main__":
    print("🚀 شروع بروزرسانی دیتابیس...")
    success = update_database()
    
    if success:
        print("🎉 بروزرسانی دیتابیس با موفقیت انجام شد!")
    else:
        print("💥 بروزرسانی دیتابیس با خطا مواجه شد!")
