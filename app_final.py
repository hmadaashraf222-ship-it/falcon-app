import flet as ft
import sqlite3
from datetime import datetime
import os
import webbrowser


def main(page: ft.Page):
    # إعدادات النافذة الأساسية
    page.title = "نظام مركز الصقر المتكامل"
    page.window_width = 1050
    page.window_height = 800
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK

    # --- تهيئة قاعدة البيانات بوضع آمن لمنع القفل ---
    def init_db():
        with sqlite3.connect('falcon_center.db') as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS Customers
                           (
                               Customer_ID
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               Name
                               TEXT,
                               Phone
                               TEXT,
                               Total_Debt
                               REAL
                               DEFAULT
                               0
                           )
                           ''')

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS Items
                           (
                               Item_ID
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               Name
                               TEXT,
                               Purchase_Price
                               REAL,
                               Sale_Price
                               REAL,
                               Stock_Qty
                               INTEGER
                           )
                           ''')

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS Maintenance_Orders
                           (
                               Order_ID
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               Customer_ID
                               INTEGER,
                               Device_Type
                               TEXT,
                               Issue_Description
                               TEXT,
                               Labor_Cost
                               REAL,
                               Total_Cost
                               REAL,
                               Paid_Amount
                               REAL,
                               Remaining_Amount
                               REAL,
                               Order_Date
                               TEXT
                           )
                           ''')

            cursor.execute("PRAGMA table_info(Maintenance_Orders)")
            columns = [col[1] for col in cursor.fetchall()]
            if "Order_Date" not in columns:
                try:
                    cursor.execute("ALTER TABLE Maintenance_Orders ADD COLUMN Order_Date TEXT")
                except:
                    pass

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
                               INTEGER
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

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS Returns
                           (
                               Return_ID
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               Customer_ID
                               INTEGER,
                               Item_ID
                               INTEGER,
                               Qty
                               INTEGER,
                               Refund_Amount
                               REAL,
                               Return_Date
                               TEXT
                           )
                           ''')
            conn.commit()

    init_db()

    main_content = ft.Container(expand=True, padding=20)

    # ==========================================
    # دالة توليد فاتورة HTML عربية احترافية مع اللوجو
    # ==========================================
    def generate_arabic_invoice_html(order_id, customer_name, phone, device, issue, labor, parts_name, parts_qty,
                                     parts_total, total, paid, remaining, date_str):
        try:
            invoices_dir = os.path.join(os.getcwd(), "Invoices")
            if not os.path.exists(invoices_dir):
                os.makedirs(invoices_dir)

            file_name = f"Invoice_{order_id}.html"
            full_path = os.path.join(invoices_dir, file_name)

            # تصميم HTML احترافي يدعم اللغة العربية والطباعة وتنسيق الفواتير
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>فاتورة صيانة - مركز الصقر</title>
                <style>
                    body {{
                        font-family: 'Cairo', 'Tahoma', Arial, sans-serif;
                        background-color: #f4f6f9;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }}
                    .invoice-box {{
                        max-width: 800px;
                        margin: auto;
                        background: #fff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 15px rgba(0, 0, 0, 0.15);
                    }}
                    .header-table {{
                        width: 100%;
                        border-bottom: 2px solid #0056b3;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                    }}
                    .header-table td {{
                        vertical-align: middle;
                    }}
                    .logo-section h2 {{
                        color: #0056b3;
                        margin: 0;
                        font-size: 26px;
                    }}
                    .logo-section p {{
                        margin: 3px 0;
                        color: #666;
                        font-size: 14px;
                    }}
                    .invoice-info {{
                        text-align: left;
                    }}
                    .invoice-info h3 {{
                        color: #333;
                        margin: 0;
                    }}
                    .details-table {{
                        width: 100%;
                        margin-top: 15px;
                        margin-bottom: 20px;
                        border-collapse: collapse;
                    }}
                    .details-table td {{
                        padding: 8px 0;
                        font-size: 15px;
                    }}
                    .items-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    .items-table th, .items-table td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: center;
                    }}
                    .items-table th {{
                        background-color: #0056b3;
                        color: white;
                        font-size: 15px;
                    }}
                    .totals-section {{
                        margin-top: 20px;
                        width: 100%;
                    }}
                    .totals-table {{
                        width: 350px;
                        float: left;
                        border-collapse: collapse;
                    }}
                    .totals-table td {{
                        padding: 8px 12px;
                        border: 1px solid #ddd;
                        font-size: 15px;
                    }}
                    .totals-table tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    .footer {{
                        clear: both;
                        margin-top: 50px;
                        text-align: center;
                        font-size: 14px;
                        color: #777;
                        border-top: 1px solid #ddd;
                        padding-top: 15px;
                    }}
                    .print-btn {{
                        display: block;
                        width: 200px;
                        margin: 30px auto 0 auto;
                        padding: 12px;
                        background-color: #28a745;
                        color: white;
                        text-align: center;
                        border: none;
                        border-radius: 5px;
                        font-size: 16px;
                        cursor: pointer;
                        font-weight: bold;
                    }}
                    .print-btn:hover {{
                        background-color: #218838;
                    }}
                    @media print {{
                        .print-btn {{
                            display: none;
                        }}
                        body {{
                            background-color: #fff;
                            padding: 0;
                        }}
                        .invoice-box {{
                            box-shadow: none;
                            padding: 0;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="invoice-box">
                    <table class="header-table">
                        <tr>
                            <td class="logo-section">
                                <h2>🦅 مركز الصقر</h2>
                                <p>لأعمال التبريد والتكييف وصيانة الأجهزة المنزلية</p>
                                <p>العنوان: بيشة عامر / منيا القمح، الشرقية</p>
                                <p>هاتف: 01026381296</p>
                            </td>
                            <td class="invoice-info">
                                <h3>فاتورة صيانة رقم: #{order_id}</h3>
                                <p>التاريخ: {date_str}</p>
                            </td>
                        </tr>
                    </table>

                    <table class="details-table">
                        <tr>
                            <td><strong>اسم العميل:</strong> {customer_name}</td>
                            <td><strong>رقم الهاتف:</strong> {phone if phone else 'غير مسجل'}</td>
                        </tr>
                        <tr>
                            <td><strong>نوع الجهاز:</strong> {device}</td>
                            <td><strong>العطل المبلغ عنه:</strong> {issue}</td>
                        </tr>
                    </table>

                    <table class="items-table">
                        <thead>
                            <tr>
                                <th>الوصف / البيان</th>
                                <th>الكمية</th>
                                <th>الإجمالي (جنيه)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="text-align: right;">تكلفة المصنعية والخدمة</td>
                                <td>1</td>
                                <td>{labor} ج.م</td>
                            </tr>
            """

            if parts_name:
                html_content += f"""
                            <tr>
                                <td style="text-align: right;">قطعة غيار: {parts_name}</td>
                                <td>{parts_qty}</td>
                                <td>{parts_total} ج.م</td>
                            </tr>
                """

            html_content += f"""
                        </tbody>
                    </table>

                    <div class="totals-section">
                        <table class="totals-table">
                            <tr>
                                <td><strong>الإجمالي العام:</strong></td>
                                <td><strong>{total} ج.م</strong></td>
                            </tr>
                            <tr>
                                <td>المدفوع:</td>
                                <td>{paid} ج.م</td>
                            </tr>
                            <tr>
                                <td><strong>المتبقي (آذان/دين):</strong></td>
                                <td><strong style="color: {'red' if remaining > 0 else 'green'};">{remaining} ج.م</strong></td>
                            </tr>
                        </table>
                    </div>

                    <div class="footer">
                        <p>شكراً لتعاملكم معنا - مركز الصقر للصيانة</p>
                    </div>

                    <button class="print-btn" onclick="window.print()">🖨️ طباعة الفاتورة / حفظ PDF</button>
                </div>
            </body>
            </html>
            """

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # فتح الفاتورة تلقائياً في المتصفح لتتمكن من معاينتها وطباعتها فوراً
            webbrowser.open(full_path)
            return full_path
        except Exception as e:
            print(f"HTML Invoice Error: {e}")
            return None

    # ==========================================
    # 1. شاشة جرد المخزن
    # ==========================================
    def get_inventory_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        view.controls.append(ft.Text("📦 جرد المخزن المباشر", size=24, weight="bold", color=ft.colors.BLUE_300))

        search_in = ft.TextField(label="🔍 ابحث باسم القطعة...", width=500)
        items_list = ft.Column(spacing=10)

        def load_inventory(e=None):
            items_list.controls.clear()
            search_text = search_in.value if search_in.value else ""

            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                if search_text:
                    cursor.execute('SELECT Name, Stock_Qty, Sale_Price FROM Items WHERE Name LIKE ?',
                                   (f'%{search_text}%',))
                else:
                    cursor.execute('SELECT Name, Stock_Qty, Sale_Price FROM Items')
                items = cursor.fetchall()

            for item in items:
                items_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"{item[0]} | متاح: {item[1]} | السعر: {item[2]}ج", size=18),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        padding=15, border_radius=8, width=500
                    )
                )
            page.update()

        search_in.on_change = load_inventory
        load_inventory()

        view.controls.extend([search_in, items_list])
        return view

    # ==========================================
    # 2. شاشة إنشاء الفاتورة
    # ==========================================
    def get_invoice_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        view.controls.append(
            ft.Text("🧾 فاتورة صيانة جديدة وتصدير عربي", size=24, weight="bold", color=ft.colors.BLUE_300))

        today_date = datetime.now().strftime("%Y-%m-%d")
        date_in = ft.TextField(label="تاريخ الفاتورة", value=today_date, width=180, read_only=True)

        selected_cust_id = [None]
        cust_search_in = ft.TextField(label="🔍 اسم العميل (ابحث أو اكتب عميل جديد)", width=350)
        cust_phone_in = ft.TextField(label="رقم الهاتف", width=180)
        cust_results_list = ft.ListView(height=100, visible=False)

        def search_customers(e):
            selected_cust_id[0] = None
            if not cust_search_in.value:
                cust_phone_in.value = ""
                cust_results_list.visible = False
                page.update()
                return

            cust_results_list.controls.clear()
            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Customer_ID, Name, Phone FROM Customers WHERE Name LIKE ?",
                               (f'%{cust_search_in.value}%',))
                customers = cursor.fetchall()

            if customers:
                cust_results_list.visible = True
                for cust in customers:
                    c_id, c_name, c_phone = cust
                    cust_results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(f"{c_name} - {c_phone if c_phone else 'بدون رقم'}"),
                            on_click=lambda e, cid=c_id, cname=c_name, cphone=c_phone: select_customer(cid, cname,
                                                                                                       cphone)
                        )
                    )
            else:
                cust_results_list.visible = False
            page.update()

        def select_customer(cid, cname, cphone):
            selected_cust_id[0] = cid
            cust_search_in.value = cname
            cust_phone_in.value = cphone if cphone else ""
            cust_results_list.visible = False
            page.update()

        cust_search_in.on_change = search_customers

        dev_in = ft.TextField(label="الجهاز", width=200)
        issue_in = ft.TextField(label="العطل", width=330)

        selected_part_id = [None]
        search_in = ft.TextField(label="🔍 ابحث عن قطعة غيار", width=250)
        qty_in = ft.TextField(label="الكمية", value="1", width=100)
        results_list = ft.ListView(height=120, visible=False)

        def search_parts(e):
            results_list.controls.clear()
            if not search_in.value:
                results_list.visible = False
                selected_part_id[0] = None
                page.update()
                return
            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Item_ID, Name, Sale_Price, Stock_Qty FROM Items WHERE Stock_Qty > 0 AND Name LIKE ?",
                    (f'%{search_in.value}%',))
                items = cursor.fetchall()
            if items:
                results_list.visible = True
                for item in items:
                    i_id, name, price, qty = item
                    results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(f"{name} ({price}ج) - متاح: {qty}"),
                            on_click=lambda e, id=i_id, txt=name: select_part(id, txt)
                        )
                    )
            else:
                results_list.visible = False
            page.update()

        def select_part(i_id, txt):
            selected_part_id[0] = i_id
            search_in.value = txt
            results_list.visible = False
            page.update()

        search_in.on_change = search_parts

        labor_in = ft.TextField(label="المصنعية", width=175)
        paid_in = ft.TextField(label="المدفوع", width=175)
        msg = ft.Text(size=16)

        def save_invoice(e):
            if not cust_search_in.value:
                msg.value = "❌ يرجى إدخال اسم العميل"
                msg.color = ft.colors.RED
                page.update()
                return

            try:
                with sqlite3.connect('falcon_center.db') as conn:
                    cursor = conn.cursor()

                    if selected_cust_id[0]:
                        final_cust_id = selected_cust_id[0]
                        cursor.execute('UPDATE Customers SET Phone = ? WHERE Customer_ID = ?',
                                       (cust_phone_in.value, final_cust_id))
                    else:
                        cursor.execute('INSERT INTO Customers (Name, Phone, Total_Debt) VALUES (?, ?, 0)',
                                       (cust_search_in.value, cust_phone_in.value))
                        final_cust_id = cursor.lastrowid

                    parts_cost = 0
                    part_name_str = ""
                    part_qty_val = 0
                    if selected_part_id[0]:
                        cursor.execute('SELECT Name, Sale_Price FROM Items WHERE Item_ID = ?', (selected_part_id[0],))
                        p_info = cursor.fetchone()
                        if p_info:
                            part_name_str = p_info[0]
                            part_qty_val = int(qty_in.value) if qty_in.value else 1
                            parts_cost = p_info[1] * part_qty_val

                    labor_val = float(labor_in.value) if labor_in.value else 0.0
                    total = labor_val + parts_cost
                    paid_val = float(paid_in.value) if paid_in.value else 0.0
                    rem = total - paid_val
                    invoice_date = date_in.value

                    cursor.execute(
                        'INSERT INTO Maintenance_Orders (Customer_ID, Device_Type, Issue_Description, Labor_Cost, Total_Cost, Paid_Amount, Remaining_Amount, Order_Date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (final_cust_id, dev_in.value, issue_in.value, labor_val, total, paid_val, rem, invoice_date))
                    o_id = cursor.lastrowid

                    if selected_part_id[0]:
                        cursor.execute('INSERT INTO Order_Details (Order_ID, Item_ID, Qty) VALUES (?, ?, ?)',
                                       (o_id, selected_part_id[0], part_qty_val))
                        cursor.execute('UPDATE Items SET Stock_Qty = Stock_Qty - ? WHERE Item_ID = ?',
                                       (part_qty_val, selected_part_id[0]))

                    if rem > 0:
                        cursor.execute('UPDATE Customers SET Total_Debt = Total_Debt + ? WHERE Customer_ID = ?',
                                       (rem, final_cust_id))
                    if paid_val > 0:
                        cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)', ('إيراد صيانة', paid_val))
                    conn.commit()

                # توليد الفاتورة العربية بالمتصفح والطباعة
                html_path = generate_arabic_invoice_html(
                    o_id, cust_search_in.value, cust_phone_in.value, dev_in.value,
                    issue_in.value, labor_val, part_name_str, part_qty_val, parts_cost,
                    total, paid_val, rem, invoice_date
                )

                if html_path:
                    msg.value = f"✅ تم الحفظ وفتح الفاتورة العربية في المتصفح!\nرقم الفاتورة: {o_id}\nمسار الملف: {html_path}"
                    msg.color = ft.colors.GREEN
                else:
                    msg.value = f"⚠️ تم حفظ الفاتورة (رقم {o_id}), ولكن حدث خطأ أثناء فتح المتصفح."
                    msg.color = ft.colors.ORANGE

                cust_search_in.value = "";
                cust_phone_in.value = "";
                selected_cust_id[0] = None;
                cust_results_list.visible = False
                search_in.value = "";
                qty_in.value = "1";
                selected_part_id[0] = None;
                results_list.visible = False
                dev_in.value = "";
                issue_in.value = "";
                labor_in.value = "";
                paid_in.value = ""
                page.update()

            except Exception as ex:
                msg.value = f"❌ خطأ: {ex}"
                msg.color = ft.colors.RED
                page.update()

        save_btn = ft.ElevatedButton("حفظ وطباعة الفاتورة العربية", on_click=save_invoice, width=360, height=45,
                                     bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)

        view.controls.extend([
            ft.Row([cust_search_in, cust_phone_in, date_in]), cust_results_list,
            ft.Row([dev_in, issue_in]), ft.Divider(),
            ft.Row([search_in, qty_in]), results_list, ft.Divider(),
            ft.Row([labor_in, paid_in]), save_btn, msg
        ])
        return view

    # ==========================================
    # 3. شاشة المشتريات
    # ==========================================
    def get_purchases_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        view.controls.append(ft.Text("🛒 المشتريات وإضافة بضاعة", size=24, weight="bold", color=ft.colors.BLUE_300))

        selected_item_id = [None]
        search_in = ft.TextField(label="🔍 اكتب اسم الصنف (للبحث أو إضافة جديد)", width=450)
        results_list = ft.ListView(height=120, visible=False)

        qty_input = ft.TextField(label="الكمية", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=110)
        p_price_input = ft.TextField(label="سعر الشراء", keyboard_type=ft.KeyboardType.NUMBER, width=110)
        s_price_input = ft.TextField(label="سعر البيع", keyboard_type=ft.KeyboardType.NUMBER, width=110)
        msg = ft.Text(size=16)

        def search_items(e):
            selected_item_id[0] = None
            p_price_input.value = ""
            s_price_input.value = ""

            results_list.controls.clear()
            if not search_in.value:
                results_list.visible = False
                page.update()
                return

            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Item_ID, Name, Purchase_Price, Sale_Price FROM Items WHERE Name LIKE ?",
                               (f'%{search_in.value}%',))
                items = cursor.fetchall()

            if items:
                results_list.visible = True
                for item in items:
                    i_id, name, p_price, s_price = item
                    results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(name),
                            subtitle=ft.Text(f"سعر الشراء: {p_price}ج | البيع: {s_price}ج", color=ft.colors.GREY_400),
                            on_click=lambda e, id=i_id, txt=name, pp=p_price, sp=s_price: select_item(id, txt, pp, sp)
                        )
                    )
            else:
                results_list.visible = False
            page.update()

        def select_item(i_id, txt, pp, sp):
            selected_item_id[0] = i_id
            search_in.value = txt
            p_price_input.value = str(pp)
            s_price_input.value = str(sp)
            results_list.visible = False
            page.update()

        search_in.on_change = search_items

        def save_purchase(e):
            if not search_in.value:
                msg.value = "❌ يرجى كتابة اسم الصنف!"
                msg.color = ft.colors.RED
                page.update()
                return

            try:
                qty = int(qty_input.value)
                p_price = float(p_price_input.value)
                s_price = float(s_price_input.value)
                total_cost = qty * p_price

                with sqlite3.connect('falcon_center.db') as conn:
                    cursor = conn.cursor()
                    if selected_item_id[0]:
                        cursor.execute(
                            'UPDATE Items SET Stock_Qty = Stock_Qty + ?, Purchase_Price = ?, Sale_Price = ? WHERE Item_ID = ?',
                            (qty, p_price, s_price, selected_item_id[0]))
                    else:
                        cursor.execute(
                            'INSERT INTO Items (Name, Purchase_Price, Sale_Price, Stock_Qty) VALUES (?, ?, ?, ?)',
                            (search_in.value, p_price, s_price, qty))

                    cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)', ('مشتريات بضاعة', -total_cost))
                    conn.commit()

                msg.value = f"✅ تم الحفظ! التكلفة: {total_cost}ج"
                msg.color = ft.colors.GREEN
                search_in.value = "";
                qty_input.value = "1"
                p_price_input.value = "";
                s_price_input.value = ""
                selected_item_id[0] = None;
                results_list.visible = False
                page.update()
            except Exception as ex:
                msg.value = "❌ خطأ: تأكد من كتابة الأرقام بشكل صحيح."
                msg.color = ft.colors.RED
                page.update()

        save_btn = ft.ElevatedButton("حفظ وإضافة للمخزن", on_click=save_purchase, width=350, height=45)

        view.controls.extend([
            search_in, results_list,
            ft.Row([qty_input, p_price_input, s_price_input]),
            ft.Divider(color=ft.colors.WHITE24),
            save_btn, msg
        ])
        return view

    # ==========================================
    # 4. شاشة العملاء
    # ==========================================
    def get_customers_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        view.controls.append(ft.Text("👥 إدارة العملاء والديون", size=24, weight="bold", color=ft.colors.BLUE_300))

        search_in = ft.TextField(label="🔍 ابحث باسم العميل أو رقمه...", width=500)
        customers_list = ft.Column(spacing=10)

        def load_customers(e=None):
            try:
                customers_list.controls.clear()
                search_text = search_in.value if search_in.value else ""

                with sqlite3.connect('falcon_center.db') as conn:
                    cursor = conn.cursor()
                    if search_text:
                        cursor.execute(
                            'SELECT Customer_ID, Name, Phone, Total_Debt FROM Customers WHERE Name LIKE ? OR Phone LIKE ?',
                            (f'%{search_text}%', f'%{search_text}%'))
                    else:
                        cursor.execute('SELECT Customer_ID, Name, Phone, Total_Debt FROM Customers')
                    customers = cursor.fetchall()

                for cust in customers:
                    c_id, name, phone, debt = cust

                    history_container = ft.Container(visible=False, padding=10, bgcolor=ft.colors.BLACK12,
                                                     border_radius=5)

                    def toggle_history(e, cid=c_id, container=history_container):
                        if container.visible:
                            container.visible = False
                            e.control.text = "📜 عرض سجل الأعطال"
                            e.control.bgcolor = ft.colors.BLUE_GREY_800
                        else:
                            with sqlite3.connect('falcon_center.db') as conn_h:
                                cursor_h = conn_h.cursor()
                                cursor_h.execute(
                                    'SELECT Order_ID, Device_Type, Issue_Description, Order_Date FROM Maintenance_Orders WHERE Customer_ID = ? ORDER BY Order_ID DESC',
                                    (cid,))
                                orders = cursor_h.fetchall()

                                history_controls = []
                                if orders:
                                    history_controls.append(
                                        ft.Text("🛠️ سجل الأعطال السابق:", weight="bold", color=ft.colors.BLUE_200))
                                    for order in orders:
                                        o_id, dev, issue, o_date = order
                                        date_str = str(o_date)[:10] if o_date else "تاريخ غير مسجل"

                                        cursor_h.execute('''
                                                         SELECT Items.Name, Order_Details.Qty
                                                         FROM Order_Details
                                                                  JOIN Items ON Order_Details.Item_ID = Items.Item_ID
                                                         WHERE Order_Details.Order_ID = ?
                                                         ''', (o_id,))
                                        parts = cursor_h.fetchall()
                                        parts_str = "، ".join([f"{p[0]} (الكمية: {p[1]})" for p in
                                                               parts]) if parts else "لم يتم سحب قطع غيار"

                                        history_controls.append(
                                            ft.Container(
                                                content=ft.Column([
                                                    ft.Text(f"📅 التاريخ: {date_str} | الجهاز: {dev}", weight="bold"),
                                                    ft.Text(f"⚠️ العطل: {issue}", color=ft.colors.GREY_300),
                                                    ft.Text(f"⚙️ قطع الغيار: {parts_str}", color=ft.colors.AMBER_200,
                                                            size=14),
                                                ], spacing=2),
                                                bgcolor=ft.colors.BLACK26,
                                                padding=8, border_radius=4, margin=ft.margin.only(bottom=5)
                                            )
                                        )
                                else:
                                    history_controls.append(
                                        ft.Text("لا يوجد سجل صيانة سابق لهذا العميل.", color=ft.colors.GREY_500))

                            container.content = ft.Column(history_controls, spacing=5)
                            container.visible = True
                            e.control.text = "🔼 إخفاء سجل الأعطال"
                            e.control.bgcolor = ft.colors.GREY_700

                        page.update()

                    history_btn = ft.ElevatedButton("📜 عرض سجل الأعطال", on_click=toggle_history,
                                                    bgcolor=ft.colors.BLUE_GREY_800, color=ft.colors.WHITE, height=35)

                    pay_amount_input = ft.TextField(label="مبلغ السداد", width=120, height=40,
                                                    keyboard_type=ft.KeyboardType.NUMBER)

                    def pay_debt_action(e, customer_id=c_id, input_field=pay_amount_input, customer_name=name):
                        try:
                            amount = float(input_field.value)
                            if amount <= 0: return
                            with sqlite3.connect('falcon_center.db') as conn_pay:
                                cursor_pay = conn_pay.cursor()
                                cursor_pay.execute(
                                    'UPDATE Customers SET Total_Debt = Total_Debt - ? WHERE Customer_ID = ?',
                                    (amount, customer_id))
                                cursor_pay.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)',
                                                   (f'سداد دين: {customer_name}', amount))
                                conn_pay.commit()
                            load_customers()
                        except:
                            pass

                    pay_btn = ft.ElevatedButton("سداد", on_click=pay_debt_action, bgcolor=ft.colors.GREEN_700,
                                                color=ft.colors.WHITE, height=40)
                    debt_color = ft.colors.RED_400 if debt > 0 else ft.colors.GREEN_400
                    status_text = f"الديون: {debt} جنيه" if debt > 0 else "✅ الحساب خالص"
                    payment_row = ft.Row([pay_amount_input, pay_btn]) if debt > 0 else ft.Container()

                    customers_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"👤 {name} | 📞 {phone if phone else 'بدون رقم'}", size=18, weight="bold"),
                                    ft.Text(status_text, color=debt_color, size=16, weight="bold")
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([payment_row, history_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                history_container
                            ]),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            padding=12, border_radius=8, width=650
                        )
                    )
                page.update()
            except Exception as err:
                customers_list.controls.append(ft.Text(f"❌ تفاصيل الخطأ: {err}", color=ft.colors.RED, size=16))
                page.update()

        search_in.on_change = load_customers
        load_customers()

        view.controls.extend([search_in, customers_list])
        return view

    # ==========================================
    # 5. شاشة المرتجعات
    # ==========================================
    def get_returns_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
        view.controls.append(ft.Text("↩️ إدارة المرتجعات", size=24, weight="bold", color=ft.colors.ORANGE_300))

        today_date = datetime.now().strftime("%Y-%m-%d")
        return_date_in = ft.TextField(label="تاريخ المرتجع", value=today_date, width=180, read_only=True)

        selected_cust_id = [None]
        cust_search_in = ft.TextField(label="🔍 اسم العميل المرتجع منه", width=350)
        cust_results_list = ft.ListView(height=90, visible=False)

        def search_customers_ret(e):
            selected_cust_id[0] = None
            if not cust_search_in.value:
                cust_results_list.visible = False
                page.update()
                return
            cust_results_list.controls.clear()
            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Customer_ID, Name, Phone FROM Customers WHERE Name LIKE ?",
                               (f'%{cust_search_in.value}%',))
                customers = cursor.fetchall()

            if customers:
                cust_results_list.visible = True
                for cust in customers:
                    c_id, c_name, c_phone = cust
                    cust_results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(f"{c_name} - {c_phone if c_phone else 'بدون رقم'}"),
                            on_click=lambda e, cid=c_id, cname=c_name: select_customer_ret(cid, cname)
                        )
                    )
            else:
                cust_results_list.visible = False
            page.update()

        def select_customer_ret(cid, cname):
            selected_cust_id[0] = cid
            cust_search_in.value = cname
            cust_results_list.visible = False
            page.update()

        cust_search_in.on_change = search_customers_ret

        selected_item_id = [None]
        item_search_in = ft.TextField(label="🔍 ابحث عن القطعة المراد إرجاعها للمخزن", width=350)
        item_qty_in = ft.TextField(label="الكمية المرتجعة", value="1", width=110, keyboard_type=ft.KeyboardType.NUMBER)
        refund_amount_in = ft.TextField(label="المبلغ المدفوع للعميل (المسترد)", width=180,
                                        keyboard_type=ft.KeyboardType.NUMBER)
        item_results_list = ft.ListView(height=90, visible=False)

        def search_items_ret(e):
            selected_item_id[0] = None
            if not item_search_in.value:
                item_results_list.visible = False
                page.update()
                return
            item_results_list.controls.clear()
            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Item_ID, Name, Sale_Price FROM Items WHERE Name LIKE ?",
                               (f'%{item_search_in.value}%',))
                items = cursor.fetchall()

            if items:
                item_results_list.visible = True
                for item in items:
                    i_id, name, price = item
                    item_results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(f"{name} (سعر البيع: {price}ج)"),
                            on_click=lambda e, id=i_id, txt=name, pr=price: select_item_ret(id, txt, pr)
                        )
                    )
            else:
                item_results_list.visible = False
            page.update()

        def select_item_ret(i_id, txt, pr):
            selected_item_id[0] = i_id
            item_search_in.value = txt
            refund_amount_in.value = str(pr)
            item_results_list.visible = False
            page.update()

        item_search_in.on_change = search_items_ret
        msg = ft.Text(size=16)

        def save_return(e):
            if not selected_cust_id[0] or not selected_item_id[0]:
                msg.value = "❌ يرجى اختيار العميل والقطعة المرتجعة من القوائم بشكل صحيح"
                msg.color = ft.colors.RED
                page.update()
                return

            try:
                qty = int(item_qty_in.value)
                refund_amt = float(refund_amount_in.value)
                if qty <= 0 or refund_amt < 0: return

                with sqlite3.connect('falcon_center.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO Returns (Customer_ID, Item_ID, Qty, Refund_Amount, Return_Date) VALUES (?, ?, ?, ?, ?)',
                        (selected_cust_id[0], selected_item_id[0], qty, refund_amt, return_date_in.value))

                    cursor.execute('UPDATE Items SET Stock_Qty = Stock_Qty + ? WHERE Item_ID = ?',
                                   (qty, selected_item_id[0]))
                    cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)',
                                   ('مرتجع مبيعات (صرف للعميل)', -refund_amt))
                    conn.commit()

                msg.value = f"✅ تم تسجيل المرتجع بنجاح وإرجاع القطعة للمخزن وخصم {refund_amt}ج من الخزينة."
                msg.color = ft.colors.GREEN

                cust_search_in.value = "";
                selected_cust_id[0] = None;
                cust_results_list.visible = False
                item_search_in.value = "";
                selected_item_id[0] = None;
                item_results_list.visible = False
                item_qty_in.value = "1";
                refund_amount_in.value = ""
                page.update()

            except Exception as ex:
                msg.value = f"❌ حدث خطأ: {ex}"
                msg.color = ft.colors.RED
                page.update()

        save_return_btn = ft.ElevatedButton("حفظ وتأكيد المرتجع", on_click=save_return, width=350, height=45,
                                            bgcolor=ft.colors.ORANGE_800, color=ft.colors.WHITE)

        view.controls.extend([
            ft.Row([cust_search_in, return_date_in]), cust_results_list,
            ft.Divider(color=ft.colors.WHITE24),
            ft.Row([item_search_in, item_qty_in]), item_results_list,
            refund_amount_in,
            ft.Divider(color=ft.colors.WHITE24),
            save_return_btn,
            msg
        ])
        return view

    # ==========================================
    # 6. شاشة الخزينة والمصروفات
    # ==========================================
    def get_treasury_view():
        view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
        view.controls.append(ft.Text("💰 الخزينة والمصروفات", size=24, weight="bold", color=ft.colors.BLUE_300))

        balance_display = ft.Text("جاري الحساب...", size=30, weight="bold", color=ft.colors.GREEN_400)

        exp_reason_in = ft.TextField(label="سبب المصروف (مثال: كهرباء، بوفيه)", width=300)
        exp_amount_in = ft.TextField(label="المبلغ", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        msg = ft.Text(size=16)

        history_list = ft.Column(spacing=8)

        def load_treasury():
            with sqlite3.connect('falcon_center.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(Amount) FROM Treasury')
                total = cursor.fetchone()[0]
                balance = total if total else 0

                balance_display.color = ft.colors.GREEN_400 if balance >= 0 else ft.colors.RED_400
                balance_display.value = f"الرصيد في الدرج: {balance} جنيه"

                cursor.execute('SELECT Type, Amount, Date FROM Treasury ORDER BY Transaction_ID DESC LIMIT 50')
                history = cursor.fetchall()

            history_list.controls.clear()
            for row in history:
                t_type, t_amount, t_date = row
                t_color = ft.colors.GREEN_300 if t_amount > 0 else ft.colors.RED_300
                date_str = t_date[:16]

                history_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"{date_str}", color=ft.colors.GREY_400, width=150),
                            ft.Text(f"{t_type}", width=250),
                            ft.Text(f"{t_amount}ج", color=t_color, weight="bold", size=18)
                        ]),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        padding=10, border_radius=6, width=650
                    )
                )
            page.update()

        def save_expense(e):
            try:
                reason = exp_reason_in.value
                amount = float(exp_amount_in.value)
                if not reason or amount <= 0: return

                with sqlite3.connect('falcon_center.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO Treasury (Type, Amount) VALUES (?, ?)', (f"مصروف: {reason}", -amount))
                    conn.commit()

                msg.value = "✅ تم خصم المصروف بنجاح"
                msg.color = ft.colors.GREEN
                exp_reason_in.value = ""
                exp_amount_in.value = ""
                load_treasury()
            except:
                msg.value = "❌ يرجى التأكد من كتابة المبلغ صحيحاً"
                msg.color = ft.colors.RED
                page.update()

        exp_btn = ft.ElevatedButton("خصم المصروف", on_click=save_expense, width=150, height=45,
                                    bgcolor=ft.colors.RED_700, color=ft.colors.WHITE)

        load_treasury()

        view.controls.extend([
            balance_default := balance_display,
            ft.Divider(color=ft.colors.WHITE24),
            ft.Text("إضافة مصروف خارجي:", color=ft.colors.GREY_300),
            ft.Row([exp_reason_in, exp_amount_in, exp_btn]),
            msg,
            ft.Divider(color=ft.colors.WHITE24),
            ft.Text("سجل حركات الخزينة (آخر 50 عملية):", color=ft.colors.GREY_300),
            history_list
        ])
        return view

    # ==========================================
    # شريط التنقل العلوي
    # ==========================================
    def show_invoice(e):
        main_content.content = get_invoice_view()
        page.update()

    def show_purchases(e):
        main_content.content = get_purchases_view()
        page.update()

    def show_inventory(e):
        main_content.content = get_inventory_view()
        page.update()

    def show_customers(e):
        main_content.content = get_customers_view()
        page.update()

    def show_returns(e):
        main_content.content = get_returns_view()
        page.update()

    def show_treasury(e):
        main_content.content = get_treasury_view()
        page.update()

    nav_bar = ft.Row([
        ft.ElevatedButton("🧾 الفاتورة", on_click=show_invoice, bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE),
        ft.ElevatedButton("🛒 المشتريات", on_click=show_purchases, bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE),
        ft.ElevatedButton("📦 المخزن", on_click=show_inventory, bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE),
        ft.ElevatedButton("👥 العملاء وسجل الصيانة", on_click=show_customers, bgcolor=ft.colors.GREEN_800,
                          color=ft.colors.WHITE),
        ft.ElevatedButton("↩ المرتجعات", on_click=show_returns, bgcolor=ft.colors.ORANGE_900, color=ft.colors.WHITE),
        ft.ElevatedButton("💰 الخزينة", on_click=show_treasury, bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE),
    ], wrap=True, spacing=10)

    main_content.content = get_invoice_view()

    page.add(
        ft.Column([
            nav_bar,
            ft.Divider(color=ft.colors.WHITE24),
            main_content
        ], expand=True)
    )


ft.app(target=main)