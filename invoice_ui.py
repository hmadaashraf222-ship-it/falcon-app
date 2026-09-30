import flet as ft
import sqlite3


def main(page: ft.Page):
    # إعدادات الشاشة
    page.title = "مركز الصقر - فاتورة ذكية"
    page.window_width = 450
    page.window_height = 850
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    page.add(ft.Text("إنشاء فاتورة شاملة ذكية", size=22, color=ft.colors.BLUE_400, weight="bold"))

    customer_id_input = ft.TextField(label="رقم العميل (مثال: 1)", keyboard_type=ft.KeyboardType.NUMBER)
    device_input = ft.TextField(label="نوع الجهاز")
    issue_input = ft.TextField(label="وصف العطل")

    # --- نظام البحث الذكي (الإكمال التلقائي) ---
    selected_part_id = [None]  # متغير مخفي لحفظ رقم القطعة عند اختيارها

    search_field = ft.TextField(label="🔍 ابحث واختر قطعة غيار (اكتب هنا)")
    part_qty_input = ft.TextField(label="الكمية", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=80)

    # القائمة المنسدلة التي ستظهر تحت مربع البحث
    results_list = ft.ListView(height=150, visible=False)

    def search_parts(e):
        search_text = search_field.value
        results_list.controls.clear()

        # لو مربع البحث فارغ، نخفي القائمة
        if not search_text:
            results_list.visible = False
            selected_part_id[0] = None
            page.update()
            return

        conn = sqlite3.connect('falcon_center.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Item_ID, Name, Sale_Price, Stock_Qty FROM Items WHERE Stock_Qty > 0 AND Name LIKE ?",
                       (f'%{search_text}%',))
        items = cursor.fetchall()
        conn.close()

        # لو وجدنا قطع مشابهة لما كتبه، نظهر القائمة المنسدلة
        if items:
            results_list.visible = True
            for item in items:
                item_id, name, price, qty = item
                text_display = f"{name} ({price}ج) - متاح: {qty}"

                # إضافة القطعة كزر يمكن الضغط عليه
                results_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(text_display),
                        leading=ft.Icon(ft.icons.SETTINGS),  # أيقونة بجوار اسم القطعة
                        on_click=lambda e, id=item_id, txt=name: select_part(id, txt)
                    )
                )
        else:
            results_list.visible = False

        page.update()

    def select_part(item_id, item_name):
        # عند الضغط على القطعة: احفظ رقمها، واكتب اسمها في المربع، وأخفِ القائمة
        selected_part_id[0] = item_id
        search_field.value = item_name
        results_list.visible = False
        page.update()

    search_field.on_change = search_parts  # ربط مربع البحث بالدالة
    # -----------------------------------------------------

    labor_cost_input = ft.TextField(label="تكلفة المصنعية (جنيه)", keyboard_type=ft.KeyboardType.NUMBER)
    paid_input = ft.TextField(label="المبلغ المدفوع (جنيه)", keyboard_type=ft.KeyboardType.NUMBER)
    result_msg = ft.Text(size=16)

    def save_invoice(e):
        try:
            c_id = int(customer_id_input.value)
            device = device_input.value
            issue = issue_input.value
            labor = float(labor_cost_input.value)
            paid = float(paid_input.value)

            conn = sqlite3.connect('falcon_center.db')
            cursor = conn.cursor()

            parts_cost = 0
            part_qty = int(part_qty_input.value)

            if selected_part_id[0]:
                cursor.execute('SELECT Sale_Price FROM Items WHERE Item_ID = ?', (selected_part_id[0],))
                part_price = cursor.fetchone()[0]
                parts_cost = part_price * part_qty

            total_cost = labor + parts_cost
            remaining = total_cost - paid

            cursor.execute('''
                           INSERT INTO Maintenance_Orders
                           (Customer_ID, Device_Type, Issue_Description, Labor_Cost, Total_Cost, Paid_Amount,
                            Remaining_Amount)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           ''', (c_id, device, issue, labor, total_cost, paid, remaining))
            order_id = cursor.lastrowid

            if selected_part_id[0]:
                cursor.execute('INSERT INTO Order_Details (Order_ID, Item_ID, Qty, Price) VALUES (?, ?, ?, ?)',
                               (order_id, selected_part_id[0], part_qty, part_price))
                cursor.execute('UPDATE Items SET Stock_Qty = Stock_Qty - ? WHERE Item_ID = ?',
                               (part_qty, selected_part_id[0]))

            if remaining > 0:
                cursor.execute('UPDATE Customers SET Total_Debt = Total_Debt + ? WHERE Customer_ID = ?',
                               (remaining, c_id))
            if paid > 0:
                cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)', ('إيراد صيانة', paid))

            conn.commit()
            conn.close()

            # تصفير كل الخانات بعد الحفظ
            selected_part_id[0] = None
            search_field.value = ""
            results_list.visible = False
            customer_id_input.value = ""
            device_input.value = ""
            issue_input.value = ""
            labor_cost_input.value = ""
            paid_input.value = ""
            part_qty_input.value = "1"

            result_msg.value = f"✅ تم الحفظ! رقم الفاتورة: {order_id} | الإجمالي: {total_cost}ج"
            result_msg.color = ft.colors.GREEN
            page.update()

        except Exception as ex:
            result_msg.value = "❌ يرجى ملء الخانات بشكل صحيح."
            result_msg.color = ft.colors.RED
            page.update()

    save_btn = ft.ElevatedButton("حفظ الفاتورة", on_click=save_invoice, width=380, height=50)

    # ترتيب مربع البحث والكمية بجوار بعضهما
    search_field.expand = True  # لجعل مربع البحث يأخذ المساحة الأكبر
    search_row = ft.Row([search_field, part_qty_input], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    page.add(
        customer_id_input, device_input, issue_input,
        ft.Divider(color=ft.colors.WHITE24),
        search_row,  # صف البحث والكمية
        results_list,  # القائمة المنسدلة (تظهر وتختفي ديناميكياً)
        ft.Divider(color=ft.colors.WHITE24),
        labor_cost_input, paid_input,
        save_btn, result_msg
    )


ft.app(target=main)