# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Ben West
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART as OriginalUART
import Queue
import uuid
import argparse
import os

class Attrs:
    CradleService = uuid.UUID("F0ABA0B1-EBFA-F96F-28DA-076C35A521DB");

    # Share Characteristic Strings
    AuthenticationCode  = uuid.UUID("F0ABACAC-EBFA-F96F-28DA-076C35A521DB");
    ShareMessageReceiver = uuid.UUID("F0ABB20A-EBFA-F96F-28DA-076C35A521DB"); #  Max 20 Bytes - Writable
    ShareMessageResponse = uuid.UUID("F0ABB20B-EBFA-F96F-28DA-076C35A521DB"); #  Max 20 Bytes
    Command = uuid.UUID("F0ABB0CC-EBFA-F96F-28DA-076C35A521DB");
    Response = uuid.UUID("F0ABB0CD-EBFA-F96F-28DA-076C35A521DB"); #  Writable?
    HeartBeat = uuid.UUID("F0AB2B18-EBFA-F96F-28DA-076C35A521DB");

    # Possible new uuids????  60bfxxxx-60b0-4d4f-0000-000160c48d70
    CradleService2 = uuid.UUID("F0ACA0B1-EBFA-F96F-28DA-076C35A521DB");
    AuthenticationCode2  = uuid.UUID("F0ACACAC-EBFA-F96F-28DA-076C35A521DB"); #  read, write
    ShareMessageReceiver2 = uuid.UUID("F0ACB20A-EBFA-F96F-28DA-076C35A521DB"); #  read, write
    ShareMessageResponse2 = uuid.UUID("F0ACB20B-EBFA-F96F-28DA-076C35A521DB"); #  indicate, read
    Command2 = uuid.UUID("F0ACB0CC-EBFA-F96F-28DA-076C35A521DB"); #  read, write
    Response2 = uuid.UUID("F0ACB0CD-EBFA-F96F-28DA-076C35A521DB"); #  indicate, read, write
    HeartBeat2 = uuid.UUID("F0AC2B18-EBFA-F96F-28DA-076C35A521DB"); #  notify, read

    # Device Info
    DeviceService = uuid.UUID("00001804-0000-1000-8000-00805f9b34fb");
    PowerLevel = uuid.UUID("00002a07-0000-1000-8000-00805f9b34fb");

    VENDOR_UUID = uuid.UUID("F0ACA0B1-EBFA-F96F-28DA-076C35A521DB")

UART_SERVICE_UUID = uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
TX_CHAR_UUID      = uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
RX_CHAR_UUID      = uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')

class ShareUART (OriginalUART):
  ADVERTISED = [Attrs.CradleService]
  # SERVICES = [Attrs.DeviceService]
  SERVICES = [Attrs.CradleService]
  CHARACTERISTICS = [Attrs.AuthenticationCode, Attrs.Command, Attrs.Response, Attrs.ShareMessageReceiver, Attrs.ShareMessageResponse, Attrs.HeartBeat, Attrs.DeviceService, Attrs.PowerLevel]

  UART_SERVICE_UUID = Attrs.CradleService
  TX_CHAR_UUID = Attrs.Command
  RX_CHAR_UUID = Attrs.Response
  pass
