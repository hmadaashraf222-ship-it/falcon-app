import sqlite3


def create_maintenance_order():
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    # إنشاء جداول التفاصيل والخزينة (إذا لم تكن موجودة) لإتمام الترابط
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Order_Details
                   (
                       Detail_ID
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       Order_ID
                       INTEGER,
                       Item_ID
                       INTEGER,
                       Qty
                       INTEGER,
                       Price
                       REAL
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Treasury
                   (
                       Transaction_ID
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       Type
                       TEXT,
                       Amount
                       REAL,
                       Date
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    try:
        # 1. بيانات الفاتورة الأساسية
        customer_id = 1
        device_type = 'تكييف 1.5 حصان'
        issue = 'شحن فريون وتغيير كابستور'
        labor_cost = 200  # المصنعية 200 جنيه

        # القطع المستخدمة: (رقم القطعة Item_ID, الكمية Qty, سعر البيع Price)
        # رقم 1: فريون (1800 جنيه) ، رقم 3: كابستور (150 جنيه)
        used_items = [
            (1, 1, 1800),
            (3, 1, 150)
        ]

        # 2. الحسابات الآلية
        parts_cost = sum(qty * price for item_id, qty, price in used_items)  # 1950 جنيه
        total_cost = labor_cost + parts_cost  # الإجمالي 2150 جنيه
        paid_amount = 1500  # العميل دفع 1500 فقط
        remaining_amount = total_cost - paid_amount  # المتبقي عليه 650 جنيه

        # 3. حفظ الفاتورة
        cursor.execute('''
                       INSERT INTO Maintenance_Orders
                       (Customer_ID, Device_Type, Issue_Description, Labor_Cost, Total_Cost, Paid_Amount,
                        Remaining_Amount)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ''', (customer_id, device_type, issue, labor_cost, total_cost, paid_amount, remaining_amount))

        order_id = cursor.lastrowid  # سحب رقم الفاتورة الذي تم إنشاؤه للتو

        # 4. حفظ تفاصيل القطع وخصمها من المخزن فوراً
        for item_id, qty, price in used_items:
            cursor.execute('INSERT INTO Order_Details (Order_ID, Item_ID, Qty, Price) VALUES (?, ?, ?, ?)',
                           (order_id, item_id, qty, price))

            # أمر الخصم السحري من المخزن
            cursor.execute('UPDATE Items SET Stock_Qty = Stock_Qty - ? WHERE Item_ID = ?', (qty, item_id))

        # 5. تحديث ديون العميل (لو عليه فلوس)
        if remaining_amount > 0:
            cursor.execute('UPDATE Customers SET Total_Debt = Total_Debt + ? WHERE Customer_ID = ?',
                           (remaining_amount, customer_id))

        # 6. إضافة الفلوس المدفوعة للخزينة
        cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)', ('إيراد صيانة', paid_amount))

        # 7. تأكيد كل العمليات معاً (لو حصل خطأ في أي خطوة قبل السطر ده، الكود مش هيحفظ حاجة)
        conn.commit()

        # طباعة شكل الفاتورة
        print("=" * 50)
        print("🧾 فاتورة صيانة - مركز الصقر 🧾")
        print("📍 الإدارة: بيشة عامر / منيا القمح | 📞 01026381296")
        print("=" * 50)
        print(f"رقم الفاتورة: {order_id} | رقم العميل: {customer_id}")
        print(f"الجهاز: {device_type} | العطل: {issue}")
        print(f"إجمالي التكلفة (قطع غيار + مصنعية): {total_cost} جنيه")
        print(f"المدفوع: {paid_amount} جنيه | المتبقي (آجل): {remaining_amount} جنيه")
        print("-" * 50)
        print("✅ تم خصم القطع من المخزن وتحديث ديون العميل بنجاح!")
        print("=" * 50)

    except Exception as e:
        conn.rollback()  # التراجع عن كل شيء لحماية البيانات في حال وجود خطأ
        print(f"حدث خطأ، تم إلغاء العملية ولم يتم تعديل أي بيانات: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    create_maintenance_order()