



import uuid

# import dbus
import pydbus

from ..interfaces import GattService, GattCharacteristic, GattDescriptor
from ..platform import get_provider


_SERVICE_INTERFACE        = 'org.bluez.GattService1'
_CHARACTERISTIC_INTERFACE = 'org.bluez.GattCharacteristic1'
_DESCRIPTOR_INTERFACE     = 'org.bluez.GattDescriptor1'


class BluezGattService(GattService):
    """Bluez GATT service object."""

    def __init__(self, dbus_obj):
        """Create an instance of the GATT service from the provided bluez
        DBus object.
        """
        self._service = dbus_obj[_SERVICE_INTERFACE]
        self._props = dbus_obj['org.freedesktop.DBus.Properties']

    @property
    def uuid(self):
        """Return the UUID of this GATT service."""
        return uuid.UUID(str(self._props.Get(_SERVICE_INTERFACE, 'UUID')[0]))

    def list_characteristics(self):
        """Return list of GATT characteristics that have been discovered for this
        service.
        """
        paths = self._props.Get(_SERVICE_INTERFACE, 'Characteristics')[0]
        print 'chars list', paths
        return map(BluezGattCharacteristic,
                   get_provider()._get_objects_by_path(paths))


class BluezGattCharacteristic(GattCharacteristic):
    """Bluez GATT characteristic object."""

    def __init__(self, dbus_obj):
        """Create an instance of the GATT characteristic from the provided bluez
        DBus object.
        """
        self._characteristic = dbus_obj[_CHARACTERISTIC_INTERFACE]
        self._props = dbus_obj['org.freedesktop.DBus.Properties']

    @property
    def uuid(self):
        """Return the UUID of this GATT characteristic."""
        return uuid.UUID(str(self._props.Get(_CHARACTERISTIC_INTERFACE, 'UUID')[0]))

    @property
    def notifying (self):
        """
          True, if notifications or indications on this
          characteristic are currently enabled.
        """
        return self._props.Get(_CHARACTERISTIC_INTERFACE, 'Notifying')[0]

    @property
    def flags (self):
        """
      Defines how the characteristic value can be used. See
      Core spec "Table 3.5: Characteristic Properties bit
      field", and "Table 3.8: Characteristic Extended
      Properties bit field". Allowed values:

        "broadcast"
        "read"
        "write-without-response"
        "write"
        "notify"
        "indicate"
        "authenticated-signed-writes"
        "reliable-write"
        "writable-auxiliaries"
        "encrypt-read"
        "encrypt-write"
        "encrypt-authenticated-read"
        "encrypt-authenticated-write"

        """
        print self._props.Get(_CHARACTERISTIC_INTERFACE, 'Flags')
        return self._props.Get(_CHARACTERISTIC_INTERFACE, 'Flags')


    def read_value(self):
        """Read the value of this characteristic."""
        return self._characteristic.ReadValue()

    def write_value(self, value):
        """Write the specified value to this characteristic."""
        self._characteristic.WriteValue(value)

    def start_notify(self, on_change):
        """Enable notification of changes for this characteristic on the
        specified on_change callback.  on_change should be a function that takes
        one parameter which is the value (as a string of bytes) of the changed
        characteristic value.
        """
        # Setup a closure to be the first step in handling the on change callback.
        # This closure will verify the characteristic is changed and pull out the
        # new value to pass to the user's on change callback.
        def characteristic_changed(iface, changed_props, invalidated_props):
            # Check that this change is for a GATT characteristic and it has a
            # new value.
            if iface != _CHARACTERISTIC_INTERFACE:
                return
            if 'Value' not in changed_props:
                return
            # Send the new value to the on_change callback.
            on_change(''.join(map(chr, changed_props['Value'])))
        # Hook up the property changed signal to call the closure above.
        # self._props.connect_to_signal('PropertiesChanged', characteristic_changed)
        self._props.PropertiesChanged.connect(characteristic_changed)
        # Enable notifications for changes on the characteristic.
        self._characteristic.StartNotify()

    def stop_notify(self):
        """Disable notification of changes for this characteristic."""
        self._characteristic.StopNotify()

    def list_descriptors(self):
        """Return list of GATT descriptors that have been discovered for this
        characteristic.
        """
        paths = self._props.Get(_CHARACTERISTIC_INTERFACE, 'Descriptors')
        print paths
        return map(BluezGattDescriptor,
                   get_provider()._get_objects_by_path(paths))


class BluezGattDescriptor(GattDescriptor):
    """Bluez GATT descriptor object."""

    def __init__(self, dbus_obj):
        """Create an instance of the GATT descriptor from the provided bluez
        DBus object.
        """
        self._descriptor = dbus_obj[_DESCRIPTOR_INTERFACE]
        self._props = dbus_obj['org.freedesktop.DBus.Properties']

    @property
    def uuid(self):
        """Return the UUID of this GATT descriptor."""
        return uuid.UUID(str(self._props.Get(_DESCRIPTOR_INTERFACE, 'UUID')[0]))

    def read_value(self):
        """Read the value of this descriptor."""
        return self._descriptor.ReadValue()
