import logging
import os
import time
import xml.etree.ElementTree as ET

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import run
import util
from djxml import XmlDictConfig


def process_file(event):
    time.sleep(5)
    run.process_xml_bod_file(event.src_path)


def on_deleted(event):
    print(f"Someone deleted {event.src_path}!")

def on_modified(event):
    run.process_xml_bod_file(event.src_path)
    print(f"{event.src_path} has been modified")

def on_moved(event):
    print(f"{event.src_path} was moved to {event.dest_path}")
    

if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = False
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = process_file
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
                            
    #path = sys.argv[1] if len(sys.argv) > 1 else '.'

    #event_handler = LoggingEventHandler()

    observer = Observer()
    observer.schedule(my_event_handler, util.get_incoming_read(), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
    
