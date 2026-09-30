import sqlite3

def create_tables():
    # إنشاء ملف قاعدة البيانات (إذا لم يكن موجوداً سيتم إنشاؤه تلقائياً)
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    # 1. جدول المخزن وقطع الغيار
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            Item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Purchase_Price REAL,
            Sale_Price REAL,
            Stock_Qty INTEGER DEFAULT 0
        )
    ''')

    # 2. جدول العملاء وديونهم
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Phone TEXT,
            Total_Debt REAL DEFAULT 0
        )
    ''')

    # 3. جدول أوامر الصيانة (الورشة)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Maintenance_Orders (
            Order_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer_ID INTEGER,
            Device_Type TEXT,
            Issue_Description TEXT,
            Labor_Cost REAL,
            Total_Cost REAL,
            Paid_Amount REAL,
            Remaining_Amount REAL,
            FOREIGN KEY(Customer_ID) REFERENCES Customers(Customer_ID)
        )
    ''')

    conn.commit()
    conn.close()
    print("تم إنشاء قاعدة البيانات وجداول مركز الصقر بنجاح!")

if __name__ == '__main__':
    create_tables()