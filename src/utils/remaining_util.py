import time
import sys


class ProgressTracker:
    def __init__(self, total_items, description="Processing"):
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = time.time()
        self.description = description

    def update(self, items_processed=1):
        self.processed_items += items_processed
        self.display_progress()

    def display_progress(self):
        elapsed_time = time.time() - self.start_time
        if self.processed_items > 0:
            if elapsed_time > 0:
                items_per_second = self.processed_items / elapsed_time
                remaining_items = self.total_items - self.processed_items
                if items_per_second > 0:
                    estimated_remaining_time = remaining_items / items_per_second
                    minutes = int(estimated_remaining_time // 60)
                    seconds = int(estimated_remaining_time % 60)
                    remaining_time_str = f"{minutes:02}:{seconds:02}"
                else:
                    remaining_time_str = "Calculating..."
            else:
                remaining_time_str = "Calculating..."
        else:
            remaining_time_str = "Calculating..."

        progress_percent = (
            (self.processed_items / self.total_items) * 100
            if self.total_items > 0
            else 0
        )
        progress_str = f"{self.description}: {progress_percent:.2f}% | {self.processed_items}/{self.total_items} | Remaining: {remaining_time_str}"
        sys.stdout.write("\r" + progress_str)
        sys.stdout.flush()

    def finish(self):
        self.display_progress()
        print()
