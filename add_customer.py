import sqlite3


def add_new_customer():
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    # بيانات العميل الجديد (الاسم، رقم الهاتف، إجمالي الديون المبدئي)
    # يمكنك تغيير الاسم والرقم كما تحب
    customer_data = ('أحمد محمود', '01012345678', 0)

    # أمر إدخال البيانات لجدول العملاء
    cursor.execute('''
                   INSERT INTO Customers (Name, Phone, Total_Debt)
                   VALUES (?, ?, ?)
                   ''', customer_data)

    # حفظ التغييرات
    conn.commit()

    # هذه الدالة تجلب رقم الـ ID للعميل الذي تم تسجيله للتو
    customer_id = cursor.lastrowid

    print(f"تم تسجيل العميل (أحمد محمود) بنجاح!")
    print(f"رقم العميل في النظام هو: {customer_id}")
    print("احتفظ بهذا الرقم لأننا سنستخدمه لعمل فاتورة الصيانة.")

    # إغلاق الاتصال
    conn.close()


if __name__ == '__main__':
    add_new_customer()