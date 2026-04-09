"""
Video Clip Processor Module

This module provides functionality to process video clips sequentially,
ensuring each clip is only edited once with thread-safe tracking.
"""

import os
import threading
from pathlib import Path
from typing import Callable, Optional, Set
import json


class VideoClipProcessor:
    """
    Processes video clips from a folder sequentially with tracking to avoid re-editing.
    """
    
    def __init__(self, 
                 input_folder: str,
                 output_folder: str,
                 processed_file: str = "processed_clips.json"):
        """
        Initialize the video clip processor.
        
        Args:
            input_folder: Path to folder containing video clips
            output_folder: Path to folder for processed clips
            processed_file: JSON file to track processed clips
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.processed_file = Path(processed_file)
        self.processed_clips: Set[str] = self._load_processed_clips()
        self.lock = threading.Lock()
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def _load_processed_clips(self) -> Set[str]:
        """Load the set of previously processed clips from JSON file."""
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r') as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load processed clips file. Starting fresh.")
                return set()
        return set()
    
    def _save_processed_clips(self):
        """Save the set of processed clips to JSON file."""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_clips), f, indent=2)
    
    def _get_clip_identifier(self, clip_path: Path) -> str:
        """
        Generate a unique identifier for a video clip.
        Uses file path and modification time for uniqueness.
        """
        stat = clip_path.stat()
        return f"{clip_path.name}_{stat.st_mtime}"
    
    def is_processed(self, clip_path: Path) -> bool:
        """Check if a clip has already been processed."""
        identifier = self._get_clip_identifier(clip_path)
        with self.lock:
            return identifier in self.processed_clips
    
    def mark_as_processed(self, clip_path: Path):
        """Mark a clip as processed."""
        identifier = self._get_clip_identifier(clip_path)
        with self.lock:
            self.processed_clips.add(identifier)
            self._save_processed_clips()
    
    def get_unprocessed_clips(self, extensions: tuple = ('.mp4', '.avi', '.mkv', '.mov', '.wmv')) -> list[Path]:
        """
        Get list of unprocessed video clips from input folder.
        
        Args:
            extensions: Tuple of valid video file extensions
            
        Returns:
            List of Path objects for unprocessed clips
        """
        if not self.input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")
        
        all_clips = []
        for ext in extensions:
            all_clips.extend(self.input_folder.glob(f"*{ext}"))
        
        unprocessed = [clip for clip in all_clips if not self.is_processed(clip)]
        return sorted(unprocessed)
    
    def process_clips(self, 
                     process_function: Callable[[Path, Path], bool],
                     progress_callback: Optional[Callable[[str, int, int], None]] = None):
        """
        Process all unprocessed clips sequentially.
        
        Args:
            process_function: Function that takes (input_path, output_path) and returns True on success
            progress_callback: Optional callback function with signature (message, current, total)
        """
        unprocessed_clips = self.get_unprocessed_clips()
        total = len(unprocessed_clips)
        
        if total == 0:
            print("No unprocessed clips found.")
            return
        
        print(f"Found {total} unprocessed clip(s) to process.")
        
        for idx, clip_path in enumerate(unprocessed_clips, 1):
            clip_name = clip_path.name
            
            # Progress callback
            if progress_callback:
                progress_callback(f"Processing {clip_name}", idx, total)
            else:
                print(f"[{idx}/{total}] Processing {clip_name}...")
            
            # Define output path
            output_path = self.output_folder / f"processed_{clip_name}"
            
            try:
                # Process the clip
                success = process_function(clip_path, output_path)
                
                if success:
                    # Mark as processed only on success
                    self.mark_as_processed(clip_path)
                    
                    if progress_callback:
                        progress_callback(f"Completed {clip_name}", idx, total)
                    else:
                        print(f"[{idx}/{total}] Completed {clip_name}")
                else:
                    print(f"[{idx}/{total}] Failed to process {clip_name}")
                    
            except Exception as e:
                print(f"[{idx}/{total}] Error processing {clip_name}: {e}")
                continue
        
        print(f"Processing complete. Processed {len([c for c in unprocessed_clips if self.is_processed(c)])}/{total} clip(s).")
    
    def move_processed_clips(self, destination_folder: Optional[str] = None):
        """
        Move processed clips to a different folder to avoid re-processing.
        
        Args:
            destination_folder: Folder to move processed clips to. If None, creates a 'processed' subfolder.
        """
        if destination_folder is None:
            destination_folder = self.input_folder / "processed"
        else:
            destination_folder = Path(destination_folder)
        
        destination_folder.mkdir(parents=True, exist_ok=True)
        
        moved_count = 0
        for clip_path in self.input_folder.glob("*"):
            if clip_path.is_file() and self.is_processed(clip_path):
                try:
                    destination = destination_folder / clip_path.name
                    clip_path.rename(destination)
                    moved_count += 1
                    print(f"Moved {clip_path.name} to processed folder")
                except Exception as e:
                    print(f"Failed to move {clip_path.name}: {e}")
        
        print(f"Moved {moved_count} processed clip(s) to {destination_folder}")
    
    def reset_tracking(self):
        """Reset the tracking of processed clips. Use with caution."""
        with self.lock:
            self.processed_clips.clear()
            if self.processed_file.exists():
                self.processed_file.unlink()
            print("Processed clips tracking has been reset.")


# Example usage and test function
if __name__ == "__main__":
    def example_process_function(input_path: Path, output_path: Path) -> bool:
        """Example processing function - replace with actual video processing logic."""
        print(f"  Would process: {input_path} -> {output_path}")
        # Simulate processing
        # In real usage, this would call your actual video editing function
        # return your_actual_edit_function(input_path, output_path)
        return True
    
    def example_progress_callback(message: str, current: int, total: int):
        """Example progress callback."""
        print(f"Progress: {message} ({current}/{total})")
    
    # Example configuration
    processor = VideoClipProcessor(
        input_folder="input_videos",
        output_folder="output_videos",
        processed_file="processed_clips.json"
    )
    
    # Process clips
    processor.process_clips(
        process_function=example_process_function,
        progress_callback=example_progress_callback
    )
    
    # Optionally move processed clips
    # processor.move_processed_clips()
