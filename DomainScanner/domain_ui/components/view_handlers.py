from ..menu_manager import MenuManager
from ..paginated_view import PaginatedView


class ViewHandlers:
    """Handle view operations (live list, archive, search)"""
    
    def __init__(self, storage):
        self.storage = storage
        self.menu_manager = MenuManager()
        self.paginator = PaginatedView()
    
    def show_live_list(self):
        """Show live domains list"""
        live_domains = self.storage.read_live()
        self.paginator.show(live_domains, "LIVE DOMAINS LIST")
    
    def show_archive(self):
        """Show archive view"""
        entries = self.storage.read_archive()
        if not entries:
            self.paginator.show([], "ARCHIVE DATA")
        else:
            formatted = [f"{e[0]} | IP:{e[1] if len(e)>1 else 'N/A'} | Status:{e[2] if len(e)>2 else 'N/A'} | Time:{e[4] if len(e)>4 else 'N/A'}" 
                        for e in entries]
            self.paginator.show(formatted, "ARCHIVE DATA")
    
    def search_archive(self):
        """Search archive for domain"""
        self.menu_manager.show_archive_search_header()
        s = input("\nEnter domain name to search: ").strip()
        if s:
            res = self.storage.search_archive(s)
            self.menu_manager.show_search_results(s, res)
        input("\n\nPress Enter to continue...")