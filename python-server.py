# network imports
import socket
import threading

# network lock
lock = threading.Lock()

# radio imports
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
import lora

# server variables
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

# tinygs satellite parameters
satellite_db =
{
    "Norby":{"freq":436.703e6, "sf":10, "cr":5, "bw":250e3},
    "Norby-2":{"freq":436.703e6, "sf":10, "cr":5, "bw":250e3},
    "Polytech_Universe-3":{"freq":436.55e6, "sf":8, "cr":6, "bw":62.5e3},
    "CSTP-1.1":{"freq":436.075e6, "sf":8, "cr":6, "bw":62.5e3},
    "CSTP-1.2":{"freq":436.27e6, "sf":8, "cr":6, "bw":62.5e3},
    "2023-091T":{"freq":435.05e6, "sf":8, "cr":6, "bw":62.5e3},
    "RS52SB":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3},
    "RS52SV":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3},
    "RS52SG":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3},
    "RS52SD":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3},
    "RS52SE":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3},
    "MDQubeSAT-2":{"freq":436.9e6, "sf":10, "cr":5, "bw":250e3},
    "2023-003A":{"freq":400.13e6, "sf":9, "cr":5, "bw":500e3},
    "Tianqi-7":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "GaoFen-13":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "GaoFen17":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "GaoFen19":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "TIANQI-24":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "TIANQI-23":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "TIANQI-22":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "TIANQI-21":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "ReshUCube-2":{"freq":436e6, "sf":7, "cr":5, "bw":125e3},
    "TIANQI-219":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3},
    "PY4-1":{},
    "PY4-2":{},
    "PY4-3":{},
    "PY4-4":{},
    "ONDOSAT-OWL-1":{"freq":435e6, "sf":10, "cr":5, "bw":250e3},
    "ONDOSAT-OWL-2":{"freq":435e6, "sf":10, "cr":5, "bw":250e3},
    "Platform-5":{},
    "SWARM":{},
    "Starlink":{"freq":137.055e6, "sf":8, "cr":5, "bw":41.7e3},
    "INS-2D":{}
}

# listen to see which satellites are in view
def handle_client(client_socket, addr, radio):
    try:
        while True:
            satellite_name = client_socket.recv(1024).decode()
            if not message:
                break
            with lock:
                radio.notify(satellite_name) # update the radio with current satellites
    except KeyboardInterrupt:
        print("closing connection")
    finally:
        client_socket.close()

class Radio(self):
    def __init__(self):
        self.samp_rate = 2.5e6
        self.offset = 700e3
        self.lora_sf = 9
        self.lora_cr = 8
        self.lora_bw = 500e3
        self.center_freq = 433.3e6
        self.gain = 20
        self.source = None
        self.lora_receiver = None

    def update_params(satellite_info):
        self.center_freq = satellite_info["freq"]
        self.lora_sf = satellite_info["sf"]
        self.lora_cr = satellite_info["cr"]
        self.lora_bw = satellite_info["bw"]

    def notify(self, satellite_name):
        if(satellite_name in satellite_db):
            satellite_info = satellite_db[satellite_name]
            self.update_params(satellite_info)
        

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    radio = Radio()

    dev = 'driver=' + 'airspy'
    stream_args = ''
    tune_args = ['']
    settings = ['']
    radio.source = soapy.source(dev, "fc32", 1, '',
                                stream_args, tune_args, settings)
    radio.source.set_sample_rate(0, radio.samp_rate)
    radio.source.set_bandwidth(0, 0)
    radio.source.set_antenna(0, 'RX')
    radio.source.set_frequency(0, (radio.center_freq + radio.offset))
    radio.source.set_frequency_correction(0, 0)
    radio.source.set_gain_mode(0, False)
    radio.source.set_gain(0, radio.gain)
    radio.source.set_dc_offset_mode(0, False)
    radio.source.set_dc_offset(0, 0)
    radio.source.set_iq_balance(0, 0)
    output_file = '/home/dragon/Documents/tiny-gs/lora_test.txt'
    radio.lora_receiver = lora.lora_receiver(radio.samp_rate, radio.center_freq + radio.offset, [radio.center_freq], int(radio.lora_bw), radio.lora_sf, False, (radio.lora_cr-4), True, False, False, 1, False, False)

    try:
        while True:
            print("awaiting connections...")
            client_socket, addr = server_socket.accept()
            print("client connected!")

            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, radio))
            client_thread.start()
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        server_socket.close()

if __name__=="__main__":
    main()
