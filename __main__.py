from app_config import ApplicationConfigData, InvalidConfigFileError
from sensor_data import AnemometerData
from sensor_watcher import AnemometerWatcher
from data_sync import WindServerSynchronizer

import threading
import os

# Defines config filename
package_dir = os.path.dirname(os.path.abspath(__file__))
config_fn = os.path.join(package_dir, "config.json")

def main():
    print("... RealtimeWind has been started")

    try:
        config_data  = ApplicationConfigData(config_fn)
        speed_data   = AnemometerData()
        speed_sensor = AnemometerWatcher(config_data.raspberry_anemometer_pin(),
                                         speed_data)

        # The threading.Event is used to signal non-daemon threads that the 
        # main thread has died.
        stop_event  = threading.Event()
        server_sync = WindServerSynchronizer(speed_data,
                                             config_data.server_syncronization_interval(),
                                             stop_event)

        server_sync.run()

        # The main thread will keep watching sensors for its whole
        # life cycle.
        speed_sensor.start_watching()

    except InvalidConfigFileError, error:
      print(error)

    except(KeyboardInterrupt, SystemExit):
        cleanup(stop_event)

def cleanup(stop_event):
  print("\n... Shutting down RealtimeWind application")

  # Signal non-daemon threads to finish their jobs
  stop_event.set()
  while threading.active_count() > 1:
      pass

  print("... RealtimeWind has been closed")

if __name__ == '__main__':
    main()
