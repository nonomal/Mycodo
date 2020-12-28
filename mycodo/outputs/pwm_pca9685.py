# coding=utf-8
#
# pwm_pca9685.py - Output for PCA9685
#
import copy

from flask_babel import lazy_gettext
from sqlalchemy import and_

from mycodo.databases.models import DeviceMeasurements
from mycodo.databases.models import OutputChannel
from mycodo.outputs.base_output import AbstractOutput
from mycodo.utils.database import db_retrieve_table_daemon
from mycodo.utils.influx import add_measurements_influxdb
from mycodo.utils.influx import read_last_influxdb
from mycodo.utils.system_pi import return_measurement_info


def constraints_pass_duty_cycle(mod_dev, value):
    """
    Check if the user input is acceptable
    :param mod_dev: SQL object with user-saved Input options
    :param value: float or int
    :return: tuple: (bool, list of strings)
    """
    errors = []
    all_passed = True
    if 100 < value < 0:
        all_passed = False
        errors.append("Must be a positive value")
    return all_passed, errors, mod_dev


def constraints_pass_hertz(mod_dev, value):
    """
    Check if the user input is acceptable
    :param mod_dev: SQL object with user-saved Input options
    :param value: float or int
    :return: tuple: (bool, list of strings)
    """
    errors = []
    all_passed = True
    if 1600 < value < 40:
        all_passed = False
        errors.append("Must be a value between 40 and 1600")
    return all_passed, errors, mod_dev


# Measurements
measurements_dict = {
    0: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    1: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    2: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    3: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    4: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    5: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    6: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    7: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    8: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    9: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    10: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    11: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    12: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    13: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    14: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    },
    15: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    }
}

channels_dict = {
    0: {
        'types': ['pwm'],
        'measurements': [0]
    },
    1: {
        'types': ['pwm'],
        'measurements': [1]
    },
    2: {
        'types': ['pwm'],
        'measurements': [2]
    },
    3: {
        'types': ['pwm'],
        'measurements': [3]
    },
    4: {
        'types': ['pwm'],
        'measurements': [4]
    },
    5: {
        'types': ['pwm'],
        'measurements': [5]
    },
    6: {
        'types': ['pwm'],
        'measurements': [6]
    },
    7: {
        'types': ['pwm'],
        'measurements': [7]
    },
    8: {
        'types': ['pwm'],
        'measurements': [8]
    },
    9: {
        'types': ['pwm'],
        'measurements': [9]
    },
    10: {
        'types': ['pwm'],
        'measurements': [10]
    },
    11: {
        'types': ['pwm'],
        'measurements': [11]
    },
    12: {
        'types': ['pwm'],
        'measurements': [12]
    },
    13: {
        'types': ['pwm'],
        'measurements': [13]
    },
    14: {
        'types': ['pwm'],
        'measurements': [14]
    },
    15: {
        'types': ['pwm'],
        'measurements': [15]
    }
}

# Output information
OUTPUT_INFORMATION = {
    'output_name_unique': 'pwm_pca9685',
    'output_name': "PCA9685 (16 channels): {}".format(lazy_gettext('PWM')),
    'output_library': 'adafruit-pca9685',
    'measurements_dict': measurements_dict,
    'channels_dict': channels_dict,
    'output_types': ['pwm'],

    'url_manufacturer': 'https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/ic-led-controllers/16-channel-12-bit-pwm-fm-plus-ic-bus-led-controller:PCA9685',
    'url_datasheet': 'https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf',
    'url_product_purchase': 'https://www.adafruit.com/product/815',

    'message': 'The PCA9685 can output a PWM signal to 16 channels at a frequency between 40 and 1600 Hz.',

    'options_enabled': [
        'i2c_location',
        'button_send_duty_cycle'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'Adafruit_PCA9685', 'adafruit-pca9685')
    ],

    'interfaces': ['I2C'],
    'i2c_location': [
        '0x40', '0x41', '0x42', '0x43', '0x44', '0x45', '0x46', '0x47',
        '0x48', '0x49', '0x4a', '0x4b', '0x4c', '0x4d', '0x4e', '0x4f'
    ],
    'i2c_address_editable': False,
    'i2c_address_default': '0x40',

    'custom_channel_options': [
        {
            'id': 'pwm_hertz',
            'type': 'integer',
            'default_value': 1600,
            'required': True,
            'constraints_pass': constraints_pass_hertz,
            'name': lazy_gettext('Frequency (Hertz)'),
            'phrase': 'The Herts to output the PWM signal (40 - 1600)'
        }
    ],

    'custom_channel_options': [
        {
            'id': 'state_startup',
            'type': 'select',
            'default_value': '',
            'options_select': [
                (-1, 'Do Nothing'),
                (0, 'Off'),
                ('set_duty_cycle', 'User Set Value'),
                ('last_duty_cycle', 'Last Known Value')
            ],
            'name': lazy_gettext('Startup State'),
            'phrase': lazy_gettext('Set the state when Mycodo starts')
        },
        {
            'id': 'startup_value',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_duty_cycle,
            'name': lazy_gettext('Startup Value'),
            'phrase': lazy_gettext('The value when Mycodo starts')
        },
        {
            'id': 'state_shutdown',
            'type': 'select',
            'default_value': '',
            'options_select': [
                (-1, 'Do Nothing'),
                (0, 'Off'),
                ('set_duty_cycle', 'User Set Value')
            ],
            'name': lazy_gettext('Shutdown State'),
            'phrase': lazy_gettext('Set the state when Mycodo shuts down')
        },
        {
            'id': 'shutdown_value',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_duty_cycle,
            'name': lazy_gettext('Shutdown Value'),
            'phrase': lazy_gettext('The value when Mycodo shuts down')
        },
        {
            'id': 'pwm_invert_signal',
            'type': 'bool',
            'default_value': False,
            'name': lazy_gettext('Invert Signal'),
            'phrase': lazy_gettext('Invert the PWM signal')
        },
        {
            'id': 'trigger_functions_startup',
            'type': 'bool',
            'default_value': False,
            'name': lazy_gettext('Trigger Functions at Startup'),
            'phrase': lazy_gettext('Whether to trigger functions when the output switches at startup')
        },
        {
            'id': 'amps',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'name': lazy_gettext('Current (Amps)'),
            'phrase': lazy_gettext('The current draw of the device being controlled')
        }
    ]
}


