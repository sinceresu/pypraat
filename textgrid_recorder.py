import json
import datetime
import os

import textgrid
# from praatio import tgio

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

    def write_textgrid(self,  file_path, time_zones) :
        tg = textgrid.TextGrid()
        tier = textgrid.IntervalTier('kws')
        for i, time_zone in enumerate(time_zones) :
            tier.add(time_zone.start, time_zone.end, str(i))
        tg.append(tier)
        tg.write(file_path)

    def read_textgrid(self,  file_path) :
        tg = textgrid.TextGrid()
        try:
            tg.read(file_path)
        except :
            return None
            # tg = tgio.openTextgrid(file_path)
            # if len(tg.tierDict["Keyword"].entryList) != 1 :
            #     return [(0,  tg.tierDict["Keyword"].maxTimestamp * 1000)]
            # start =  int(tg.tierDict["Keyword"].entryList[0].start* 1000)
            # end =  int(tg.tierDict["Keyword"].entryList[0].end * 1000)

            # return [(0, start), (start, end), (end, tg.tierDict["Keyword"].maxTimestamp * 1000)]
        intervals = []
        for item in tg.tiers[0] :
            #convert to ms
            interval = TimeZone(float(item.minTime), float(item.maxTime))
            intervals.append(interval)

        return intervals

if __name__ == "__main__":
     recorder = TextGridRecorder()
     input_time_zones = [TimeZone(0, 2.0), TimeZone(2.0, 4.0)]
     recorder.write_textgrid('test.textgrid', input_time_zones)
     output_time_zones = recorder.read_textgrid('test.textgrid')
     assert(len(output_time_zones) == len(input_time_zones))
     for input_time_zone , output_time_zone in zip(input_time_zones, output_time_zones) :
        assert(input_time_zone.start == output_time_zone.start and input_time_zone.end == output_time_zone.end)