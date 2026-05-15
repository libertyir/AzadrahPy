# 🔍 Network Scanner Suite

مجموعه‌ای از ابزارهای شبکه برای اسکن و بررسی در دسترس بودن **دامنه‌ها (Domain Scanner)** و **آیپی‌ها (IP Scanner)**

> **⚠️ توجه:** این پروژه‌ها به طور کامل توسط **هوش مصنوعی (AI Assistant)** نوشته و تولید شده‌اند و همچنان در حال توسعه هستند.

---

## 📦 پروژه‌های موجود

### 1. 🌐 Domain Scanner
اسکنر دامنه چندنخی با پشتیبانی از فایل‌های GeoSite (V2Ray)

**قابلیت‌ها:**
- اسکن چندنخی با قابلیت تنظیم تردها
- پشتیبانی از تگ‌های `geosite:` برای استخراج خودکار دامنه
- تشخیص دامنه‌های زنده با متد HEAD
- کنترل‌های Pause/Resume/Stop
- آرشیو نتایج و جلوگیری از اسکن مجدد

**لینک‌ها:**
- [مشاهده README کامل](DomainScanner/README.md)
- [پوشه پروژه](DomainScanner/)

---

### 2. 🖧 IP Scanner
اسکنر IP چندنخی با پشتیبانی از CIDR، GeoIP و استخراج دامنه از گواهی SSL

**قابلیت‌ها:**
- سه روش اسکن: Fast، Deep و Fake SNI
- پشتیبانی از محدوده‌های CIDR (مثل `45.115.42.0/23`)
- استخراج دامنه از گواهی SSL (CN و SAN)
- پشتیبانی از فایل GeoIP برای استخراج IP بر اساس کشور
- کنترل‌های Pause/Resume/Stop

**لینک‌ها:**
- [مشاهده README کامل](IpScanner/README.md)
- [پوشه پروژه](IpScanner/)

---

## 🚀 شروع سریع

### Clone مخزن
```bash
git clone https://github.com/your-username/network-scanner-suite.git
cd network-scanner-suite
```

### اجرای Domain Scanner
```bash
cd DomainScanner
pip install -r requirements.txt
python main.py
```

### اجرای IP Scanner
```bash
cd IpScanner
pip install -r requirements.txt
python ip_main.py
```

---

## 📁 ساختار پروژه

```
network-scanner-suite/
├── DomainScanner/           # پروژه اسکنر دامنه
│   ├── main.py
│   ├── README.md
│   └── ...
├── IpScanner/               # پروژه اسکنر IP
│   ├── ip_main.py
│   ├── README.md
│   └── ...
└── README.md                # این فایل
```

---

## ⚙️ پیش‌نیازها

- Python 3.7 یا بالاتر
- کتابخانه `requests` (برای هر دو پروژه)

```bash
pip install requests
```

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.

---

## 🤝 وضعیت توسعه

هر دو پروژه **در حال توسعه (Under Development)** هستند. ویژگی‌های جدید به مرور اضافه خواهند شد.

- **Domain Scanner**: پایدار و قابل استفاده
- **IP Scanner**: پایدار و قابل استفاده

---

## 📞 ارتباط

برای گزارش مشکلات یا پیشنهادات، لطفاً در مخزن مربوطه **Issue** ایجاد کنید.

---

<p align="center">
  <b>Network Scanner Suite</b><br>
  توسعه یافته توسط <b>هوش مصنوعی (AI Assistant)</b><br>
  با ❤️ برای جامعه برنامه‌نویسان ایران
</p>
