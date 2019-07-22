#!/usr/bin/python
import sys
import time
import os
import random
import subprocess
import logging
from shutil import copyfile, move
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

INPUT_PATH = '/data/input'
PROCESSING_PATH = '/data/processing'
OUTPUT_PATH = '/data/output'
TOOL_PATH = '/tool/NEEL_Linking.jar'
KB_PATH = '/kb'

class FileWatcherHandler(PatternMatchingEventHandler):
  def __init__(self, inpath, procpath, outpath, toolpath, kbpath):
    super(FileWatcherHandler, self).__init__(ignore_directories=True, ignore_patterns=['*.tmp'])
    self.inpath = inpath
    self.procpath = procpath
    self.outpath = outpath
    self.toolpath = toolpath
    self.kbpath = kbpath

  def process(self, src_path):
    filename = os.path.basename(src_path)
    tmpfile = os.path.join(self.procpath, filename)
    outfile = os.path.join(self.outpath, filename)
    
    logging.info("Processing: {0}".format(src_path))
    subprocess.call(['java', '-jar', self.toolpath, src_path, self.kbpath, tmpfile])
    
    if os.path.exists(tmpfile):
      move(tmpfile, outfile)
      try:
        os.remove(src_path)
      except OSError:
        logging.error("Can't delete input file %s" % src_path)

      logging.info("Processing of %s completed, output file available at: %s" % (filename, outfile))

  def process_existing_files(self):
    for src_path in os.listdir(self.inpath):
      path = os.path.join(self.inpath, src_path)
      if not os.path.isdir(path):
        self.process(path)

  def on_created(self, event):
    self.process(event.src_path)
  
  def on_moved(self, event):
    self.process(event.dest_path)

def make_directories():
  for folder in [INPUT_PATH, PROCESSING_PATH, OUTPUT_PATH]:
    if not os.path.exists(folder):
      os.mkdir(folder)

if __name__ == "__main__":
  logging.info("NEL tool started")
  make_directories()
  
  event_handler = FileWatcherHandler(INPUT_PATH, PROCESSING_PATH, OUTPUT_PATH, TOOL_PATH, KB_PATH)
  event_handler.process_existing_files()

  logging.info("Waiting for input files into: %s" % INPUT_PATH)
  
  observer = Observer()
  observer.schedule(event_handler, INPUT_PATH, recursive=False)
  observer.start()
  
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  
  observer.join()