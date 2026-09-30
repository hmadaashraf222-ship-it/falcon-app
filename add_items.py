import sqlite3


def add_inventory_items():
    # الاتصال بقاعدة البيانات التي أنشأناها
    conn = sqlite3.connect('falcon_center.db')
    cursor = conn.cursor()

    # قائمة ببعض قطع الغيار (اسم القطعة، سعر الشراء، سعر البيع، الكمية المتوفرة)
    items_to_add = [
        ('أسطوانة فريون 134a', 1500, 1800, 5),
        ('كباس 1.5 حصان', 3000, 3500, 2),
        ('مكثف (كابستور) تكييف', 100, 150, 20),
        ('مروحة تبريد ثلاجة', 250, 350, 10)
    ]

    # أمر إدخال البيانات إلى جدول المخزن (Items)
    cursor.executemany('''
                       INSERT INTO Items (Name, Purchase_Price, Sale_Price, Stock_Qty)
                       VALUES (?, ?, ?, ?)
                       ''', items_to_add)

    # حفظ التغييرات وإغلاق الاتصال
    conn.commit()
    conn.close()

    print("تمت إضافة بضاعة 'مركز الصقر' إلى المخزن بنجاح!")


if __name__ == '__main__':
    add_inventory_items()