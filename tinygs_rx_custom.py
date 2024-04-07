#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.4.0

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
import lora

from gnuradio import qtgui

class tinygs_rx(gr.top_block, Qt.QWidget):

    def __init__(self, radio):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        #Qt.QWidget.__init__(self)
        #self.setWindowTitle("Not titled yet")
        #qtgui.util.check_set_qss()
        #try:
        #    self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        #except:
        #    pass
        #self.top_scroll_layout = Qt.QVBoxLayout()
        #self.setLayout(self.top_scroll_layout)
        #self.top_scroll = Qt.QScrollArea()
        #self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        #self.top_scroll_layout.addWidget(self.top_scroll)
        #self.top_scroll.setWidgetResizable(True)
        #self.top_widget = Qt.QWidget()
        #self.top_scroll.setWidget(self.top_widget)
        #self.top_layout = Qt.QVBoxLayout(self.top_widget)
        #self.top_grid_layout = Qt.QGridLayout()
        #self.top_layout.addLayout(self.top_grid_layout)

        #self.settings = Qt.QSettings("GNU Radio", "tinygs_rx")

        #try:
        #    if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        #        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        #    else:
        #        self.restoreGeometry(self.settings.value("geometry"))
        #except:
        #    pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = 2.5e6
        self.offset = 0.7e6
        self.lora_sf = 9
        self.lora_cr = 8
        self.lora_bw = 500e3
        self.center_freq =  433.3e6
        self.gain = 20
        if(radio is not None):
            self.samp_rate = radio.samp_rate
            self.offset = radio.offset
            self.gain = radio.gain
            self.lora_sf = radio.lora_sf
            self.lora_cr = radio.lora_cr
            self.lora_bw = radio.lora_bw
            self.center_freq = radio.center_freq

        ##################################################
        # Blocks
        ##################################################
        self.soapy_custom_source_0 = None
        dev = 'driver=' + 'airspy'
        stream_args = ''
        tune_args = ['']
        settings = ['']
        self.soapy_custom_source_0 = soapy.source(dev, "fc32",
                                  1, '',
                                  stream_args, tune_args, settings)
        self.soapy_custom_source_0.set_sample_rate(0, self.samp_rate)
        self.soapy_custom_source_0.set_bandwidth(0, 0)
        self.soapy_custom_source_0.set_antenna(0, 'RX')
        self.soapy_custom_source_0.set_frequency(0, (self.center_freq + self.offset))
        self.soapy_custom_source_0.set_frequency_correction(0, 0)
        self.soapy_custom_source_0.set_gain_mode(0, False)
        self.soapy_custom_source_0.set_gain(0, self.gain)
        self.soapy_custom_source_0.set_dc_offset_mode(0, False)
        self.soapy_custom_source_0.set_dc_offset(0, 0)
        self.soapy_custom_source_0.set_iq_balance(0, 0)
        self.lora_message_socket_sink_0 = lora.message_socket_sink('127.0.0.1', 40868, 0)
        self.lora_lora_receiver_0 = lora.lora_receiver(self.samp_rate, self.center_freq + self.offset, [self.center_freq], int(self.lora_bw), self.lora_sf, False, (self.lora_cr-4), True, False, False, 1, False, False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.lora_message_socket_sink_0, 'in'))
        self.connect((self.soapy_custom_source_0, 0), (self.lora_lora_receiver_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "tinygs_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.lora_lora_receiver_0.set_center_freq(self.center_freq + self.offset)
        self.soapy_custom_source_0.set_frequency(0, (self.center_freq + self.offset))

    def get_lora_sf(self):
        return self.lora_sf

    def set_lora_sf(self, lora_sf):
        self.lora_sf = lora_sf
        self.lora_lora_receiver_0.set_sf(self.lora_sf)

    def get_lora_cr(self):
        return self.lora_cr

    def set_lora_cr(self, lora_cr):
        self.lora_cr = lora_cr

    def get_lora_bw(self):
        return self.lora_bw

    def set_lora_bw(self, lora_bw):
        self.lora_bw = lora_bw

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.lora_lora_receiver_0 = lora.lora_receiver(self.samp_rate, self.center_freq + self.offset, [self.center_freq], int(self.lora_bw), self.lora_sf, False, (self.lora_cr-4), True, False, False, 1, False, False)
        self.soapy_custom_source_0.set_frequency(0, (self.center_freq + self.offset))




def main(top_block_cls=tinygs_rx, options=None, radio=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    #qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(radio=radio)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        #Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    #qapp.exec_()

if __name__ == '__main__':
    main()
