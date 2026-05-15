from ..menu_manager import MenuManager


class DomainManager:
    """Handle domain management operations (add, sort, etc.)"""
    
    def __init__(self, storage):
        self.storage = storage
        self.menu_manager = MenuManager()
    
    def add_domain(self):
        """Add single domain or multiple domains"""
        self.menu_manager.show_add_domain_header()
        d = input("Enter domain name (e.g., example.com): ").strip()
        if d:
            if ',' in d:
                domains_list = [i.strip() for i in d.split(',')]
                added = self.storage.add_domains_batch(domains_list)
                print(f"\n[OK] Added {added} new domains")
            else:
                if self.storage.add_domain(d):
                    print(f"\n[OK] Domain '{d}' added successfully!")
                else:
                    print(f"\n[ERROR] Invalid or duplicate domain: {d}")
        else:
            print("\nNo domain entered.")
        input("\nPress Enter to continue...")
    
    def sort_live(self):
        """Sort live domains list"""
        self.storage.sort_live()
        print("\n[OK] IsLive.txt sorted successfully!")
        input("\nPress Enter to continue...")
    
    def sort_domains(self):
        """Sort domains.txt file"""
        self.storage.sort_domains()
        print("\n[OK] domains.txt sorted and deduplicated successfully!")
        input("\nPress Enter to continue...")
    
    def sort_archive(self):
        """Sort archive.csv file"""
        self.storage.sort_archive()
        print("\n[OK] Archive sorted successfully!")
        input("\nPress Enter to continue...")