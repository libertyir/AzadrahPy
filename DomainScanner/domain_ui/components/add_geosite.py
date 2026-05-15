import os
from ..menu_manager import MenuManager


class GeositeAdder:
    """Handle adding domains from geosite.dat"""
    
    def __init__(self, geosite_manager, storage):
        self.geosite_manager = geosite_manager
        self.storage = storage
        self.menu_manager = MenuManager()
    
    def add(self):
        """Add domains from geosite.dat using a tag"""
        self.menu_manager.show_add_from_geosite_header()
        
        if not os.path.exists("geosite.dat"):
            print("\n[NOTE] geosite.dat not found in current directory!")
            print("Using built-in domain lists for common services.")
            print("\nYou can download geosite.dat from menu option 11.\n")
        else:
            print("\n[OK] geosite.dat found. Will load on first use.\n")
        
        self.menu_manager.show_common_tags()
        
        tag = input("Enter geosite tag (e.g., 'google', 'facebook'): ").strip()
        if not tag:
            print("No tag entered!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n[INFO] Extracting domains for geosite:{tag}...")
        domains = self.geosite_manager.extract_domains_by_geosite(tag)
        
        if not domains:
            print(f"[ERROR] No domains found for tag '{tag}'")
            input("\nPress Enter to continue...")
            return
        
        self.menu_manager.show_domains_preview(tag, domains)
        
        choice = self.menu_manager.get_add_options_choice()
        
        if choice == '1':
            added = self.storage.add_domains_batch(domains)
            print(f"\n[OK] Added {added} new domains to domains.txt")
        elif choice == '2':
            filtered = [d for d in domains if d.endswith('.com')]
            added = self.storage.add_domains_batch(filtered)
            print(f"\n[OK] Added {added} .com domains to domains.txt")
        elif choice == '3':
            filtered = [d for d in domains if d.endswith('.net')]
            added = self.storage.add_domains_batch(filtered)
            print(f"\n[OK] Added {added} .net domains to domains.txt")
        elif choice == '4':
            filtered = [d for d in domains if d.endswith('.org')]
            added = self.storage.add_domains_batch(filtered)
            print(f"\n[OK] Added {added} .org domains to domains.txt")
        elif choice == '5':
            self._filter_by_keyword(domains)
        else:
            print("Cancelled.")
        
        input("\nPress Enter to continue...")
    
    def _filter_by_keyword(self, domains):
        keyword = input("Enter keyword to filter: ").strip()
        if keyword:
            filtered = [d for d in domains if keyword.lower() in d.lower()]
            print(f"\nFound {len(filtered)} domains containing '{keyword}'")
            if filtered:
                for i, d in enumerate(filtered[:10]):
                    print(f"  {i+1}. {d}")
                if len(filtered) > 10:
                    print(f"  ... and {len(filtered)-10} more")
                
                choice2 = input("\nAdd these domains? (y/n): ").strip().lower()
                if choice2 == 'y':
                    added = self.storage.add_domains_batch(filtered)
                    print(f"\n[OK] Added {added} domains to domains.txt")
                else:
                    print("Cancelled.")
            else:
                print("No domains match the keyword.")
        else:
            print("No keyword entered.")