class Share2UART (OriginalUART):
  # ADVERTISED = [Attrs.CradleService2]
  # ADVERTISED = [Attrs.VENDOR_UUID]
  ADVERTISED = [Attrs.VENDOR_UUID]
  # SERVICES = [Attrs.DeviceService]
  # SERVICES = [Attrs.CradleService2, Attrs.VENDOR_UUID]
  SERVICES = [Attrs.VENDOR_UUID, Attrs.DeviceService]
  # CHARACTERISTICS = [Attrs.AuthenticationCode2, Attrs.Command2, Attrs.Response2, Attrs.ShareMessageReceiver2, Attrs.ShareMessageResponse2, Attrs.HeartBeat2, Attrs.DeviceService, Attrs.PowerLevel]
  CHARACTERISTICS = [ ]

  HEARTBEAT_UUID = Attrs.HeartBeat2
  # UART_SERVICE_UUID = Attrs.CradleService2
  UART_SERVICE_UUID = Attrs.VENDOR_UUID
  TX_CHAR_UUID = Attrs.Command2
  RX_CHAR_UUID = Attrs.Response2
  def __init__(self, device):
      """Initialize UART from provided bluez device."""
      # Find the UART service and characteristics associated with the device.
      self._uart = device.find_service(self.UART_SERVICE_UUID)
      print self._uart
      self._queue = Queue.Queue()
      r = device.is_paired
      print "paired?", r
      if not r:
        print "pairing..."
        # help(device._device)
        # help(device._device.Pair)
        device.pair( )
        # device._device.Pair( )
        print "paired"
        print device.advertised
        print "finding service"
        self._uart = device.find_service(self.UART_SERVICE_UUID)
        print "SERVICE", self._uart
      for svc in device.list_services( ):
        print svc.uuid, svc.uuid == self.UART_SERVICE_UUID, svc, svc._service
        print "CHARACTERISTICS"
        chrsts = svc.list_characteristics( )
        for chtr in chrsts:
          print chtr.uuid, chtr, chtr._characteristic
      # print device.list_services( )
      self.setup_dexcom( )
      self.pair_auth_code(SERIAL)
  def pair_auth_code (self, serial):
      print "sending auth code"
      self._auth = self._uart.find_characteristic(Attrs.AuthenticationCode2)
      print self._auth
      # self._auth.
      msg = bytearray(serial + "000000")
      self._auth.write_value(str(msg))
      self._rx.start_notify(self._rx_received)
  def setup_dexcom (self):
    self._tx = self._uart.find_characteristic(self.TX_CHAR_UUID)
    self._rx = self._uart.find_characteristic(self.RX_CHAR_UUID)
    # Use a queue to pass data received from the RX property change back to
    # the main thread in a thread-safe way.
    self._heartbeat = self._uart.find_characteristic(self.HEARTBEAT_UUID)
    self._heartbeat.start_notify(self._heartbeat_tick)
  def _heartbeat_tick (self, data):
    print "_heartbeat_tick", data


class BothShare (ShareUART):
  ADVERTISED = ShareUART.ADVERTISED + Share2UART.ADVERTISED
  # SERVICES = [Attrs.DeviceService]
  SERVICES =  ShareUART.SERVICES + Share2UART.SERVICES
  CHARACTERISTICS =  ShareUART.SERVICES + Share2UART.SERVICES
  

  UART_SERVICE_UUID = Attrs.CradleService2
  TX_CHAR_UUID = Attrs.Command2
  RX_CHAR_UUID = Attrs.Response2
  pass

class UART (Share2UART):
  pass
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


SERIAL="SM53306551"

def got_gatt_services (self):
  print "services"

# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.

    print device.name
    # device._device.Pair( )
    print ble._print_tree( )
    for service in device.list_services( ):
      print service, service.uuid
    print "ADVERTISED"
    print device.advertised
    # device.connectProfile(str(device.advertised[-1]))
    # print device.gatt_services
    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        # print device._device.GattServices
        print('Discovering services...')
        UART.discover(device)
        # UART.find_device(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        uart = UART(device)

        # Write a string to the TX characteristic.
        # uart.write('Hello world!\r\n')
        print("Sent 'Hello world!' to the device.")

        # Now wait up to one minute to receive data from the device.
        print('Waiting up to 60 seconds to receive data from the device...')
        received = None
        # received = uart.read(timeout_sec=60)
        if received is not None:
            # Received data, print it out.
            print('Received: {0}'.format(received))
        else:
            # Timeout waiting for data, None is returned.
            print('Received no data!')
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()


# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
