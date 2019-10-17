import logging
import os
from abc import ABC, abstractmethod

import numpy as np
from corpus_reader import CorpusReader


class LabelParser(ABC) :
  def __init__(self, next_parser = None):
    self.next_parser_ = next_parser
    self.split_token_ ='_' 

  def parse_text(self, raw_text):
    i = raw_text.find(self.split_token_)
    if i != -1 :
      result_dict = self._parse(raw_text[:i])
      if self.next_parser_:
        result_dict.update(self.next_parser_.parse_text( raw_text[i+1:]))
      return result_dict
    else:
      return self._parse(raw_text)
      
  @abstractmethod
  def _parse(self, raw_label):
    pass

class OriginalLabelParser(LabelParser) :
  def __init__(self, next_parser = None):
    super().__init__(next_parser)


  def _parse(self, raw_label):
    return {"Original":raw_label}


class DetectedLabelParser(LabelParser) :
  def __init__(self, next_parser = None):
    super().__init__(next_parser)
    self.next_parser_ = next_parser

  def _parse(self, raw_label):
    return {"Detected":raw_label}


class FilePathParser(LabelParser) :
  def __init__(self, next_parser = None):
    super().__init__(next_parser)
    self.split_token_ ='@' 


  def _parse(self, raw_label):
    return {"FilePath":raw_label}

class WavDataReader(CorpusReader): 

  def __init__(self, wanted_words = None):
    super().__init__(wanted_words)
    self.label_parser = OriginalLabelParser(
                          DetectedLabelParser(
                         FilePathParser() ))



  def parse_dir(self, data_dir): 
    wav_paths = self.find_wavs(data_dir) 

    wav_labels = []
    for file_path in wav_paths :
      parsed_label = self.parse_label(file_path)
      wav_labels.append(parsed_label['Detected'])

    return wav_paths,  wav_labels

  def parse_label(self, filepath):
    root, _ = os.path.splitext(os.path.basename(filepath))
    label = self.label_parser.parse_text(root)
    return label

