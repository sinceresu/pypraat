#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' plotter: plotting module '

__author__ = 'Andy Su'

import numpy as np
import matplotlib.pyplot as plt
from python_speech_features import fbank
import librosa

from global_defs import TimeZone

class Plotter(object):
    """
    implementing a wrapper class for polymorphism
    """

    def __init__(self, figure_size):
        """
        initialize plotter differently to adapt multiple type of data source (
            static data or data queue)
        """

        self.figure_ = plt.figure(figsize=figure_size)
        self.sub_plots_ = self.figure_.subplots(4, gridspec_kw={'height_ratios': [8, 8, 8, 1]})
        plt.subplots_adjust(hspace=0.00, left=0.03, right=0.992, top=0.95, bottom=0.03)

        for i in range(len(self.sub_plots_)):
            self.sub_plots_[i].set_ylim(0, 65536)

        self.audio_axes = self.sub_plots_[0]
        self.specgram_axes = self.sub_plots_[1]
        self.time_zone_axes = self.sub_plots_[2]
        self.zone_info_axes = self.sub_plots_[3]

        self.init_audio_axes()
        self.init_specgram_axes()
        self.init_time_zone_axes()
        self.init_zone_info_axes()

        self.time_zones = []

        self.current_time_pos = None
        self.current_time_zone= None
        self.play_time_zone= None



        self.figure_.canvas.draw()

    def get_figure(self) :
        return self.figure_

    def get_timezones(self) :
        return self.time_zones

    def get_play_time_zone(self) :
        return self.play_time_zone 

    def plot_audio(self, audio,  sr) :
        axes  = self.audio_axes
        sample_interval = 1.0/sr #ms
        xaxis_array = np.arange(audio.shape[0]) * sample_interval

        audio_min = np.min(audio)
        audio_max = np.max(audio)
        axes.clear()

        self.audio_time_line = None
        self.audio_progress_line = None
        self.audio_zone_span = None

        axes.set_xlim(self.xlim)
        # axes.set_xlabel("Time(s)")
        # axes.set_ylabel("Altitude")
        axes.set_ylim(int(audio_min), int(audio_max))

        axes.plot(xaxis_array, audio, '')

        # axes.set_title('Audio')
    def get_pcen(self, audio, sr, frame_step) :
            fbe, _ = fbank(audio, samplerate=sr, winlen=0.025, winstep=frame_step, nfilt=80, nfft=512)
        # Magnitude spectra (nfilt x nframe)
            mag_spec = np.transpose(np.sqrt(fbe/2))
            zi = np.reshape(mag_spec[:,0], (-1,1))
            pcen_s = librosa.pcen(mag_spec, sr=sr, hop_length=int(frame_step*sr), zi=zi)   
            pcen_s = np.transpose(pcen_s)
            return pcen_s   

    def plot_specgram(self, audio, sr) :
        axes  = self.specgram_axes
        axes.clear()

        self.specgram_time_line = None
        self.specgram_progress_line = None
        self.specgram_zone_span = None

        # axes.specgram(audio, Fs=sr, scale_by_freq=True, sides='default')  # 绘制频谱
        PCEN_STEP = 0.01
        pcen = self.get_pcen(audio, sr, PCEN_STEP)
        sample_interval = PCEN_STEP #ms
        xaxis_array = np.arange(pcen.shape[0] + 1) * sample_interval
        yaxis_array = np.arange(pcen.shape[1] + 1)
        axes.pcolormesh(xaxis_array, yaxis_array, np.transpose(pcen))

        #axes.set_xlim(self.xlim)
        #axes.set_title('Specgram')


    def plot_time_zone(self, time_zone_selected = False) :

        axes  = self.time_zone_axes
        axes.clear()
        axes.set_xlim(self.xlim)

        self.time_zone_time_line = None
        self.time_zone_progress_line = None

        self.high_light_time_zone()
        self.plot_time_zone_edge(time_zone_selected)

    def plot_zone_info(self, time_zone_selected = False) :

        axes  = self.zone_info_axes
        axes.clear()
        axes.set_xlim(self.xlim)

        self.plot_zone_info_text()
        self.plot_zone_info_edge(time_zone_selected)


    def plot(self, file_path, audio, sr = 16000, time_zones = None):
        self.xlim = (0, audio.shape[0] / sr)
        
        self.plot_specgram(audio,  sr)
        self.plot_audio(audio, sr)

        if time_zones is None :
            self.current_time_zone = TimeZone(self.xlim[0], self.xlim[1])
            self.time_zones = [self.current_time_zone]
        else :
            self.time_zones = time_zones
            self.current_time_zone = time_zones[len(time_zones) // 2]


        self.time_zones_history = []
        self.current_zone_history = []

        self.play_time_zone = TimeZone(self.xlim[0], self.xlim[1])

        self.plot_time_zone()

        self.plot_zone_info()
        

        self.figure_.suptitle(file_path , fontsize=16)

        self.high_lighted_span = None

        self.figure_.canvas.draw()

    def init_audio_axes(self) :
        axes  = self.audio_axes

        axes.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,         # ticks along the top edge are off
            labelleft=False) # labels along the bottom edge are off

        axes.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            labelbottom=False) # labels along the bottom edge are off

    def init_specgram_axes(self) :
        axes  = self.specgram_axes
        axes.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            labelbottom=False) # labels along the bottom edge are off        

    def init_time_zone_axes(self) :
        axes  = self.time_zone_axes
        axes.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,         # ticks along the top edge are off
            labelleft=False) # labels along the bottom edge are off

        axes.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom = False,
            top = False,
            labelbottom=False) # labels along the bottom edge are off

        
    def init_zone_info_axes(self) :
        axes  = self.zone_info_axes
        axes.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,         # ticks along the top edge are off
            labelleft=False) # labels along the bottom edge are off
        
        axes.set_facecolor('#e0e0e0')


    def plot_time_zone_edge(self, time_zone_selected = False):
        for time_zone in self.time_zones :
            if time_zone !=  self.time_zones[0] and time_zone == self.current_time_zone:
                self.time_zone_axes.axvline( time_zone.start, color = 'red' if time_zone_selected else  'blue', alpha=0.5, linewidth = 4.0)
            elif time_zone !=  self.time_zones[0] :
                self.time_zone_axes.axvline( time_zone.start, color= 'blue', alpha=0.5, linewidth = 4.0)

    def plot_zone_info_edge(self, time_zone_selected = False):
        for time_zone in self.time_zones :
            if time_zone !=  self.time_zones[0] and time_zone == self.current_time_zone:
                self.zone_info_axes.axvline( time_zone.start, color = 'red' if time_zone_selected else  'blue', alpha=0.5, linewidth = 4.0)
            elif time_zone !=  self.time_zones[0] :
                self.zone_info_axes.axvline( time_zone.start, color= 'blue', alpha=0.5, linewidth = 4.0)


    def plot_zone_info_text(self, time_zone_selected = False):
        for time_zone in self.time_zones :
            zone_center = (time_zone.start + time_zone.end) / 2
            self.zone_info_axes.text( zone_center, 0.5, "{:.3f}s".format(time_zone.end - time_zone.start), horizontalalignment='center', verticalalignment='center')

    def high_light_audio(self):
        self.clear_on_audio()
        self.audio_zone_span = self.audio_axes.axvspan(self.current_time_zone.start, self.current_time_zone.end, alpha=0.5, color='pink')

    def high_light_specgram(self):
        self.clear_on_specgram()
        self.specgram_zone_span = self.specgram_axes.axvspan(self.current_time_zone.start, self.current_time_zone.end, alpha=0.5, color='pink')

    def high_light_time_zone(self):
        self.time_zone_axes.axvspan(self.current_time_zone.start, self.current_time_zone.end, alpha=0.5, color='yellow')

    def clear_zone_span_on_audio(self) :            
        if self.audio_zone_span :
            self.audio_zone_span.remove()
            self.audio_zone_span = None

    def clear_on_audio(self) :            
        if self.audio_time_line :
            self.audio_time_line.remove()
            self.audio_time_line = None
        self.clear_zone_span_on_audio()

    def plot_time_line_on_audio(self, time_pos) :
        self.clear_zone_span_on_audio()

        if self.audio_time_line is  None:
            self.audio_time_line = self.audio_axes.axvline( time_pos, alpha=0.5, color= 'r', linestyle='dashed')
        else :
            self.audio_time_line.set_data((time_pos, time_pos), (0, 1))

    def clear_zone_span_on_specgram(self) :            
        if self.specgram_zone_span :
            self.specgram_zone_span.remove()
            self.specgram_zone_span = None

    def clear_on_specgram(self) :            
        if self.specgram_time_line :
            self.specgram_time_line.remove()
            self.specgram_time_line = None
        self.clear_zone_span_on_specgram()

    def plot_time_line_on_specgram(self, time_pos) :
        self.clear_zone_span_on_specgram()

        if self.specgram_time_line is  None:
            self.specgram_time_line = self.specgram_axes.axvline( time_pos, alpha=0.5, color= 'r', linestyle='dashed')
        else :
            self.specgram_time_line.set_data((time_pos, time_pos), (0, 1))

    def clear_on_time_zone(self) :            
        if self.time_zone_time_line :
            self.time_zone_time_line.remove()
            self.time_zone_time_line = None

    def plot_time_line_on_time_zone(self, time_pos) :
        container_time_zone = None
        for time_zone in self.time_zones :
                if time_pos >= time_zone.start and time_pos < time_zone.end :
                    container_time_zone = time_zone
                    break

        if (self.current_time_zone != container_time_zone) :
            self.current_time_zone = container_time_zone
            self.plot_time_zone()

        if self.time_zone_time_line is  None:
            self.time_zone_time_line = self.time_zone_axes.axvline( time_pos, alpha=0.5, color= 'grey', linestyle='solid', linewidth = 4.0)
        else :
            self.time_zone_time_line.set_data((time_pos, time_pos), (0, 1))
    
    def plot_progress(self, time_pos) :
        if self.audio_progress_line is None :
            self.audio_progress_line = self.audio_axes.axvline( time_pos, alpha=0.5, color= 'g', linestyle='dashed', linewidth = 2.0)
            self.specgram_progress_line = self.specgram_axes.axvline( time_pos, alpha=0.5, color= 'g', linestyle='dashed', linewidth = 2.0)
        else :
            self.audio_progress_line.set_data((time_pos, time_pos), (0, 1))
            self.specgram_progress_line.set_data((time_pos, time_pos), (0, 1))

        if self.time_zone_progress_line is None :
            self.time_zone_progress_line = self.time_zone_axes.axvline( time_pos, alpha=0.5, color= 'g', linestyle='dashed', linewidth = 2.0)
        else :
            self.time_zone_progress_line.set_data((time_pos, time_pos), (0, 1))

        self.figure_.canvas.draw()

    def remove_progress(self) :
        if self.audio_progress_line :
            self.audio_axes.lines.remove(self.audio_progress_line)
            self.audio_progress_line = None
        if self.specgram_progress_line :
            self.specgram_axes.lines.remove(self.specgram_progress_line)
            self.specgram_progress_line = None
        if self.time_zone_progress_line :
            self.time_zone_axes.lines.remove(self.time_zone_progress_line)
            self.time_zone_progress_line = None

        self.figure_.canvas.draw()

    def on_position_time(self, time_pos = 0):

        self.plot_time_line_on_audio(time_pos)
        self.plot_time_line_on_specgram(time_pos)      

        self.plot_time_line_on_time_zone(time_pos)


        self.current_time_pos = time_pos
        self.play_time_zone = TimeZone(self.current_time_pos, self.xlim[1])

    def select_time_zone(self, time_pos = 0):
        self.clear_on_audio()
        self.clear_on_specgram()
      
        for time_zone in self.time_zones :
            if time_pos is None or time_zone.start is None:
                print("error!")
            if time_pos >= time_zone.start and time_pos < time_zone.end :
                self.current_time_zone = time_zone
                break

        self.play_time_zone   = self.current_time_zone
        
        self. plot_time_zone(time_zone_selected = True)
        self. plot_zone_info(time_zone_selected = True)

        self.high_light_audio()
        self.high_light_specgram()

        self.figure_.canvas.draw()

    def on_clicked(self, axes, time_pos):

        if axes == self.sub_plots_[0] or axes == self.sub_plots_[1] :
            self.on_position_time(time_pos = time_pos) 
        elif axes == self.sub_plots_[2]:
            self.select_time_zone(time_pos = time_pos) 
        else:
            pass
        self.figure_.canvas.draw()

    def set_zone(self):
        if self.current_time_pos :
            container_time_zone = None
            for i, time_zone in enumerate(self.time_zones) :
                    if self.current_time_pos >= time_zone.start and self.current_time_pos < time_zone.end :
                        container_time_zone = i
                        break
            #too closed to zone edge, just neglect 
            if  min(self.current_time_pos - self.time_zones[container_time_zone].start, self.time_zones[container_time_zone].end - self.current_time_pos) < 1e-5 :
                return 

            self.time_zones_history.append(self.time_zones.copy())
            self.current_zone_history.append(self.current_time_zone)

            new_time_zone  = TimeZone(self.current_time_pos, self.time_zones[container_time_zone].end)
            self.time_zones[container_time_zone] = TimeZone(self.time_zones[container_time_zone].start, self.current_time_pos )
            self.time_zones.insert(container_time_zone + 1, new_time_zone)

            self.current_time_zone = new_time_zone
            self.plot_time_zone()
            self.plot_zone_info()

            self.figure_.canvas.draw()

    def delete_time_zone(self):
        if len(self.time_zones) == 1 :
            return
        self.clear_on_audio()
        self.clear_on_specgram()

        self.time_zones_history.append(self.time_zones.copy())
        self.current_zone_history.append(self.current_time_zone)       

        for i, time_zone in enumerate(self.time_zones) :
            if time_zone == self.current_time_zone:
                if i > 0 :
                    self.time_zones[i - 1] = TimeZone(self.time_zones[i-1].start, self.current_time_zone.end)
                    self.time_zones.remove(self.current_time_zone)
                    self.current_time_zone = self.time_zones[i - 1]
                else:
                    self.time_zones[0] = TimeZone(self.current_time_zone.start, self.time_zones[1].end)
                    self.time_zones.remove(self.time_zones[1])
                    self.current_time_zone = self.time_zones[0]
                break

        self.plot_time_zone()
        self.plot_zone_info()

        self.figure_.canvas.draw()

    def revert_history_time_zone(self):
        if len(self.time_zones_history) == 0  :
            return

        self.clear_on_audio()
        self.clear_on_specgram()


        self.time_zones = self.time_zones_history.pop()
        self.current_time_zone = self.current_zone_history.pop()

        self.plot_time_zone()
        self.plot_zone_info()

        self.figure_.canvas.draw()
