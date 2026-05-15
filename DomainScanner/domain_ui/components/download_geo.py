import os
from ..menu_manager import MenuManager
from dat_downloader import DatDownloader


class GeoDownloader:
    """Handle downloading of geosite.dat and geoip.dat files"""
    
    def __init__(self, geosite_manager):
        self.downloader = DatDownloader()
        self.menu_manager = MenuManager()
        self.geosite_manager = geosite_manager
    
    def download_menu(self):
        """Display download menu and handle user input"""
        while True:
            self.menu_manager.show_download_menu()
            
            print("\nCurrent files status:")
            geosite_exists = os.path.exists("geosite.dat")
            geoip_exists = os.path.exists("geoip.dat")
            print(f"  geosite.dat: {'✅ Exists' if geosite_exists else '❌ Missing'}")
            print(f"  geoip.dat:   {'✅ Exists' if geoip_exists else '❌ Missing'}")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._download_geosite()
            elif choice == '2':
                self._download_geoip()
            elif choice == '3':
                self._download_both()
            elif choice == '4':
                self._show_status()
            elif choice == '0':
                break
            else:
                print("\n[ERROR] Invalid choice!")
                input("\nPress Enter to continue...")
    
    def _download_geosite(self):
        print("\n📥 Downloading geosite.dat...")
        if self.downloader.download_geosite():
            print("\n✅ Download completed! Reloading geosite manager...")
            self.geosite_manager.reload()
            print("✅ Geosite manager reloaded successfully.")
        else:
            print("\n⚠️ Download failed. Trying mirror...")
            if self.downloader.download_geosite(use_mirror=True):
                print("✅ Download completed via mirror. Reloading...")
                self.geosite_manager.reload()
            else:
                print("❌ Download failed. Please check your internet connection.")
        input("\nPress Enter to continue...")
    
    def _download_geoip(self):
        print("\n📥 Downloading geoip.dat...")
        if self.downloader.download_geoip():
            print("\n✅ Download completed successfully!")
        else:
            print("\n⚠️ Download failed. Trying mirror...")
            if self.downloader.download_geoip(use_mirror=True):
                print("✅ Download completed via mirror.")
            else:
                print("❌ Download failed.")
        input("\nPress Enter to continue...")
    
    def _download_both(self):
        print("\n📥 Downloading BOTH files...")
        print("\n1. Downloading geosite.dat...")
        geosite_ok = self.downloader.download_geosite()
        if not geosite_ok:
            geosite_ok = self.downloader.download_geosite(use_mirror=True)
        
        print("\n2. Downloading geoip.dat...")
        geoip_ok = self.downloader.download_geoip()
        if not geoip_ok:
            geoip_ok = self.downloader.download_geoip(use_mirror=True)
        
        if geosite_ok:
            self.geosite_manager.reload()
            print("\n✅ geosite.dat downloaded and reloaded.")
        if geoip_ok:
            print("✅ geoip.dat downloaded.")
            
        if geosite_ok or geoip_ok:
            print("\n✅ Download completed!")
        else:
            print("\n❌ All downloads failed!")
        input("\nPress Enter to continue...")
    
    def _show_status(self):
        self.menu_manager.show_geo_status_header()
        
        geosite_exists = os.path.exists("geosite.dat")
        geoip_exists = os.path.exists("geoip.dat")
        
        print(f"\ngeosite.dat: {'✅ EXISTS' if geosite_exists else '❌ MISSING'}")
        if geosite_exists:
            size = os.path.getsize("geosite.dat")
            print(f"  Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        
        print(f"\ngeoip.dat:   {'✅ EXISTS' if geoip_exists else '❌ MISSING'}")
        if geoip_exists:
            size = os.path.getsize("geoip.dat")
            print(f"  Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        
        print("\n" + "="*60)
        print("RECOMMENDATION:")
        if not geosite_exists:
            print("  - geosite.dat is missing. Download it for full geosite support.")
        if not geoip_exists:
            print("  - geoip.dat is missing. Download it for geoip features.")
        if geosite_exists and geoip_exists:
            print("  - All files are present. You're ready to go!")
        input("\nPress Enter to continue...")