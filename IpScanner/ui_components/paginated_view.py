#!/usr/bin/env python3
"""Paginated View - Handles paginated display with keyboard navigation"""

import sys
import platform
from typing import List


class PaginatedView:
    """Handles paginated display of lists with keyboard navigation"""
    
    def show(self, items: List[str], title: str, items_per_page: int = 10):
        """Display paginated list with keyboard navigation"""
        if not items:
            print(f"\n{title}: No items to display.")
            input("\nPress Enter to continue...")
            return
        
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        current_page = 1
        
        controls = """
    Controls:
    ← (Left Arrow)  - Previous page
    → (Right Arrow) - Next page
    Home            - First page
    End             - Last page
    Esc             - Exit
    """
        
        while True:
            self._clear_screen()
            print(f"\n{'='*60}")
            print(f"{title} - Page {current_page}/{total_pages}")
            print(f"{'='*60}\n")
            
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(items))
            
            for i in range(start_idx, end_idx):
                print(f"{i+1}. {items[i]}")
            
            print(controls)
            
            # Get keyboard input
            if not self._handle_navigation_input(current_page, total_pages):
                break
            
            # Update page based on key (handled in _handle_navigation_input)
            # Simplified: we'll re-implement navigation here
            key = self._get_key()
            
            if key == 'left' and current_page > 1:
                current_page -= 1
            elif key == 'right' and current_page < total_pages:
                current_page += 1
            elif key == 'home':
                current_page = 1
            elif key == 'end':
                current_page = total_pages
            elif key == 'esc':
                break
    
    def _clear_screen(self):
        """Clear terminal screen"""
        if platform.system() == "Windows":
            import os
            os.system('cls')
        else:
            import os
            os.system('clear')
    
    def _get_key(self):
        """Get keyboard input and return key type"""
        if platform.system() == "Windows":
            import msvcrt
            key = msvcrt.getch()
            
            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'K':
                    return 'left'
                elif key == b'M':
                    return 'right'
                elif key == b'G':
                    return 'home'
                elif key == b'O':
                    return 'end'
            elif key == b'\x1b':
                return 'esc'
            return None
        else:
            import termios
            import tty
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                
                if key == '\x1b':
                    next_key = sys.stdin.read(1)
                    if next_key == '[':
                        final_key = sys.stdin.read(1)
                        if final_key == 'D':
                            return 'left'
                        elif final_key == 'C':
                            return 'right'
                        elif final_key == 'H':
                            return 'home'
                        elif final_key == 'F':
                            return 'end'
                elif key == '\x1b':
                    return 'esc'
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _handle_navigation_input(self, current_page: int, total_pages: int) -> bool:
        """Handle navigation input, return False to exit"""
        # This is a placeholder - actual navigation is in show() method
        return True