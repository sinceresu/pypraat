#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' playingback & plotting recorded sensor data '

__author__ = 'Andy Su'

import json
import os
import re
import sys
from tkinter import *
from tkinter import filedialog, ttk

import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.io.wavfile as wav

from textgrid_recorder import TextGridRecorder

from plotter import Plotter


class FileItem() :
    def __init__(self,  file_path,  command = None  ) :
        self.file_path = file_path
        self.command = command
        self.base_file_name = os.path.basename(file_path)

class KeywordClip(object) : 
    statuses = [
        'clipped',
        'unclipped',
        ''
    ] 

    search_labels =[  'All' ] + statuses
    # keywords_to_id = {
    #     'xnxn': 0,
    #     'dddd':1,
    #     'unknown':2,
    # }
    config_file_name = "config.json"

    commands_file_name = "commands.csv"

    def __init__(self) :

        """
        main function
        """
        self.app_config = self.load_config()
        #read the data
        init_src_data_folder = self.app_config ['src_folder']

        self.play_obj  = None
        
        self.root=Tk()
        self.root.wm_title('keyword clip')

        screen_width, screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry('%dx%d+%d+%d' % (screen_width, screen_height, 0, 0))

        Button(self.root,text='open folder',command=self.on_select_src_folder, height = 2).grid(column=0, row=0, padx=20, pady=8)

        self.src_folder_ctrl = StringVar()
        self.src_folder_ctrl.set(init_src_data_folder)
        Label(self.root, textvariable=self.src_folder_ctrl).grid(column=1, row=0, padx=20, pady=8) 

        # Button(self.root,text='load',command=self.on_load,  width = 20,  height = 2).grid(column=2, row=0, padx=20, pady=8)


        self.plotter_ = Plotter( figure_size=((screen_width - 728)/100, (screen_height - 200)/100))

        # plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.plotter_.get_figure(), master=self.root)
        self.canvas.get_tk_widget().grid(column=0, columnspan=5, row=1)
        # self.canvas.draw() 

        self.canvas.mpl_connect('button_press_event', self.on_canvas_mouse_click)
        # self.canvas.mpl_connect('key_release_event', self.on_set_zone_pressed)

        self.tree = ttk.Treeview(self.root, show="headings",columns=("a", "b",  "c"))
        self.vbar = ttk.Scrollbar(self.root, orient=VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)

        self. tree.column("a", width=50, anchor="center", stretch=False)
        self. tree.column("b", width=50,  anchor="center")
        self. tree.column("c", width=400, anchor="center")
        self.tree.heading("a", text="ID")
        self.tree.heading("b", text="Status")
        self.tree.heading("c", text="File Name")
        self.tree["selectmode"] = "browse"       


        self.tree.grid(row=1, column=5, columnspan=4, sticky=NSEW)
        self.vbar.grid(row=1, column=9, sticky=NS)

        self.tree.bind("<<TreeviewSelect>>",  self.on_select_item)
        self.root.bind("<KeyPress-space>",  self.on_confirm_and_next)
        self.root.bind("<KeyPress-f>",  self.on_play)
        self.root.bind("<KeyPress-p>",  self.on_play)
        self.root.bind("<KeyPress-b>",  self.on_go_prev) 
        self.root.bind("<KeyPress-s>",  self.on_set_zone_pressed)
        self.root.bind("<Return>",  self.on_set_zone_pressed)
        self.root.bind("<Tab>",  self.on_play)
        self.root.bind("<Delete>",  self.on_delete_timezone)
        self.root.bind("<KeyPress-d>",  self.on_delete_timezone)
        self.root.bind("<KeyPress-r>",  self.on_revert)

        # self.root.bind("<Space>",  self.on_rename)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        
        # search ctrls
        Label(self.root,text='select status: ').grid(column=5, row=0, padx=20, pady=8)   
        self.detected_label_to_search = StringVar()
        detected_search_ctrl = ttk.Combobox(self.root, width=12, textvariable=self.detected_label_to_search, state='readonly')
        detected_search_ctrl['values'] = KeywordClip.search_labels
        detected_search_ctrl.grid(column=6, row=0, padx=20, pady=8) 
        detected_search_ctrl.current(0) 
        detected_search_ctrl.bind("<<ComboboxSelected>>",  self.on_status_search_selected)

        self.regex_str= StringVar()
        regex_ctrl = Entry(self.root, width=30, textvariable=self.regex_str)
        regex_ctrl.grid(column=7, row=0)
        regex_ctrl.bind('<Return>', self.on_regex_search)

        Button(self.root, text='search', command=self.on_regex_search, width = 10,).grid(column=8, row=0, padx=20, pady=8)
        # Button(self.root, text='reset', command=self.on_regex_reset, width = 10).grid(column=8, row=0, padx=20, pady=8)


        # rename ctrls
        Button(self.root, text='exit',  command=self.on_closing, width = 20,  height = 2).grid(column=0, row=2, padx=20, pady=30)

        Button(self.root, text='play',  command=self.on_play, width = 20,  height = 2).grid(column=1, row=2, padx=20, pady=30)

        Button(self.root, text='delete file',  command=self.on_delete_file, width = 20,  height = 2).grid(column=2, row=2, padx=20, pady=30)

        Button(self.root,text='confirm',command=self.on_confirm, width = 20,  height = 2).grid(column=3, row=2, padx=20, pady=30)
        
        # Button(self.root,text='rename',command=self.on_rename, width = 10,  height = 2).grid(column=4, row=4, padx=20, pady=8)


        Button(self.root,text='go to first',command=self.on_select_first, width = 10,  height = 2 ).grid(column=5, row=2, padx=20, pady=30)
        Button(self.root,text='go to last',command=self.on_select_last, width = 10,  height = 2).grid(column=6, row=2, padx=20, pady=30)
        
        # Button(self.root,text='prev',command=self.on_prev_item, width = 10,  height = 2 ).grid(column=7, row=4, padx=20, pady=8)
        # Button(self.root,text='next',command=self.on_next_item, width = 10,  height = 2).grid(column=8, row=4, padx=20, pady=8)
        self.process_progress = StringVar()
        self.process_progress.set('')
        Label(self.root, textvariable=self.process_progress).grid(column=7, row=2, columnspan = 3, pady=30)   
        for row in range(self.root.grid_size()[1]):
            self.root.grid_rowconfigure(row, minsize=60)
        if init_src_data_folder :
            self.load_dir(init_src_data_folder)

        self.tree.focus()
        self.progress_timer = None

    def update_selected_label(self):

        selected_file_id = self.get_selected_item()
        item_value = self.tree.item(str(selected_file_id),"values")
        new_item_value = (item_value[0],  item_value[1],  item_value[2])
        self. tree.item(str(selected_file_id), values=(new_item_value))

            
    def display_files(self, display_filter):
        for _ in map(self.tree.delete, self.tree.get_children("")):
            pass
        self.displayed_ids = []
        first_unprocessed_item_id = None
        first_unprocessed_file_id = None

        processed_items = 0
        item_id = 0
        for i in range(len(self.file_items)):
            if display_filter[i] :
                status = ''
                if self.file_items[i].command :
                    status = self.file_items[i].command['status']
                    processed_items  += 1
                else :
                    if first_unprocessed_item_id is None:
                        first_unprocessed_item_id = item_id
                        first_unprocessed_file_id = i

                self.tree.insert('', 'end', values=(item_id,  status,  self.file_items[i].base_file_name), iid=i)
                self.displayed_ids.append(i)
                item_id += 1
                
        if self.displayed_ids :
            self.tree.selection_set(self.displayed_ids[0])
            self.tree.focus(self.displayed_ids[0])

        self.total_items = len(self.displayed_ids)
        self.processed_items = processed_items
        self.first_unprocessed_item_id = first_unprocessed_item_id
        self.first_unprocessed_file_id = first_unprocessed_file_id

    def draw_wav_data(self, file_path, time_zones = None):
        fs, audio_data = wav.read(file_path)

        self.plotter_.plot(os.path.basename(file_path), audio_data, fs, time_zones)


    def on_status_search_selected(self, *args):
        status_seach_info= self.detected_label_to_search.get()
        #print(seach_info)
        display_filter = [True] * len( self.file_items)
        if (status_seach_info != 'All') :
            for i in range(len(self.file_items)):
                # pass
                status = self.file_items[i].command['status'] if self.file_items[i].command != None else ''
                display_filter[i] = status_seach_info  ==  status

        self.display_files(display_filter)
        self.update_view()

        
    def on_regex_search(self, *args):
        regex_str = self.regex_str.get()
        display_filter =  [True] * len( self.file_items)
        if regex_str :
            if regex_str :
                display_filter =  [False] * len( self.file_items)
                r = re.compile(regex_str)
                for i in range(len(self.file_items)):
                    display_filter[i] = r.match(self.file_items[i].base_file_name)
        self.display_files(display_filter)
        
        self.update_view()
         
    # def regex_reset(self, *args):
    #     display_filter =  [True] * len( self.file_items)
    #     self.display_files(display_filter)
    #     self.update_view()      

    def on_confirm_and_next(self, *args):
        self.on_confirm(*args)
        self.tree.yview_scroll(1, what='unit')
        self.goto_next_item()

    def on_go_prev(self, *args):
        self.goto_prev_item()


    def on_delete_file(self, *args):
        selected_file_id = self.get_selected_item()
        item_value = self.tree.item(str(selected_file_id),"values")
        new_item_value = (item_value[0], 'deleted',  item_value[2])
        self. tree.item(str(selected_file_id), values=(new_item_value))

        os.remove(self.file_items[selected_file_id].file_path)
        if selected_file_id == self.first_unprocessed_file_id :
            self.find_next_unprocessed_item()

        self.tree.yview_scroll(1, what='unit')
        self.goto_next_item()

    def find_next_unprocessed_item(self) :
        i = self.first_unprocessed_item_id + 1
        while i <  len(self.displayed_ids)  :
            if not self.file_items[self.displayed_ids[i]].command :
                self.first_unprocessed_file_id = self.displayed_ids[i]
                self.first_unprocessed_item_id = i
                break
            i += 1

        if i == len(self.displayed_ids) :
            self.first_unprocessed_file_id = None
            self.first_unprocessed_item_id = None

    def on_confirm(self, *args):
        recorder = TextGridRecorder()

        time_zones = self.plotter_.get_timezones()
        selected_file_id = self.get_selected_item()

        if not self.file_items[selected_file_id].command :
            self.processed_items += 1

        item_value = self.tree.item(str(selected_file_id),"values")

        # self.file_items[selected_file_id].raw_label = selected_label      
        status = 'clipped' if len(time_zones) > 1 else 'unclipped'

        if (len(time_zones) % 2) == 0:
            print ("the number of  time zones  must be 1 or 3!")  
            status = 'wrong'  

        new_item_value = (item_value[0], status,  item_value[2])
        self. tree.item(str(selected_file_id), values=(new_item_value))

        textgrid_file_path =os.path.splitext(self.file_items[selected_file_id].file_path)[0] + '.textgrid'

        recorder.write_textgrid(textgrid_file_path, time_zones)

        self.file_items[selected_file_id].command = {"status": status, 'timezones':time_zones}

        if  selected_file_id  == self.first_unprocessed_file_id  :
            self.find_next_unprocessed_item()

        self.update_progress()

    def on_select_first(self, *args):

        self.tree.selection_set(self.displayed_ids[0])
        self.tree.focus(self.displayed_ids[0])
        self.tree.yview_moveto(0)   

        self.update_view()
        

    def on_select_last(self, *args):

        self.tree.selection_set(self.displayed_ids[-1])
        self.tree.focus(self.displayed_ids[-1])
        self.tree.yview_moveto(1)   
        self.update_view()

    def on_canvas_mouse_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        if (event.inaxes is not None and event.xdata is not None) :
            self.plotter_.on_clicked(event.inaxes, event.xdata) 

    def on_set_zone_pressed(self, event):
        # print('%s entered: xdata=%f, ydata=%f' %
        #    (event.key,  event.xdata, event.ydata))
        # if event.key == 'enter' :
        self.plotter_.set_zone() 

    def  goto_prev_item(self) :
        selected_file_id = self.get_selected_item()
        prev_item = self. tree.prev(str(selected_file_id))
        if prev_item :
            self.tree.selection_set(prev_item)
            self.tree.focus(prev_item)

        self.update_view()

    # def on_prev_item(self, *args):

    #     self.goto_prev_item()

    def  goto_next_item(self) :

        selected_file_id = self.get_selected_item()
        next_item = self. tree.next(str(selected_file_id))
        if next_item :
            self.tree.selection_set(next_item)
            self.tree.focus(next_item)

        self.update_view()

    # def on_next_item(self, *args):
    UPDATE_PROGRESS_INTERVAL = 0.2
    UPDATE_PROGRESS_INTERVAL_MS = int(UPDATE_PROGRESS_INTERVAL * 1000)
    #     self.goto_next_item()
    def update_play_progress(self) :
        self.play_time  += KeywordClip.UPDATE_PROGRESS_INTERVAL
        if self.play_time < self.play_end_time - 0.1 :
            self.root.after(KeywordClip.UPDATE_PROGRESS_INTERVAL_MS, self.update_play_progress)
            self.plotter_.plot_progress(self.play_time)
        else :
            self.plotter_.remove_progress()

    def play_audio(self, wave_file):
        if self.progress_timer :
            self.root.after_cancel(self.progress_timer)
        sa.stop_all()
             
        play_zone = self.plotter_.get_play_time_zone()
        
        fs, audio_data = wav.read(wave_file)
        if play_zone :
            start_position =  int(play_zone.start * fs)
            end_position = int(play_zone.end * fs)
            self.play_time = play_zone.start
            self.play_end_time = play_zone.end            
        else :
            start_position = 0
            end_position = audio_data.shape[0]
            self.play_time = 0
            self.play_end_time = audio_data.shape[0] / fs

        # self.timer = self.plotter_.get_figure().canvas.new_timer(interval = 100, callbacks=[(self.update_play_progress, (1, ), {'a': 3}),])
        # self.timer.start()
        # self.plotter_.plot_progress(self.play_time)

        self.wait_id = self.root.after(KeywordClip.UPDATE_PROGRESS_INTERVAL_MS, self.update_play_progress)
        sa.play_buffer(audio_data[start_position:end_position], num_channels = 1, bytes_per_sample = 2, sample_rate = fs)


        # wave_obj = sa.WaveObject.from_wave_file(wave_file)
        # wave_obj.play()
        # play_obj.wait_done()  # Wait until sound has finished playing  

    def on_play(self, *args):
        selected_file_id = self.get_selected_item()
        self.play_audio(self.file_items[selected_file_id].file_path)

    def on_delete_timezone(self, *args):
        self.plotter_.delete_time_zone() 

    def on_revert(self, *args):
        self.plotter_.revert_history_time_zone() 

        # self.play_audio(self.file_items[selected_file_id].file_path)

    def on_select_src_folder(self, *args):
        src_data_folder = filedialog.askdirectory()
        if src_data_folder:
            self.src_folder_ctrl.set(src_data_folder)
            self.app_config['src_folder'] = src_data_folder
            self.save_config( self.app_config)
            self.load_dir(src_data_folder)

    def on_select_item(self, *args) :
        self.update_view()
        self.on_play()

    def on_closing(self, *args):
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        self.root.destroy()

    def update_view(self) :
        self.update_ctrls()
        self. update_figure()

    def update_ctrls(self) :
        selected_file_id = self.get_selected_item()
        if selected_file_id is None :
            return 

        # self. selected_label_ctrl.current(KeywordClip.keywords_to_id[self.file_items[selected_file_id].raw_label])
        # self.detected_label.set(self.file_items[selected_file_id].raw_label)

        self.update_progress()

    def update_progress(self) :
        progress_str = "processed: {}/{}".format(self.processed_items, self.total_items)
        if self.first_unprocessed_file_id is not None:
            progress_str += ", first unprocessed: {}".format(self.first_unprocessed_item_id)

        self.process_progress.set(progress_str)

    def update_figure(self):
        # try:
        selected_file_id = self.get_selected_item()

        self.draw_wav_data(self.file_items[selected_file_id].file_path, None if self.file_items[selected_file_id].command is None else self.file_items[selected_file_id].command['timezones'])

    def load_status(self,  data_dir) :
        textgrid_files = TextGridRecorder.find_textgrid(data_dir)
        if not textgrid_files :
            return None

        recorder = TextGridRecorder()

        records_map = {}
        for textgrid_file in textgrid_files :
            time_zones = recorder.read_textgrid(textgrid_file)
            wav_file_path =os.path.splitext(os.path.basename(textgrid_file))[0]
            records_map[wav_file_path] = {'status': 'clipped' if len(time_zones) > 1 else 'unclipped', 'timezones':time_zones} 

        return records_map

    @staticmethod
    def find_wav(data_dir) :
            wav_files = [] 
            if data_dir:
                for (dirpath, _, filenames) in os.walk(data_dir):  
                    for filename in filenames:  
                        if filename.endswith('.wav') or filename.endswith('.WAV'):  
                            filename_path = os.sep.join([dirpath, filename])  
                            wav_files.append(filename_path) 
            return wav_files

    def load_dir(self, data_dir):

        file_paths = self.find_wav(data_dir)
        if not file_paths :
            return
            
        self.file_items = []

        records_map = self.load_status(data_dir) 

        for file_path in file_paths :
            if records_map :
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                command_status = records_map.get(base_name)
                if command_status :
                    self.file_items.append(FileItem(file_path, command_status))
                else :
                    self.file_items.append(FileItem(file_path))
            else:
                self.file_items.append(FileItem(file_path))


        display_filter = [True] * len( file_paths)
        #display all files in the folder
        self.display_files(display_filter)

        # self.update_view()


    # def on_load(self, *args):
    #     self.load_dir(self.src_folder_ctrl.get())
        
    #     print('on_load succes')

    def get_selected_item(self) :
        selection = self.tree.focus()
        return  int(selection)


    def run(self) :
        self.root.mainloop()
    
    def load_config(self) :
        app_config = {}

        if  not os.path.exists(KeywordClip.config_file_name) :
            app_config['src_folder'] = ''
            return app_config

        with open(KeywordClip.config_file_name, 'r') as json_file :
            json_data = json.loads(json_file.read())
            app_config['src_folder'] = json_data.get('src_folder', '')

        return app_config

    def save_config(self, app_config) :
        with open(KeywordClip.config_file_name, 'w') as json_file :
            json.dump(app_config, json_file, ensure_ascii=False)
        

def main():
    speech_purger = KeywordClip()
    speech_purger.run()


if __name__ == '__main__':
    main()
