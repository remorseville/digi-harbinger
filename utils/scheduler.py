import asyncio
import threading
from datetime import datetime, timedelta
import logging
import pytest
import os
import sys
import shutil
from functools import partial
from conftest import process_defined_tests 




class AsyncTestScheduler:
    def __init__(self):
        self._running = False
        self._current_iteration = 0
        self._selected_tests = None
        self._interval = 0
        self._repetitions = 0
        self._task = None
        self._file_name = ""
        self._next_run_time = 0
        self._countdown = 0
        self._loop = asyncio.new_event_loop()
        self.logger = logging.getLogger(__name__)

    def resource_path(self, relative_path):           # Dynamic path handling for file references (prod vs dev)
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        
    async def schedule_tests(self, selected_tests, interval_min, repetitions):
        """Start the test scheduler with pytest-asyncio support"""
        if self._running:
            self.logger.warning("Scheduler already running")
            return False

        self._selected_tests = selected_tests
        self._interval = interval_min
        self._repetitions = repetitions
        self._running = True
        self._current_iteration = 0
        self._next_run_time = datetime.now()
        self._countdown = self._interval * 60
        # Run in background thread to avoid blocking
        threading.Thread(
            target=self._start_async_loop,
            daemon=True
        ).start()
        
        return True

    def _start_async_loop(self):
        """Run the asyncio loop in a separate thread"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._run_test_cycle())

    async def _run_test_cycle(self):
        """Main test execution loop"""
        while self._running and self._current_iteration < self._repetitions:
            self._current_iteration += 1
            self.logger.info(f"Test cycle {self._current_iteration}/{self._repetitions}")
            print(self._selected_tests)
            print(self._next_run_time)
            
            
            try:
                # Create partial function with current test selection
                self._countdown = self._interval * 60 + 5
                self._next_run_time = self._next_run_time + timedelta(
                    minutes=self._interval
                )

                test_runner = partial(
                    process_defined_tests,
                    selected_tests=self._selected_tests
                )

                
                
                #self._countdown = self._countdown - 1
                
                # Run the pytest async tests
                await test_runner()
                now = datetime.now()                                        # Date/time handling for report filenames - appends to "report_****.html"
                formatted_time = now.strftime("%Y%m%d%H%M%S")
                source = self.resource_path('./templates/report.html')

                destination = self.resource_path(f'./templates/reports/CIS_report_{formatted_time}.html')  # Custom report titles
                self._file_name = f"CIS_report_{formatted_time}"

                try:
                    os.makedirs(os.path.dirname(destination), exist_ok=True)    # creates the "Templates/reports" directory  
                    shutil.copy2(source, destination)                           # copies generated "Report.Html" to "Templates/reports"
                    print(f"File copied from {source} to {destination}")
                except FileNotFoundError:
                    print(f"Source file {source} not found.")
                except PermissionError:
                    print(f"Permission denied for {destination}.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                
            except Exception as e:
                self.logger.error(f"Test cycle failed: {str(e)}")

            # Wait for interval unless we're done
            if self._running and self._current_iteration < self._repetitions:
                await asyncio.sleep(self._interval * 60)
                
        self.stop()

    def stop(self):
        """Stop the scheduler and clean up"""
        self._running = False
        if hasattr(self, '_loop') and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self.logger.info("Test scheduler stopped")

    def get_status(self):
        """Return current scheduler status"""
        next_run = None
        if self._running:
            next_run = datetime.now() + timedelta(
                minutes=self._interval
            )
            self._countdown = round((self._next_run_time - datetime.now()).total_seconds())
            
        
        
        
        
        return {
            "running": self._running,
            "current_iteration": self._current_iteration,
            "total_iterations": self._repetitions,
            "next_run": self._countdown if next_run else None,
            "next_run_time" : self._next_run_time.isoformat() if next_run else None,
            "countdown" : self._countdown, 
            "interval" : self._interval, 
        }
    
    def get_file_name(self):
        return self._file_name