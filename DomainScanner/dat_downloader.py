import os
import requests
from typing import Optional, Dict

class DatDownloader:
    """
    دانلودر فایل‌های geosite.dat و geoip.dat از مخازن عمومی
    """
    def __init__(self):
        # لینک‌های رسمی پروژه V2Fly (پایدار و به‌روز)
        self.default_urls = {
            "geoip": "https://github.com/v2fly/geoip/releases/latest/download/geoip.dat",
            "geosite": "https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat"
        }
        # لینک‌های جایگزین (مثل CDN) برای مواقعی که فیلتر هست
        self.mirrors = {
            "geoip": "https://cdn.jsdelivr.net/gh/elysias123/geosite@release/geoip.dat",
            "geosite": "https://cdn.jsdelivr.net/gh/elysias123/geosite@release/geosite.dat"
        }

    def download_file(self, url: str, dest: str) -> bool:
        """دریافت فایل از آدرس مشخص شده"""
        try:
            print(f"⏳ در حال دانلود از {url} ...")
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ فایل با موفقیت ذخیره شد: {dest}")
                return True
            else:
                print(f"❌ خطا در دریافت فایل: کد وضعیت {r.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطا در دانلود: {e}")
            return False

    def download_geoip(self, dest: str = "geoip.dat", use_mirror=False) -> bool:
        url = self.mirrors["geoip"] if use_mirror else self.default_urls["geoip"]
        return self.download_file(url, dest)

    def download_geosite(self, dest: str = "geosite.dat", use_mirror=False) -> bool:
        url = self.mirrors["geosite"] if use_mirror else self.default_urls["geosite"]
        return self.download_file(url, dest)