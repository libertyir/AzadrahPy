import sys
import threading
import time
from ..scan_controller import ScanController
from ..menu_manager import MenuManager
from domain_parser import DomainValidator


class ScanRunner:
    """Handle domain scanning execution"""
    
    def __init__(self, storage, geosite_manager, scanner_class):
        self.storage = storage
        self.geosite_manager = geosite_manager
        self.scanner_class = scanner_class
        self.scan_controller = ScanController()
        self.menu_manager = MenuManager()
        self.scanner = None
        self.scan_thread = None
    
    def run(self, force: bool = False):
        """Run domain scan with interactive control"""
        raw_lines = self.storage.load_domains_raw()
        if not raw_lines:
            print("\n[ERROR] No domains found in domains.txt!")
            input("\nPress Enter to continue...")
            return
        
        domains_to_scan = self._prepare_domains(raw_lines, force)
        
        if not domains_to_scan:
            print("\n[INFO] No new domains to scan!")
            input("\nPress Enter to continue...")
            return
        
        timeout, workers = self.scan_controller.get_scan_config()
        
        self.scanner = self.scanner_class(timeout=timeout, max_workers=workers)
        
        self._print_scan_header(workers, timeout, len(domains_to_scan), force)
        
        last_live_count = [0]
        last_dead_count = [0]
        
        def update_progress(processed, total):
            if total > 0:
                percent = (processed / total) * 100
                print(f"\r[PROGRESS] {processed}/{total} ({percent:.1f}%) | Live: {last_live_count[0]} | Dead: {last_dead_count[0]}", end="", flush=True)
        
        def save_domain_result(result):
            self.storage.save_result(result)
            if result.get("accessible", False):
                last_live_count[0] += 1
                print(f"\n✓ LIVE: {result['domain']}")
                sys.stdout.flush()
            else:
                last_dead_count[0] += 1
        
        self.scanner.set_callbacks(progress_callback=update_progress, domain_callback=save_domain_result)
        
        self._start_scan_thread(domains_to_scan, force)
        self._wait_for_completion()
        
        self.storage.flush()
        
        self._print_scan_summary(last_live_count[0], last_dead_count[0])
    
    def _prepare_domains(self, raw_lines, force):
        """Expand geosite tags and prepare domain list"""
        validator = DomainValidator()
        is_debug = hasattr(sys, 'gettrace') and sys.gettrace() is not None
        
        all_domains = []
        
        print("\n[PREPARE] Expanding geosite tags...")
        sys.stdout.flush()
        
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            
            if line.lower().startswith('geosite:'):
                tag = line[8:].strip()
                if not is_debug:
                    print(f"  Expanding geosite:{tag}...")
                    sys.stdout.flush()
                domains = self.geosite_manager.extract_domains_by_geosite(tag, silent=is_debug)
                if domains:
                    all_domains.extend(domains)
            else:
                all_domains.append(line)
        
        valid_domains = [d for d in all_domains if validator.is_valid(d)]
        
        unique_domains = []
        seen = set()
        for d in valid_domains:
            if d not in seen:
                seen.add(d)
                unique_domains.append(d)
        
        previous_checked = self.storage.load_previous() if not force else set()
        
        if not force and previous_checked:
            return [d for d in unique_domains if d not in previous_checked]
        return unique_domains
    
    def _print_scan_header(self, workers, timeout, total, force):
        print("\n" + "="*60)
        print(f"Domains to scan: {total}")
        print("="*60)
        print("\n" + "="*60)
        print("SCANNING IN PROGRESS")
        print("="*60)
        print(f"Threads: {workers}")
        print(f"Timeout: {timeout}s")
        print(f"Force Update: {force}")
        print("\nControls: P=Pause, R=Resume, S=Stop")
        print("-" * 40)
        print()
        sys.stdout.flush()
    
    def _start_scan_thread(self, domains, force):
        previous_checked = self.storage.load_previous() if not force else set()
        
        self.scan_thread = threading.Thread(
            target=self.scanner.start_scan,
            args=(domains, force, previous_checked)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def _wait_for_completion(self):
        while self.scan_thread.is_alive():
            key = self.scan_controller.get_key()
            if key:
                if key == 'p':
                    self.scanner.pause()
                    print("\n[PAUSED]")
                    sys.stdout.flush()
                elif key == 'r':
                    self.scanner.resume()
                    print("\n[RESUMED]")
                    sys.stdout.flush()
                elif key == 's':
                    self.scanner.stop()
                    print("\n[STOPPED]")
                    sys.stdout.flush()
                    break
            time.sleep(0.05)
    
    def _print_scan_summary(self, live_count, dead_count):
        print("\n\n" + "="*60)
        print("SCAN COMPLETED!")
        print("="*60)
        print(f"Total checked: {self.scanner.processed_count}")
        print(f"Live domains: {live_count}")
        print(f"Dead domains: {dead_count}")
        sys.stdout.flush()
        input("\nPress Enter to continue...")