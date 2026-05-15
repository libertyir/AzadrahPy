#!/usr/bin/env python3
"""Paginated View for Domain Scanner"""

import platform
import os
from typing import List


class PaginatedView:
    """Handles paginated display of lists with keyboard navigation"""
    
    def show(self, items: List[str], title: str, items_per_page: int = 15):
        """Display paginated list with keyboard navigation"""
        if not items:
            print(f"\n{title}: No items to display.")
            input("\nPress Enter to continue...")
            return
        
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        current_page = 1
        
        while True:
            self._clear_screen()
            print(f"\n{'='*60}")
            print(f"{title} - Page {current_page}/{total_pages}")
            print(f"{'='*60}\n")
            
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(items))
            
            for i in range(start_idx, end_idx):
                print(f"{i+1}. {items[i]}")
            
            print("\n" + "-"*40)
            print("Commands: [N]ext | [P]rev | [H]ome | [E]nd | [Q]uit")
            
            cmd = input("\nCommand: ").strip().lower()
            
            if cmd == 'n' and current_page < total_pages:
                current_page += 1
            elif cmd == 'p' and current_page > 1:
                current_page -= 1
            elif cmd == 'h':
                current_page = 1
            elif cmd == 'e':
                current_page = total_pages
            elif cmd == 'q':
                break
    
    def _clear_screen(self):
        """Clear terminal screen"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')