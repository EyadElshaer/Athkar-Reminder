"""
Language support module for Athkar Reminder application.
Contains translations for all UI elements in different languages.
"""

# English language dictionary
ENGLISH = {
    # Application title and general terms
    "app_title": "Athkar Reminder",
    "ok": "OK",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "add": "Add",
    "edit": "Edit",
    "close": "Close",

    # Tab names
    "home_tab": "Home",
    "custom_duaas_tab": "Custom Duaas",
    "settings_tab": "Settings",
    "about_tab": "About",

    # Home tab
    "settings_group": "Settings",
    "reminder_interval": "Reminder interval (minutes):",
    "pause_reminders": "Pause Reminders",
    "resume_reminders": "Resume Reminders",
    "test_notification": "Test Notification",
    "status_group": "Status",
    "status_active": "Active - Next reminder in {time}",
    "status_paused": "Paused - Reminders are currently disabled",

    # Custom Duaas tab
    "all_duaas": "All Duaas",
    "add_new_duaa": "Add New Duaa",
    "add_duaa": "Add Duaa",
    "delete_selected": "Delete Selected",

    # Settings tab
    "app_settings": "Application Settings",
    "language_settings": "Language Settings",
    "choose_language": "Choose language:",
    "english": "English",
    "arabic": "العربية",
    "future_settings": "Additional settings will be available in future updates.",

    # About tab
    "about_title": "About Athkar Reminder",
    "about_text": "Athkar Reminder displays duaas of Prophet Mohammed ﷺ\n\nThe app runs in the background and shows notifications at your chosen interval. It adapts to your system theme automatically.\n\nYou can drag the notification window to any position on your screen, and use the copy button to copy the duaa text.",
    "developer_title": "Developed by",
    "developer_name": "Eyad Elshaer",
    "copyright_text": "All rights reserved",

    # System tray
    "show": "Show",
    "exit": "Exit",
    "tray_info": "Athkar Reminder will continue running in the system tray.\n\nTo exit completely, right-click the tray icon and select 'Exit'.",
    "tray_info_short": "App is running in the system tray.",
}

# Arabic language dictionary
ARABIC = {
    # Application title and general terms
    "app_title": "مذكر الأذكار",
    "ok": "موافق",
    "cancel": "إلغاء",
    "save": "حفظ",
    "delete": "حذف",
    "add": "إضافة",
    "edit": "تعديل",
    "close": "إغلاق",

    # Tab names
    "home_tab": "الرئيسية",
    "custom_duaas_tab": "الأدعية المخصصة",
    "settings_tab": "الإعدادات",
    "about_tab": "حول",

    # Home tab
    "settings_group": "الإعدادات",
    "reminder_interval": "الفاصل الزمني للتذكير (دقائق):",
    "pause_reminders": "إيقاف التذكير",
    "resume_reminders": "استئناف التذكير",
    "test_notification": "اختبار الإشعار",
    "status_group": "الحالة",
    "status_active": "نشط - التذكير التالي بعد: {time}",
    "status_paused": "متوقف - التذكير معطل حاليًا",

    # Custom Duaas tab
    "all_duaas": "جميع الأدعية",
    "add_new_duaa": "إضافة دعاء جديد",
    "add_duaa": "إضافة دعاء",
    "delete_selected": "حذف المحدد",

    # Settings tab
    "app_settings": "إعدادات التطبيق",
    "language_settings": "إعدادات اللغة",
    "choose_language": "اختر اللغة:",
    "english": "English",
    "arabic": "العربية",
    "future_settings": "ستتوفر إعدادات إضافية في التحديثات المستقبلية.",

    # About tab
    "about_title": "حول مذكر الأذكار",
    "about_text": "يعرض مذكر الأذكار أدعية النبي محمد ﷺ\n\nيعمل التطبيق في الخلفية ويعرض إشعارات في الفاصل الزمني الذي تختاره. يتكيف تلقائيًا مع سمة النظام.\n\nيمكنك سحب نافذة الإشعار إلى أي موضع على شاشتك، واستخدام زر النسخ لنسخ نص الدعاء.",
    "developer_title": "تطوير",
    "developer_name": "إياد الشاعر",
    "copyright_text": "جميع الحقوق محفوظة",

    # System tray
    "show": "عرض",
    "exit": "خروج",
    "tray_info": "سيستمر مذكر الأذكار في العمل في شريط النظام.\n\nللخروج بشكل كامل، انقر بزر الماوس الأيمن على أيقونة شريط النظام واختر 'خروج'.",
    "tray_info_short": "التطبيق يعمل في شريط النظام.",
}

# Dictionary of available languages
LANGUAGES = {
    "English": ENGLISH,
    "العربية": ARABIC
}

def get_text(language, key, **kwargs):
    """
    Get translated text for the given key in the specified language.
    Supports format string replacements via kwargs.

    Args:
        language (str): Language name ("English" or "العربية")
        key (str): Text key to retrieve
        **kwargs: Format string parameters

    Returns:
        str: Translated text
    """
    if language not in LANGUAGES:
        language = "English"  # Default to English if language not found

    text = LANGUAGES[language].get(key, LANGUAGES["English"].get(key, key))

    # Apply format string replacements if any kwargs provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text

    return text
