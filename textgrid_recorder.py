import json
import datetime
import os

import textgrid
from praatio import tgio
import argparse

from global_defs import TimeZone


class TextGridRecorder(object) :
    def __init__(self) :
        pass

    @staticmethod
    def find_textgrid(data_dir) :
            textgrid_files = []  
            for (dirpath, _, filenames) in os.walk(data_dir):  
                for filename in filenames:  
                    if filename.endswith('.textgrid') or filename.endswith('.TextGrid'):  
                        filename_path = os.sep.join([dirpath, filename])  
                        textgrid_files.append(filename_path) 
            return textgrid_files

    @staticmethod
    def write_textgrid(file_path, time_zones,  tier_name = 'clipped') :
        tg = textgrid.TextGrid()
        tier = textgrid.IntervalTier(tier_name)
        for i, time_zone in enumerate(time_zones) :
            tier.add(time_zone.start, time_zone.end, str(i))
        tg.append(tier)
        tg.write(file_path)

    @staticmethod
    def read_textgrid(file_path) :
        tg = textgrid.TextGrid()
        try:
            tg.read(file_path)
        except :
            # return None
            tg = tgio.openTextgrid(file_path)
            if len(tg.tierDict["Keyword"].entryList) < 1 :
                intervals = [TimeZone(0,  tg.tierDict["Keyword"].maxTimestamp)]
                return intervals, "kws"

            intervals = []
            latest_end = 0
            max_time =  tg.tierDict["Keyword"].maxTimestamp
            for entry in tg.tierDict["Keyword"].entryList :
                start =  entry.start
                end =  entry.end
                end = min(end, max_time - 0.001)
                intervals.extend([TimeZone(latest_end, start), TimeZone(start, end)])
                latest_end = end

            intervals.append(TimeZone(latest_end, max_time))

            return intervals, "kws"
        intervals = []
        for item in tg.tiers[0] :
            #convert to ms
            interval = TimeZone(float(item.minTime), float(item.maxTime))
            intervals.append(interval)

        return intervals, tg.tiers[0].name

if __name__ == "__main__":
     input_time_zones = [TimeZone(0, 2.0), TimeZone(2.0, 4.0)]
     TextGridRecorder.write_textgrid('test.textgrid', input_time_zones)
     output_time_zones = TextGridRecorder.read_textgrid('test.textgrid')
     assert(len(output_time_zones) == len(input_time_zones))
     for input_time_zone , output_time_zone in zip(input_time_zones, output_time_zones) :
        assert(input_time_zone.start == output_time_zone.start and input_time_zone.end == output_time_zone.end)
