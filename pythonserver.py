# general imports
import time
import bisect

# network imports
import socket
import threading
import signal

# network lock
lock = threading.Lock()
stop_flag = False

# radio imports
import tinygs_rx_custom

# server variables
SERVER_IP = "127.0.0.1"
SERVER_PORT_GPREDICT = 5555
SERVER_PORT_LORA = 40868

# tinygs satellite parameters
DEFAULT_SATELLITE = "ISM_433"
RECENTLY_SEEN = 300 # in the last 5 minutes
satellite_db = {
    "Norby":{"freq":436.703e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "Norby-2":{"freq":436.703e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "Polytech_Universe-3":{"freq":436.55e6, "sf":8, "cr":6, "bw":62.5e3, "last_seen":1712504745, "num_timeouts":0},
    "CSTP-1.1":{"freq":436.075e6, "sf":8, "cr":6, "bw":62.5e3, "last_seen":1712504745, "num_timeouts":0},
    "CSTP-1.2":{"freq":436.27e6, "sf":8, "cr":6, "bw":62.5e3, "last_seen":1712504745, "num_timeouts":0},
    "2023-091T":{"freq":435.05e6, "sf":8, "cr":6, "bw":62.5e3, "last_seen":1712504745, "num_timeouts":0},
    "RS52SB":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "RS52SV":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "RS52SG":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "RS52SD":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "RS52SE":{"freq":436.26e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "MDQubeSAT-2":{"freq":436.9e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "2023-003A":{"freq":400.13e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "Tianqi-7":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "GaoFen-13":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "GaoFen17":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "GaoFen19":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "TIANQI-24":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "TIANQI-23":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "TIANQI-22":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "TIANQI-21":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "ReshUCube-2":{"freq":436e6, "sf":7, "cr":5, "bw":125e3, "last_seen":1712504745, "num_timeouts":0},
    "TIANQI-219":{"freq":400.45e6, "sf":9, "cr":5, "bw":500e3, "last_seen":1712504745, "num_timeouts":0},
    "PY4-1":{"last_seen":1712504745, "num_timeouts":999999999},
    "PY4-2":{"last_seen":1712504745, "num_timeouts":999999999},
    "PY4-3":{"last_seen":1712504745, "num_timeouts":999999999},
    "PY4-4":{"last_seen":1712504745, "num_timeouts":999999999},
    "ONDOSAT-OWL-1":{"freq":435e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "ONDOSAT-OWL-2":{"freq":435e6, "sf":10, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0},
    "Platform-5":{"last_seen":1712504745, "num_timeouts":999999999},
    "SWARM":{"last_seen":1712504745, "num_timeouts":999999999},
    "Starlink":{"freq":137.055e6, "sf":8, "cr":5, "bw":41.7e3, "last_seen":1712504745, "num_timeouts":0},
    "INS-2D":{"last_seen":1712504745, "num_timeouts":999999999},
    "ISM_433":{"freq":433.3e6, "sf":8, "cr":5, "bw":250e3, "last_seen":1712504745, "num_timeouts":0}
}

class Radio():
    def __init__(self, default_satellite=DEFAULT_SATELLITE):
        # generic radio params
        self.samp_rate = 2.5e6
        self.offset = 700e3
        self.gain = 20
        # satellite specific params
        self.lora_sf = -1
        self.lora_cr = -1
        self.lora_bw = -1
        self.center_freq = -1
        # socket parameters
        self.timeout_s = 5 # how long to wait for lora data
        self.num_timeout_threshold = 100 # how many consecutive timeouts before switching satellites
        # general data structures
        self.active_satellite = "" # changes based on satellites in view. Empty if no satellite in view.
        self.persistent_stare = True # set to true if you only want to look at default satellite

    # update radio parameters based on the satellite we want to listen to
    def update_params(self, satellite_name, tb=None):
        print(f"Tuning in to {satellite_name}\n")
        satellite_info = satellite_db[satellite_name]
        self.lora_bw = satellite_info["bw"]
        self.lora_sf = satellite_info["sf"]
        self.lora_cr = satellite_info["cr"]
        self.center_freq = satellite_info["freq"]
        if(tb is not None):
            tb.set_lora_bw(self.lora_bw)
            tb.set_lora_sf(self.lora_sf)
            tb.set_lora_cr(self.lora_cr)
            tb.set_center_freq(self.center_freq)
            tb.start()
            #tb.show()
        return

    # update which satellites are in view
    def update_satellites_in_view(self, satellite_name, tb):
        if(satellite_name in satellite_db):
            satellite_db[satellite_name]["last_seen"] = int(time.time())
        # retune radio if there's a new satellite
        if(not persistent_stare and not active_satellite):
            active_satellite = satellite_name
            self.update_params(satellite_name, tb=tb)
        return

    # sorting metric for satellites
    def sorting_key(self, satellite, timestamp):
        return (timestamp - satellite_db[satellite]["last_seen"]), satellite_db[satellite]["num_timeouts"]

    # switch satellite we're staring at based on last seen and precedence of timeouts
    def switch_satellites(self, received_data):
        # only switch if we are not persistently staring and there is an active satellite
        if(not self.persistent_stare and self.active_satellite):
            # penalize the satellite if no data was received
            if(not received_data):
                satellite_db[self.active_satellite]["num_timeouts"] = satellite_db[self.active_satellite]["num_timeouts"] + 1
            
            # create a sorted list of satellites to choose from
            timestamp = int(time.time())
            priority_list = sorted([], key=lambda satellite: self.sorting_key(satellite, timestamp), reverse=False)
            for satellite in satellite_db:
                if(satellite == self.active_satellite or satellite_db[satellite]["num_timouts"] == 999999999):
                    continue
                bisect.insort(priority_list, satellite)
            
            # if it was recently seen, tune to it. otherwise, go back to default
            if(timestamp - satellite_db[priority_list[0]]["last_seen"] < RECENTLY_SEEN):
                self.active_satellite = priority_list[0]
            else:
                self.active_satellite = ""
            signal.raise_signal(signal.SIGTERM) # tell the tinygs thread to stop
        return
            
        
# listen to see which satellites are in view
def handle_gpredict_client(client_socket, addr, radio, tb):
    global stop_flag
    try:
        while not stop_flag:
            satellite_name = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"updating {satellite_name}\n")
            with lock:
                radio.update_satellites_in_view(satellite_name, tb=tb) # update the radio with current satellites
    except KeyboardInterrupt:
        print("closing connection\n")
    finally:
        client_socket.close()

def handle_lora_client(server_socket, radio, tb):
    global stop_flag
    num_timeouts = 0
    received_data = False
    try:
        while not stop_flag:
            try:
                data, _ = server_socket.recvfrom(1024)
                print(f"Received from server: {data}\n")
                num_timeouts = 0
                received_data = True
            except TimeoutError:
                num_timeouts = num_timeouts + 1
                if(not radio.persistent_stare and num_timeouts > radio.num_timeout_threshold):
                    with lock:
                        radio.switch_satellites(received_data) # also stops tb
                    tb.stop()
                    tb.wait()
                    received_data = False
                    num_timeouts = 0
                    print("no data received from satellite, switching now\n")
                    satellite_name = radio.active_satellite
                    if(not satellite_name):
                        satellite_name = DEFAULT_SATELLITE
                    radio.update_params(satellite_name, tb=tb)
    except KeyboardInterrupt:
        print("stopping lora receive\n")
    finally:
        server_socket.close()

def main():
    global stop_flag
    # create gpredict server
    server_socket_gpredict = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_gpredict.bind((SERVER_IP, SERVER_PORT_GPREDICT))
    server_socket_gpredict.listen()

    # initialize radio parameters and start receiving
    radio = Radio()
    radio.update_params(DEFAULT_SATELLITE)
    tb = tinygs_rx_custom.tinygs_rx(radio)
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
    signal.signal(signal.SIGTERM, sig_handler)

    # create LoRa TAP server
    server_socket_lora = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket_lora.settimeout(radio.timeout_s)
    server_socket_lora.bind((SERVER_IP, SERVER_PORT_LORA))
    lora_thread = threading.Thread(target=handle_lora_client, args=(server_socket_lora, radio, tb))
    lora_thread.start()

    try:
        while True:
            # wait for gpredict to tell us which satellites are in the sky
            client_socket, addr = server_socket_gpredict.accept()
            client_thread = threading.Thread(target=handle_gpredict_client, args=(client_socket, addr, radio, tb))
            client_thread.start()
    except KeyboardInterrupt:
        print("shutting down, wait for socket timeout to expire\n")
    finally:
        stop_flag = True
        lora_thread.join()
        server_socket_gpredict.close()
        tb.stop()
        tb.wait()

if __name__=="__main__":
    main()
