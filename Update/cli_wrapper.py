#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Wrapper for AIO Tool - Subprocess Integration
Provides command line interface for VCPMC Tool integration
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add core to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from ScraperChecker import run_scraper, run_checker, run_downloader
from enricher import enrich


def progress_callback(done: int, total: int):
    """Progress callback for subprocess communication"""
    print(f"PROGRESS:{done},{total}", flush=True)


def log_callback(message: str, prefix: str = ""):
    """Log callback for subprocess communication"""
    full_msg = f"[{prefix}] {message}" if prefix else message
    print(f"LOG:{full_msg}", flush=True)


def detail_callback(data: dict):
    """Detail progress callback for downloads"""
    print(f"DETAIL:{json.dumps(data)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="AIO YouTube Tool CLI")
    parser.add_argument("--operation", required=True, 
                       choices=["scraper", "checker", "downloader", "enricher"],
                       help="Operation to perform")
    
    # Common arguments
    parser.add_argument("--output_dir", default="./output", help="Output directory")
    
    # Scraper arguments
    parser.add_argument("--channel", help="YouTube channel URL/ID/@handle")
    parser.add_argument("--limit", type=int, default=200, help="Video limit for scraper")
    parser.add_argument("--include_shorts", action="store_true", help="Include YouTube Shorts")
    
    # Checker arguments
    parser.add_argument("--file_path", help="Input file path for checker")
    parser.add_argument("--max_workers", type=int, default=4, help="Number of worker threads")
    
    # Downloader arguments
    parser.add_argument("--input_value", help="Input for downloader (ID/URL/file)")
    parser.add_argument("--quality", default="best", help="Video quality")
    parser.add_argument("--audio_only", action="store_true", help="Audio only download")
    parser.add_argument("--concurrent_frags", type=int, default=8, help="Concurrent fragments")
    parser.add_argument("--cookies_file", help="Cookies file path")
    parser.add_argument("--proxy", help="Proxy URL")
    parser.add_argument("--enable_aria2", action="store_true", help="Enable aria2c")
    parser.add_argument("--use_archive", action="store_true", default=True, help="Use download archive")
    
    # Enricher arguments
    parser.add_argument("--include_transcript", action="store_true", default=True, help="Include transcript")
    parser.add_argument("--out_excel", help="Output Excel file for enricher")
    
    args = parser.parse_args()
    
    try:
        if args.operation == "scraper":
            if not args.channel:
                print("ERROR:Missing channel parameter", file=sys.stderr)
                sys.exit(1)
                
            result = run_scraper(
                channel_input=args.channel,
                out_folder=args.output_dir,
                log_func=log_callback,
                progress_callback=progress_callback
            )
            
        elif args.operation == "checker":
            if not args.file_path:
                print("ERROR:Missing file_path parameter", file=sys.stderr)
                sys.exit(1)
                
            result = run_checker(
                fp=args.file_path,
                max_workers=args.max_workers,
                progress_callback=progress_callback,
                log_func=log_callback
            )
            
        elif args.operation == "downloader":
            if not args.input_value:
                print("ERROR:Missing input_value parameter", file=sys.stderr)
                sys.exit(1)
                
            result = run_downloader(
                input_value=args.input_value,
                out_folder=args.output_dir,
                quality=args.quality,
                audio_only=args.audio_only,
                max_workers=args.max_workers,
                concurrent_frags=args.concurrent_frags,
                cookies_file=args.cookies_file,
                proxy=args.proxy,
                progress_callback=progress_callback,
                detail_callback=detail_callback,
                log_func=log_callback,
                enable_aria2=args.enable_aria2,
                use_archive=args.use_archive
            )
            
        elif args.operation == "enricher":
            if not args.input_value:
                print("ERROR:Missing input_value parameter", file=sys.stderr)
                sys.exit(1)
                
            df, result = enrich(
                input_value=args.input_value,
                max_workers=args.max_workers,
                include_transcript=args.include_transcript,
                out_excel=args.out_excel,
                progress=progress_callback,
                log=log_callback
            )
            
        if result:
            print(f"SUCCESS:{result}", flush=True)
        else:
            print("SUCCESS:Operation completed", flush=True)
            
    except Exception as e:
        print(f"ERROR:{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()