class OutputModule(AbstractOutput):
    """
    An output support class that operates an output
    """
    def __init__(self, output, testing=False):
        super(OutputModule, self).__init__(output, testing=testing, name=__name__)

        self.pwm_duty_cycles = {}
        for i in range(16):
            self.pwm_duty_cycles[i] = 0
        self.pwm_output = None
        self.pwm_hertz = None

        self.setup_custom_options(
            OUTPUT_INFORMATION['custom_options'], output)

        output_channels = db_retrieve_table_daemon(
            OutputChannel).filter(OutputChannel.output_id == self.output.unique_id).all()
        self.options_channels = self.setup_custom_channel_options_json(
            OUTPUT_INFORMATION['custom_channel_options'], output_channels)

    def setup_output(self):
        import Adafruit_PCA9685

        error = []
        if self.options_channels['pwm_hertz'][0] < 40:
            error.append("PWM Hertz must be a value between 40 and 1600")
        if error:
            for each_error in error:
                self.logger.error(each_error)
            return

        try:
            self.pwm_output = Adafruit_PCA9685.PCA9685(
                address=int(str(self.output.i2c_location), 16),
                busnum=self.output.i2c_bus)
                
            self.pwm_output.set_pwm_freq(self.pwm_hertz)

            self.output_setup = True
            self.logger.info("Output setup on bus {} at {}".format(
                self.output.i2c_bus, self.output.i2c_location))

            for i in range(16):
                if self.options_channels['state_startup'][i] == 0:
                    self.output_switch('off')
                elif self.options_channels['state_startup'][i] == 'set_duty_cycle':
                    self.output_switch('on', amount=self.options_channels['startup_value'][i])
                elif self.options_channels['state_startup'][i] == 'last_duty_cycle':
                    device_measurement = db_retrieve_table_daemon(DeviceMeasurements).filter(
                        and_(DeviceMeasurements.device_id == self.unique_id,
                             DeviceMeasurements.channel == i)).first()

                    last_measurement = None
                    if device_measurement:
                        channel, unit, measurement = return_measurement_info(device_measurement, None)
                        last_measurement = read_last_influxdb(
                            self.unique_id,
                            unit,
                            channel,
                            measure=measurement,
                            duration_sec=None)

                    if last_measurement:
                        self.logger.info(
                            "Setting channel {ch} startup duty cycle to last known value of {dc} %".format(
                                ch=i, dc=last_measurement[1]))
                        self.output_switch('on', amount=last_measurement[1])
                    else:
                        self.logger.error(
                            "Output channel {} instructed at startup to be set to "
                            "the last known duty cycle, but a last known "
                            "duty cycle could not be found in the measurement "
                            "database".format(i))
        except Exception as except_msg:
            self.logger.exception("Output was unable to be setup: {err}".format(err=except_msg))

    def output_switch(self, state, output_type=None, amount=None, output_channel=None):
        measure_dict = copy.deepcopy(measurements_dict)

        if state == 'on':
            if self.options_channels['pwm_invert_signal'][output_channel]:
                amount = 100.0 - abs(amount)
        elif state == 'off':
            if self.options_channels['pwm_invert_signal'][output_channel]:
                amount = 100
            else:
                amount = 0

        self.pwm_output.set_pwm(self.options_channels['pwm_hertz'][output_channel], amount)
        self.pwm_duty_cycles[output_channel] = amount

        measure_dict[output_channel]['value'] = amount
        add_measurements_influxdb(self.unique_id, measure_dict)

        self.logger.debug("Duty cycle of channel {ch} set to {dc:.2f} %".format(
            ch=output_channel, dc=amount))
        return "success"

    def is_on(self, output_channel=None):
        if self.is_setup():
            duty_cycle = self.pwm_duty_cycles[output_channel]

            if duty_cycle > 0:
                return duty_cycle

            return False

    def is_setup(self):
        return self.output_setup

    def stop_output(self):
        """ Called when Output is stopped """
        for i in range(16):
            if self.options_channels['state_shutdown'][i] == 0:
                self.output_switch('off')
            elif self.options_channels['state_shutdown'][i] == 'set_duty_cycle':
                self.output_switch('on', amount=self.options_channels['shutdown_value'][i])
        self.running = False
