import sqlite3


def view_inventory():
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    # أمر جلب جميع البيانات من جدول المخزن
    cursor.execute('SELECT * FROM Items')
    items = cursor.fetchall()  # جلب كل النتائج ووضعها في قائمة

    # طباعة البيانات بشكل منظم
    print("=" * 50)
    print("📋 جرد مخزن مركز الصقر 📋")
    print("=" * 50)

    # المرور على كل قطعة وطباعتها
    for item in items:
        item_id = item[0]
        name = item[1]
        purchase_price = item[2]
        sale_price = item[3]
        qty = item[4]

        print(f"الرقم: {item_id} | القطعة: {name}")
        print(f"الكمية المتاحة: {qty} | سعر البيع: {sale_price} جنيه")
        print("-" * 50)

    # إغلاق الاتصال
    conn.close()


if __name__ == '__main__':
    view_inventory()