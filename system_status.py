import sqlite3


def check_system_status():
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    print("=" * 50)
    print("📊 تقرير النظام الشامل - مركز الصقر 📊")
    print("=" * 50)

    # 1. فحص ديون العميل
    cursor.execute('SELECT Name, Total_Debt FROM Customers WHERE Customer_ID = 1')
    customer = cursor.fetchone()
    if customer:
        print(f"👤 حساب العميل ({customer[0]}): عليه ديون بقيمة {customer[1]} جنيه")
    print("-" * 50)

    # 2. فحص رصيد الخزينة
    cursor.execute('SELECT SUM(Amount) FROM Treasury')
    treasury_balance = cursor.fetchone()[0]
    if treasury_balance is None:
        treasury_balance = 0
    print(f"💰 إجمالي النقدية في الخزينة: {treasury_balance} جنيه")
    print("-" * 50)

    # 3. فحص الكميات في المخزن
    cursor.execute('SELECT Name, Stock_Qty FROM Items')
    items = cursor.fetchall()
    print("📦 حالة المخزن الحالية (الكميات المتبقية):")
    for item in items:
        name = item[0]
        qty = item[1]
        print(f"- {name}: متبقي {qty} وحدة")

    print("=" * 50)
    conn.close()


if __name__ == '__main__':
    check_system_status()