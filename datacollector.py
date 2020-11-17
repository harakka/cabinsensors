"""Retrieve sensor and system data for later consumption

This module runs in its own thread, and every x seconds it adds sensor results to the results queue.
"""
import subprocess
from Queue import Queue
from threading import Thread
from time import sleep, time

from ruuvitag_sensor.ruuvi import RuuviTagSensor

import Adafruit_DHT

queue = Queue()


class DataCollector(Thread):
    polling_time = 10           #
    latest_ruuvitag_data = {}

    """Initialize the data collection by binding ruuvitag sensor to result callback method.
    """
    def __init__(self, results_queue: Queue):
        RuuviTagSensor.get_datas(self.get_ruuvitag_data)

    def run(self):
        sleep(self.polling_time)

    """Retrieve system info like ethernet and disk usage
    """
    @staticmethod
    def get_system_data():
        system = {}
        system['wan_ip'] = subprocess.check_output("ip -4 -h addr show dev wlan0 | grep inet | xargs | cut -d \' \' -f 2", shell=True)
        system['lan_ip'] = subprocess.check_output("ip -4 -h addr show dev eth0 | grep inet | xargs | cut -d \' \' -f 2", shell=True)
        system['cpu_load'] = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'", shell=True)
        system['mem_usage'] = subprocess.check_output("free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'", shell=True)
        system['disk_usage'] = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'", shell=True)

    def get_ruuvitag_data(self, data):
        # data[0] is the ruuvitag mac which we ignore, data[1] contains the actual sensor data.abspath
        # If we ever use multiple ruuvitags, this needs to be adapted, eg. by using the mac as key.
        self.latest_ruuvitag_data['temperature'] = data[1]['temperature']
        self.latest_ruuvitag_data['humidity'] = data[1]['humidity']
