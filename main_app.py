import flet as ft
import sqlite3


def main(page: ft.Page):
    # إعدادات نافذة التطبيق
    page.title = "نظام مركز الصقر"
    page.window_width = 400  # عرض مناسب لشكل الموبايل
    page.window_height = 700
    page.rtl = True  # لدعم اللغة العربية من اليمين لليسار
    page.theme_mode = ft.ThemeMode.DARK  # الوضع الليلي (Dark Mode) المفضل لك

    # العناصر المرئية (النصوص والأعمدة)
    title_text = ft.Text("مرحباً بك في نظام مركز الصقر", size=22, weight="bold", color=ft.colors.BLUE_400)
    inventory_display = ft.Column()  # عمود فارغ سنضع فيه بيانات المخزن لاحقاً

    # دالة تعمل عند الضغط على الزر
    def load_inventory(e):
        # تفريغ الشاشة أولاً لتجنب التكرار
        inventory_display.controls.clear()

        # الاتصال بقاعدة البيانات لجلب البضاعة
        conn = sqlite3.connect('falcon_center.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Name, Stock_Qty, Sale_Price FROM Items')
        items = cursor.fetchall()
        conn.close()

        # إضافة كل قطعة كـ "بطاقة نصية" داخل الشاشة
        for item in items:
            item_name = item[0]
            item_qty = item[1]
            item_price = item[2]

            # تصميم شكل القطعة في الواجهة
            row = ft.Container(
                content=ft.Text(f"📦 {item_name} | الكمية: {item_qty} | السعر: {item_price} ج", size=16),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=10,
                border_radius=8,
                margin=5
            )
            inventory_display.controls.append(row)

        # تحديث الشاشة لإظهار البيانات الجديدة
        page.update()

    # إنشاء زر الجرد وربطه بالدالة
    check_btn = ft.ElevatedButton("جرد المخزن", icon=ft.icons.INVENTORY, on_click=load_inventory)

    # إضافة كل العناصر (العنوان، الزر، والعمود) إلى الشاشة
    page.add(
        title_text,
        ft.Divider(),
        check_btn,
        inventory_display
    )


# تشغيل التطبيق
ft.app(target=main)