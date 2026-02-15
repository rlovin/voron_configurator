from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'voron-configurator-secret-key'

# Configuration definitions - Based on LDO Kits
PRINTERS = {
    'voron2.4': {
        'name': 'Voron 2.4',
        'sizes': {
            '250': {'name': '250mm', 'bed_size': [250, 250, 250]},
            '300': {'name': '300mm', 'bed_size': [300, 300, 300]},
            '350': {'name': '350mm', 'bed_size': [350, 350, 350]},
        }
    },
    'trident': {
        'name': 'Voron Trident',
        'sizes': {
            '250': {'name': '250mm', 'bed_size': [250, 250, 250]},
            '300': {'name': '300mm', 'bed_size': [300, 300, 300]},
            '350': {'name': '350mm', 'bed_size': [350, 350, 350]},
        }
    }
}

# Main Board Configurations
MAIN_BOARDS = {
    'leviathan': {
        'name': 'LDO Leviathan',
        'mcu': 'stm32f446',
        'serial_port': '/dev/serial/by-id/usb-Klipper_stm32f446xx_',
        'heater_pins': {'bed': 'PG11', 'extruder': 'PG10'},
        'fan_pins': {'part_cooling': 'PB7', 'hotend': 'PB3', 'controller': 'PF7'},
        'endstop_pins': {'x': 'PC1', 'y': 'PC2', 'z': 'PC3'},
        'probe_pin': 'PF1',
        # X/Y use HV steppers with TMC5160 (SPI)
        'xy_driver_type': 'tmc5160',
        'xy_spi_bus': 'spi4',
        'stepper_pins': {
            # HV-STEPPER-0 (X) - TMC5160
            'x': {'step': 'PB10', 'dir': 'PB11', 'enable': 'PG0', 'cs': 'PE15'},
            # HV-STEPPER-1 (Y) - TMC5160
            'y': {'step': 'PF15', 'dir': 'PF14', 'enable': 'PE9', 'cs': 'PE11'},
            # STEPPER-0 (Z) - TMC2209
            'z': {'step': 'PD4', 'dir': 'PD3', 'enable': 'PD7', 'uart': 'PD5'},
            # STEPPER-1 (Z1) - TMC2209
            'z1': {'step': 'PC12', 'dir': 'PC11', 'enable': 'PD2', 'uart': 'PD0'},
            # STEPPER-2 (Z2) - TMC2209
            'z2': {'step': 'PC9', 'dir': 'PC8', 'enable': 'PC10', 'uart': 'PA8'},
            # STEPPER-3 (Z3) - TMC2209
            'z3': {'step': 'PG7', 'dir': 'PG6', 'enable': 'PC7', 'uart': 'PG8'},
            # STEPPER-4 (Extruder) - TMC2209
            'extruder': {'step': 'PD10', 'dir': 'PD9', 'enable': 'PD13', 'uart': 'PD11'},
        },
    },
    'octopus_v1': {
        'name': 'BTT Octopus V1.1',
        'mcu': 'stm32f446',
        'serial_port': '/dev/serial/by-id/usb-Klipper_stm32f446xx_',
        'heater_pins': {'bed': 'PA0', 'extruder': 'PA2'},
        'fan_pins': {'part_cooling': 'PA8', 'hotend': 'PE5', 'controller': 'PB4'},
        'endstop_pins': {'x': 'PG6', 'y': 'PG9', 'z': 'PG12'},
        'probe_pin': 'PA3',
        # Stepper pins for Octopus V1.1
        'stepper_pins': {
            'x': {'step': 'PF13', 'dir': 'PF12', 'enable': 'PF14', 'uart': 'PC4'},
            'y': {'step': 'PG0', 'dir': 'PG1', 'enable': 'PF15', 'uart': 'PD11'},
            'z': {'step': 'PF11', 'dir': 'PG3', 'enable': 'PG5', 'uart': 'PC6'},
            'z1': {'step': 'PG4', 'dir': 'PC1', 'enable': 'PA2', 'uart': 'PC7'},
            'z2': {'step': 'PF9', 'dir': 'PF10', 'enable': 'PG2', 'uart': 'PF2'},
            'z3': {'step': 'PC13', 'dir': 'PF0', 'enable': 'PF1', 'uart': 'PE4'},
            'extruder': {'step': 'PE2', 'dir': 'PE3', 'enable': 'PD5', 'uart': 'PE1'},
        },
    },
    'octopus_pro': {
        'name': 'BTT Octopus Pro',
        'mcu': 'stm32f446',
        'serial_port': '/dev/serial/by-id/usb-Klipper_stm32f446xx_',
        'heater_pins': {'bed': 'PA0', 'extruder': 'PA2'},
        'fan_pins': {'part_cooling': 'PA8', 'hotend': 'PE5', 'controller': 'PB4'},
        'endstop_pins': {'x': 'PG6', 'y': 'PG9', 'z': 'PG12'},
        'probe_pin': 'PA3',
        # Same pinout as Octopus V1.1
        'stepper_pins': {
            'x': {'step': 'PF13', 'dir': 'PF12', 'enable': 'PF14', 'uart': 'PC4'},
            'y': {'step': 'PG0', 'dir': 'PG1', 'enable': 'PF15', 'uart': 'PD11'},
            'z': {'step': 'PF11', 'dir': 'PG3', 'enable': 'PG5', 'uart': 'PC6'},
            'z1': {'step': 'PG4', 'dir': 'PC1', 'enable': 'PA2', 'uart': 'PC7'},
            'z2': {'step': 'PF9', 'dir': 'PF10', 'enable': 'PG2', 'uart': 'PF2'},
            'z3': {'step': 'PC13', 'dir': 'PF0', 'enable': 'PF1', 'uart': 'PE4'},
            'extruder': {'step': 'PE2', 'dir': 'PE3', 'enable': 'PD5', 'uart': 'PE1'},
        },
    },
    'spider_v23': {
        'name': 'Fysetc Spider V2.3',
        'mcu': 'stm32f446',
        'serial_port': '/dev/serial/by-id/usb-Klipper_stm32f446xx_',
        'heater_pins': {'bed': 'PB7', 'extruder': 'PB6'},
        'fan_pins': {'part_cooling': 'PB5', 'hotend': 'PB4', 'controller': 'PB3'},
        'endstop_pins': {'x': 'PB14', 'y': 'PB13', 'z': 'PA0'},
        'probe_pin': 'PA3',
        # Stepper pins for Spider V2.3
        'stepper_pins': {
            'x': {'step': 'PE11', 'dir': 'PE10', 'enable': 'PE9', 'uart': 'PE8'},
            'y': {'step': 'PE14', 'dir': 'PE13', 'enable': 'PE12', 'uart': 'PC15'},
            'z': {'step': 'PE0', 'dir': 'PB9', 'enable': 'PE8', 'uart': 'PC14'},
            'z1': {'step': 'PB8', 'dir': 'PC7', 'enable': 'PB6', 'uart': 'PA15'},
            'z2': {'step': 'PC6', 'dir': 'PB5', 'enable': 'PB4', 'uart': 'PA14'},
            'z3': {'step': 'PF6', 'dir': 'PF5', 'enable': 'PF4', 'uart': 'PF3'},
            'extruder': {'step': 'PC0', 'dir': 'PF1', 'enable': 'PF0', 'uart': 'PC13'},
        },
    },
    'manta_m8p': {
        'name': 'BTT Manta M8P',
        'mcu': 'stm32g0b1',
        'serial_port': '/dev/serial/by-id/usb-Klipper_stm32g0b1xx_',
        'heater_pins': {'bed': 'PA0', 'extruder': 'PA1'},
        'fan_pins': {'part_cooling': 'PA2', 'hotend': 'PA3', 'controller': 'PA4'},
        'endstop_pins': {'x': 'PB4', 'y': 'PB3', 'z': 'PA15'},
        'probe_pin': 'PA8',
        # Stepper pins for Manta M8P
        'stepper_pins': {
            'x': {'step': 'PD0', 'dir': 'PD1', 'enable': 'PD2', 'uart': 'PD3'},
            'y': {'step': 'PD4', 'dir': 'PD5', 'enable': 'PD6', 'uart': 'PD7'},
            'z': {'step': 'PD8', 'dir': 'PD9', 'enable': 'PD10', 'uart': 'PD11'},
            'z1': {'step': 'PD12', 'dir': 'PD13', 'enable': 'PD14', 'uart': 'PD15'},
            'z2': {'step': 'PE0', 'dir': 'PE1', 'enable': 'PE2', 'uart': 'PE3'},
            'z3': {'step': 'PE4', 'dir': 'PE5', 'enable': 'PE6', 'uart': 'PC13'},
            'extruder': {'step': 'PC0', 'dir': 'PC1', 'enable': 'PC2', 'uart': 'PC3'},
        },
    },
}

TOOLHEAD_BOARDS = {
    'nitehawk': {
        'name': 'LDO Nitehawk',
        'serial_port': '/dev/serial/by-id/usb-Klipper_rp2040_',
        'mcu': 'rp2040',
        # Nitehawk-36 Pin Mapping (RP2040 GPIO pins)
        'heater_pin': 'gpio9',           # HE0
        'thermistor_pin': 'gpio29',       # TH0
        'fan_pins': {
            'part_cooling': 'gpio6',     # PC_FAN (Part Cooling)
            'hotend': 'gpio5',           # HEF (Hotend Fan with tachometer)
        },
        'probe_pin': 'gpio10',           # PRB (Probe)
        'filament_sensor': 'gpio3',       # Filament sensor
        'stepper_pins': {
            'step': 'gpio23',            # E_STEP
            'dir': 'gpio24',             # E_DIR
            'enable': 'gpio25',          # E_EN (active low)
            'uart': 'gpio0',             # E_UART
            'tx': 'gpio1',               # E_TX
        },
        'accelerometer_pins': {
            'cs': 'gpio27',
            'clk': 'gpio18',
            'mosi': 'gpio20',
            'miso': 'gpio19',
        },
        'endstop_pins': {
            'x': 'gpio13',               # X_ENDSTOP
            'y': 'gpio12',               # Y_ENDSTOP
        },
    },
    'ebb_sb2209': {
        'name': 'BTT EBB SB2209 (RP2040)',
        'serial_port': '/dev/serial/by-id/usb-Klipper_rp2040_',
        'mcu': 'rp2040',
        'connection': 'canbus',
        'canbus_uuid': 'ebb2209',  # Placeholder - user must update
        # BTT EBB SB2209 Pin Mapping (RP2040 GPIO pins)
        'heater_pin': 'gpio9',           # HE0 (Hotend Heater)
        'thermistor_pin': 'gpio29',       # TH0 (Hotend Thermistor)
        'fan_pins': {
            'part_cooling': 'gpio6',     # FAN0 (Part Cooling Fan)
            'hotend': 'gpio5',           # FAN1 (Hotend Fan)
        },
        'probe_pin': 'gpio10',           # PROBE (Tap/Beacon/Probe)
        'filament_sensor': 'gpio3',       # FILAMENT (Filament Runout Sensor)
        'stepper_pins': {
            'step': 'gpio23',            # E_STEP (Extruder Step)
            'dir': 'gpio24',             # E_DIR (Extruder Direction)
            'enable': 'gpio25',          # E_EN (Extruder Enable, active low)
            'uart': 'gpio0',             # E_UART (TMC2209 UART)
            'tx': 'gpio1',               # E_TX (TMC2209 UART TX)
        },
        'accelerometer_pins': {
            'cs': 'gpio21',              # ADXL345 CS
            'clk': 'gpio18',             # ADXL345 SCK/CLK
            'mosi': 'gpio20',            # ADXL345 MOSI/SDA
            'miso': 'gpio19',            # ADXL345 MISO/SDO
        },
        'endstop_pins': {
            'x': 'gpio16',               # X_STOP (X Endstop on toolhead)
            'y': 'gpio17',               # Y_STOP (Y Endstop on toolhead)
        },
        'led_pin': 'gpio8',              # RGB LED
    },
    'ebb36': {
        'name': 'BTT EBB36 (RP2040)',
        'serial_port': '/dev/serial/by-id/usb-Klipper_rp2040_',
        'mcu': 'rp2040',
        'connection': 'canbus',
        'canbus_uuid': 'ebb36',  # Placeholder - user must update
        # BTT EBB36 Pin Mapping (RP2040 GPIO pins) - Universal 36mm mount
        'heater_pin': 'gpio9',           # HE0 (Hotend Heater)
        'thermistor_pin': 'gpio29',       # TH0 (Hotend Thermistor)
        'fan_pins': {
            'part_cooling': 'gpio6',     # FAN0 (Part Cooling Fan)
            'hotend': 'gpio5',           # FAN1 (Hotend Fan)
        },
        'probe_pin': 'gpio10',           # PROBE (Probe input)
        'filament_sensor': 'gpio3',       # FILAMENT (Filament Runout Sensor)
        'stepper_pins': {
            'step': 'gpio23',            # E_STEP (Extruder Step)
            'dir': 'gpio24',             # E_DIR (Extruder Direction)
            'enable': 'gpio25',          # E_EN (Extruder Enable, active low)
            'uart': 'gpio0',             # E_UART (TMC2209 UART)
            'tx': 'gpio1',               # E_TX (TMC2209 UART TX)
        },
        'accelerometer_pins': {
            'cs': 'gpio21',              # ADXL345 CS
            'clk': 'gpio18',             # ADXL345 SCK
            'mosi': 'gpio20',            # ADXL345 MOSI
            'miso': 'gpio19',            # ADXL345 MISO
        },
        'endstop_pins': {
            'x': 'gpio16',               # X_STOP (Optional X on toolhead)
            'y': 'gpio17',               # Y_STOP (Optional Y on toolhead)
        },
        'aux_pins': {
            'gpio2': 'gpio2',              # AUX1 (Spare GPIO)
            'gpio4': 'gpio4',              # AUX2 (Spare GPIO)
            'gpio7': 'gpio7',              # AUX3 (Spare GPIO)
        },
    },
}

EXTRUDERS = {
    'g2e_9t': {
        'name': 'G2E Extruder (9:1 Ratio)',
        'type': 'g2e',
        'gear_ratio': '9:1',
        'rotation_distance': '47.088',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.04',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'g2e_21t': {
        'name': 'G2E Extruder (21:1 Ratio)',
        'type': 'g2e',
        'gear_ratio': '21:1',
        'rotation_distance': '107.76',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.04',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'bondtech_lgx_lite': {
        'name': 'Bondtech LGX Lite',
        'type': 'bondtech',
        'gear_ratio': '5.8:1',
        'rotation_distance': '47.088',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.025',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.65',
        'motor': 'ldo_36mm',
    },
    'bondtech_lgx': {
        'name': 'Bondtech LGX (Large)',
        'type': 'bondtech',
        'gear_ratio': '6.2:1',
        'rotation_distance': '50.00',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.025',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.65',
        'motor': 'ldo_36mm',
    },
    'bondtech_cw2': {
        'name': 'Bondtech Clockwork 2',
        'type': 'bondtech',
        'gear_ratio': '5:1',
        'rotation_distance': '47.088',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.025',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'bondtech_cw1': {
        'name': 'Bondtech Clockwork 1',
        'type': 'bondtech',
        'gear_ratio': '50:10',
        'rotation_distance': '47.088',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.035',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'ldo_orbiter_v1_5': {
        'name': 'LDO Orbiter v1.5',
        'type': 'ldo',
        'gear_ratio': '7.5:1',
        'rotation_distance': '42.0',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.03',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'ldo_orbiter_v2_std': {
        'name': 'LDO Orbiter v2.0 (Standard)',
        'type': 'ldo',
        'gear_ratio': '10.0:1',
        'rotation_distance': '53.5',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.025',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
    'ldo_orbiter_v2_tbg': {
        'name': 'LDO Orbiter v2.0 (TBG)',
        'type': 'ldo',
        'gear_ratio': '10.0:1',
        'rotation_distance': '53.5',
        'nozzle_diameter': '0.400',
        'filament_diameter': '1.750',
        'max_extrude_only_distance': '200.0',
        'max_extrude_only_velocity': '120.0',
        'pressure_advance': '0.025',
        'pressure_advance_smooth_time': '0.040',
        'default_motor_current': '0.6',
        'motor': 'ldo_36mm',
    },
}

# LDO Kit Motor Specifications
MOTORS = {
    'ldo': {
        'name': 'LDO Standard Kit Motors',
        'x': {'current': '1.5', 'model': '42STH48-2504AC'},
        'y': {'current': '1.5', 'model': '42STH48-2504AC'},
        'z': {'current': '1.0', 'model': '42STH48-2004AC'},
        'extruder': {'current': '0.6', 'model': '36STH20-1004AHG'},
    }
}

PROBES = {
    'tap': {
        'name': 'Voron Tap',
        'type': 'probe',
        'pin': '^probe_pin',
    },
    'beacon': {
        'name': 'Beacon Probe',
        'type': 'beacon',
        'serial_port': '/dev/serial/by-id/usb-Beacon_',
    }
}

THEMES = {
    'crimson': {
        'name': 'Crimson',
        'primary': '#E63946',
        'background': '#1A1A2E',
        'surface': '#16213E',
        'card': '#0F3460',
        'text': '#E94560',
        'text-secondary': '#A8DADC',
        'border': '#2C3E50',
    },
    'forest': {
        'name': 'Forest',
        'primary': '#2ECC71',
        'background': '#0F291E',
        'surface': '#1A4231',
        'card': '#265C47',
        'text': '#E8F6EF',
        'text-secondary': '#95D5B2',
        'border': '#40916C',
    },
    'nebula': {
        'name': 'Nebula',
        'primary': '#9D4EDD',
        'background': '#10002B',
        'surface': '#240046',
        'card': '#3C096C',
        'text': '#E0AAFF',
        'text-secondary': '#C77DFF',
        'border': '#5A189A',
    },
    'amber': {
        'name': 'Amber',
        'primary': '#F77F00',
        'background': '#1C1917',
        'surface': '#292524',
        'card': '#44403C',
        'text': '#FDBA74',
        'text-secondary': '#D6D3D1',
        'border': '#57534E',
    },
    'arctic': {
        'name': 'Arctic',
        'primary': '#00B4D8',
        'background': '#0D1B2A',
        'surface': '#1B263B',
        'card': '#415A77',
        'text': '#E0E1DD',
        'text-secondary': '#778DA9',
        'border': '#415A77',
    },
    'voron': {
        'name': 'Voron (Red/Black)',
        'primary': '#E30613',  # Voron Red
        'background': '#1A1A1A',  # Dark Charcoal (was #0A0A0A)
        'surface': '#252525',  # Lighter Surface (was #141414)
        'card': '#333333',  # Lighter Card (was #1E1E1E)
        'text': '#FF4444',  # Bright Red (was #FF1A1A)
        'text-secondary': '#AAAAAA',  # Lighter Gray (was #888888)
        'border': '#444444',  # Lighter Border (was #333333)
    }
}

# Better Print Start Macro Options
PRINT_START_OPTIONS = {
    'standard': {
        'name': 'Standard LDO Kit Macro',
        'description': 'Simple heating and priming sequence'
    },
    'better': {
        'name': 'Better Print Start (Ellis)',
        'description': 'Enhanced macro with chamber heat soak, adaptive mesh, and smart priming'
    }
}

# LDO Official Reference Configs from GitHub
LDO_REFERENCE_CONFIGS = {
    'voron2.4': {
        'leviathan': {
            'rev_d': {
                'name': 'Leviathan Rev D',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoron2/main/Firmware/leviathan-printer-rev-d.cfg',
                'description': 'Latest LDO Leviathan config for Voron 2.4'
            }
        },
        'octopus': {
            'rev_c': {
                'name': 'Octopus Rev C',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoron2/main/Firmware/octopus-printer-rev-c.cfg',
                'description': 'Latest LDO Octopus config for Voron 2.4'
            },
            'rev_a': {
                'name': 'Octopus Rev A',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoron2/main/Firmware/octopus-printer-rev-a.cfg',
                'description': 'Legacy LDO Octopus config for Voron 2.4'
            }
        }
    },
    'trident': {
        'leviathan': {
            'rev_d': {
                'name': 'Leviathan Rev D',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoronTrident/master/Firmware/printer-leviathan-rev-d.cfg',
                'description': 'Latest LDO Leviathan config for Trident'
            }
        },
        'octopus': {
            'rev_c': {
                'name': 'Octopus Rev C',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoronTrident/master/Firmware/printer-octopus-rev-c.cfg',
                'description': 'Latest LDO Octopus config for Trident'
            },
            'rev_a': {
                'name': 'Octopus Rev A',
                'url': 'https://raw.githubusercontent.com/MotorDynamicsLab/LDOVoronTrident/master/Firmware/printer-octopus-rev-a.cfg',
                'description': 'Legacy LDO Octopus config for Trident'
            }
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html', 
                         printers=PRINTERS, 
                         main_boards=MAIN_BOARDS,
                         toolhead_boards=TOOLHEAD_BOARDS,
                         motors=MOTORS,
                         probes=PROBES,
                         extruders=EXTRUDERS,
                         themes=THEMES,
                         print_start_options=PRINT_START_OPTIONS,
                         ldo_reference_configs=LDO_REFERENCE_CONFIGS,
                         default_theme='arctic')

@app.route('/api/generate', methods=['POST'])
def generate_config():
    data = request.json
    
    printer_type = data.get('printer', 'voron2.4')
    size = data.get('size', '300')
    main_board_id = data.get('main_board', 'leviathan')
    toolhead_board_id = data.get('toolhead_board', 'nitehawk')
    motor_kit = data.get('motors', 'ldo')
    probe_type = data.get('probe', 'tap')
    print_start_type = data.get('print_start', 'standard')
    extruder_type = data.get('extruder', 'g2e_9t')
    
    # Get selected options
    printer = PRINTERS.get(printer_type, PRINTERS['voron2.4'])
    printer_size = printer['sizes'].get(size, printer['sizes']['300'])
    main_board = MAIN_BOARDS.get(main_board_id, MAIN_BOARDS['leviathan'])
    toolhead_board = TOOLHEAD_BOARDS.get(toolhead_board_id, TOOLHEAD_BOARDS['nitehawk'])
    motor_config = MOTORS.get(motor_kit, MOTORS['ldo'])
    probe = PROBES.get(probe_type, PROBES['tap'])
    extruder_config = EXTRUDERS.get(extruder_type, EXTRUDERS['g2e_9t'])
    
    # Generate single comprehensive printer.cfg
    config_content = generate_comprehensive_cfg(
        printer, printer_size, main_board, toolhead_board, motor_config, probe, printer_type, print_start_type, extruder_config
    )
    
    return jsonify({
        'success': True,
        'config': config_content,
        'filename': 'printer.cfg',
        'metadata': {
            'printer': printer['name'],
            'size': printer_size['name'],
            'main_board': main_board['name'],
            'toolhead_board': toolhead_board['name'],
            'motors': motor_config['name'],
            'probe': probe['name'],
            'print_start': PRINT_START_OPTIONS.get(print_start_type, PRINT_START_OPTIONS['standard'])['name'],
            'generated_at': datetime.now().isoformat(),
        }
    })

@app.route('/api/download', methods=['POST'])
def download_config():
    data = request.json
    config = data.get('config', '')
    filename = data.get('filename', 'printer.cfg')
    
    memory_file = BytesIO()
    memory_file.write(config.encode('utf-8'))
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='text/plain',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/reference-configs', methods=['GET'])
def get_reference_configs():
    """Return ALL available LDO reference configs across all printer types and boards"""
    # Printer display names
    printer_names = {
        'voron2.4': '2.4',
        'trident': 'Trident'
    }
    
    # Aggregate ALL configs across all printer types and board types
    all_configs = {}
    
    for printer_type, printer_configs in LDO_REFERENCE_CONFIGS.items():
        printer_name = printer_names.get(printer_type, printer_type)
        
        for board_type, board_configs in printer_configs.items():
            for revision, config in board_configs.items():
                # Create a unique key that includes printer and board type
                key = f"{printer_type}_{board_type}_{revision}"
                # Prepend printer model to the name
                display_name = f"{printer_name} {config['name']}"
                all_configs[key] = {
                    'name': display_name,
                    'description': config['description'],
                    'url': config['url'],
                    'printer_type': printer_type,
                    'board_type': board_type,
                    'revision': revision
                }
    
    return jsonify({
        'success': True,
        'configs': all_configs
    })

@app.route('/api/reference-config', methods=['GET'])
def get_reference_config_content():
    """Fetch content of a specific LDO reference config from GitHub"""
    import urllib.request
    
    printer_type = request.args.get('printer', 'voron2.4')
    board_type = request.args.get('board', 'leviathan')
    revision = request.args.get('revision', 'rev_d')
    
    config_info = LDO_REFERENCE_CONFIGS.get(printer_type, {}).get(board_type, {}).get(revision)
    
    if not config_info:
        return jsonify({
            'success': False,
            'error': 'Config not found'
        }), 404
    
    try:
        with urllib.request.urlopen(config_info['url'], timeout=10) as response:
            content = response.read().decode('utf-8')
            return jsonify({
                'success': True,
                'content': content,
                'name': config_info['name'],
                'description': config_info['description']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reference/<printer>/<board>/<revision>')
def view_reference_config(printer, board, revision):
    """View LDO reference config in simplified standalone page"""
    import urllib.request
    
    config_info = LDO_REFERENCE_CONFIGS.get(printer, {}).get(board, {}).get(revision)
    
    if not config_info:
        return render_template('reference.html', 
                             error='Reference config not found',
                             config_content=None,
                             config_name=None,
                             config_description=None,
                             printer=printer,
                             board=board,
                             revision=revision)
    
    try:
        with urllib.request.urlopen(config_info['url'], timeout=10) as response:
            content = response.read().decode('utf-8')
            
            return render_template('reference.html',
                                 config_content=content,
                                 config_name=config_info['name'],
                                 config_description=config_info['description'],
                                 printer=printer,
                                 board=board,
                                 revision=revision,
                                 error=None)
    except Exception as e:
        return render_template('reference.html',
                             error=f'Failed to load config: {str(e)}',
                             config_content=None,
                             config_name=None,
                             config_description=None,
                             printer=printer,
                             board=board,
                             revision=revision)

def generate_xy_driver_config(axis, main_board, run_current):
    """Generate X/Y stepper driver configuration (TMC5160 for Leviathan, TMC2209 for others)"""
    axis_pins = main_board['stepper_pins'][axis]
    
    # Check if this board uses TMC5160 for XY (Leviathan)
    if main_board.get('xy_driver_type') == 'tmc5160':
        spi_bus = main_board.get('xy_spi_bus', 'spi4')
        return f"""[tmc5160 stepper_{axis}]
spi_bus: {spi_bus}
cs_pin: {axis_pins['cs']}
interpolate: false
run_current: {run_current}
sense_resistor: 0.075
stealthchop_threshold: 0"""
    else:
        # Standard TMC2209
        return f"""[tmc2209 stepper_{axis}]
uart_pin: {axis_pins['uart']}
interpolate: false
run_current: {run_current}
sense_resistor: 0.110
stealthchop_threshold: 0"""

def generate_comprehensive_cfg(printer, printer_size, main_board, toolhead_board, motor_config, probe, printer_type, print_start_type='standard', extruder_config=None):
    if extruder_config is None:
        extruder_config = EXTRUDERS['g2e_9t']  # Default to G2E 9:1
    
    bed_x, bed_y, bed_z = printer_size['bed_size']
    x_current = motor_config['x']['current']
    y_current = motor_config['y']['current']
    z_current = motor_config['z']['current']
    e_current = extruder_config['default_motor_current']
    
    probe_section = generate_probe_section(probe, bed_x, bed_y)
    z_section = generate_z_section(printer_type, bed_x, bed_y, bed_z, z_current, main_board)
    
    # Check if toolhead uses CAN bus
    is_canbus = toolhead_board.get('connection') == 'canbus'
    
    # Generate toolhead MCU section based on connection type
    if is_canbus:
        toolhead_mcu_section = f"""[mcu toolhead]
##  For CAN bus toolheads, find UUID with: python3 ~/klipper/scripts/canbus_query.py can0
canbus_uuid: {toolhead_board.get('canbus_uuid', 'update_me')}
# canbus_interface: can0
restart_method: command"""
    else:
        toolhead_mcu_section = f"""[mcu toolhead]
##  Obtain definition by "ls -l /dev/serial/by-id/" then unplug to verify
serial: {toolhead_board['serial_port']}
restart_method: command"""
    
    # Generate leveling section based on printer type
    if printer_type == 'voron2.4':
        # Calculate gantry corners and probe points based on bed size
        if bed_x == 250:
            gantry_corners = "    -60,-10\n    310, 260"
            probe_points = "    50,25\n    50,175\n    200,175\n    200,25"
        elif bed_x == 350:
            gantry_corners = "    -60,-10\n    410,360"
            probe_points = "    50,25\n    50,300\n    300,300\n    300,25"
        else:  # 300mm default
            gantry_corners = "    -60,-10\n    360,310"
            probe_points = "    50,25\n    50,255\n    255,255\n    255,25"
        
        leveling_section = f"""##  Use QUAD_GANTRY_LEVEL to level a gantry.
##  Min & Max gantry corners - measure from nozzle at MIN (0,0) and 
##  MAX ({bed_x}, {bed_y}) to respective belt positions
[quad_gantry_level]
gantry_corners:
{gantry_corners}
##  Probe points
points:
{probe_points}
speed: 100
horizontal_move_z: 10
retries: 5
retry_tolerance: 0.0075
max_adjust: 10"""
    else:  # Trident
        leveling_section = f"""##  Use Z_TILT_ADJUST to level a bed with independently controlled Z motors.
[z_tilt]
##--------------------------------------------------------------------
z_positions:
    -50, 18
    {bed_x / 2}, {bed_y + 50}
    {bed_x + 50}, 18
points:
    30, 30
    {bed_x / 2}, {bed_y - 30}
    {bed_x - 30}, 30
##--------------------------------------------------------------------
speed: 100
horizontal_move_z: 10
retries: 5
retry_tolerance: 0.0075

# Bed Screw Positions (for manual bed tramming assistance)
[bed_screws]
screw1: 30, 30
screw1_name: Front Left
screw2: {bed_x - 30}, 30
screw2_name: Front Right
screw3: {bed_x - 30}, {bed_y - 30}
screw3_name: Back Right
screw4: 30, {bed_y - 30}
screw4_name: Back Left
speed: 100
screw_thread: CW-M4"""
    
    config = f"""# This file contains common pin mappings for the {main_board['name']}
# To use this config, the firmware should be compiled for the {main_board['mcu'].upper()}
# Enable "extra low-level configuration options" and select the "12MHz crystal" as clock reference

# See docs/Config_Reference.md for a description of parameters.

## {printer['name']} {printer_size['name']} {main_board['name']} Config

## *** THINGS TO CHANGE/CHECK: ***
## MCU paths                            [mcu] section
## Thermistor types                     [extruder] and [heater_bed] sections - See https://www.klipper3d.org/Config_Reference.html#common-thermistors for common thermistor types
## Z Endstop Switch location            [safe_z_home] section
## Homing end position                  [gcode_macro G32] section
## Z Endstop Switch  offset for Z0      [stepper_z] section
## Probe points                         [{"quad_gantry_level" if printer_type == "voron2.4" else "z_tilt"}] section
## Min & Max gantry corner positions    [{"quad_gantry_level" if printer_type == "voron2.4" else "z_tilt"}] section
## PID tune                             [extruder] and [heater_bed] sections
## Probe pin                            [probe] section
## Fine tune E steps                    [extruder] section

[mcu]
##  Obtain definition by "ls -l /dev/serial/by-id/" then unplug to verify
##--------------------------------------------------------------------
serial: {main_board['serial_port']}
restart_method: command
##--------------------------------------------------------------------

{toolhead_mcu_section}

[printer]
kinematics: corexy
max_velocity: 300  
max_accel: 10000
max_z_velocity: 30
max_z_accel: 350
square_corner_velocity: 5.0

#####################################################################
#   X/Y Stepper Settings
#####################################################################

##  B Stepper - Left (X)
##  Connected to Motor Port
##  Endstop connected to X-ENDSTOP
[stepper_x]
step_pin: {main_board['stepper_pins']['x']['step']}
dir_pin: {main_board['stepper_pins']['x']['dir']}
enable_pin: !{main_board['stepper_pins']['x']['enable']}
rotation_distance: 40
microsteps: 16
full_steps_per_rotation: 200  #set to 400 for 0.9 degree stepper
endstop_pin: {main_board['endstop_pins']['x']}
position_min: 0
position_endstop: {bed_x}
position_max: {bed_x}
homing_speed: 100
homing_retract_dist: 5
homing_positive_dir: true

##  X Driver Configuration
{generate_xy_driver_config('x', main_board, x_current)}

##  A Stepper - Right (Y)
##  Connected to Motor Port
##  Endstop connected to Y-ENDSTOP
[stepper_y]
step_pin: {main_board['stepper_pins']['y']['step']}
dir_pin: {main_board['stepper_pins']['y']['dir']}
enable_pin: !{main_board['stepper_pins']['y']['enable']}
rotation_distance: 40
microsteps: 16
full_steps_per_rotation: 200  #set to 400 for 0.9 degree stepper
endstop_pin: {main_board['endstop_pins']['y']}
position_min: 0
position_endstop: {bed_y}
position_max: {bed_y}
homing_speed: 100
homing_retract_dist: 5
homing_positive_dir: true

##  Y Driver Configuration
{generate_xy_driver_config('y', main_board, y_current)}
 
#####################################################################
#   Z Stepper Settings
#####################################################################

{z_section}

#####################################################################
#   Extruder
#####################################################################

##  Connected to Toolhead
##  Heater - HE0
##  Thermistor - TH0
[extruder]
step_pin: toolhead:{toolhead_board['stepper_pins']['step']}
dir_pin: toolhead:{toolhead_board['stepper_pins']['dir']}
enable_pin: !toolhead:{toolhead_board['stepper_pins']['enable']}
##  Update value below when you perform extruder calibration
##  If you ask for 100mm of filament, but in reality it is 98mm:
##  rotation_distance = <previous_rotation_distance> * <actual_extrude_distance> / 100
rotation_distance: {extruder_config['rotation_distance']}
##  Update Gear Ratio depending on your Extruder Type
gear_ratio: {extruder_config['gear_ratio']}
microsteps: 16
full_steps_per_rotation: 200    #200 for 1.8 degree, 400 for 0.9 degree
nozzle_diameter: {extruder_config['nozzle_diameter']}
filament_diameter: {extruder_config['filament_diameter']}
heater_pin: toolhead:{toolhead_board['heater_pin']}
## Check what thermistor type you have. See https://www.klipper3d.org/Config_Reference.html#common-thermistors for common thermistor types.
## Use "Generic 3950" for NTC 100k 3950 thermistors
sensor_type: ATC Semitec 104NT-4-R025H42
sensor_pin: toolhead:{toolhead_board['thermistor_pin']}
min_temp: 0
max_temp: 270
max_power: 1.0
min_extrude_temp: 170
#control: pid
#pid_kp = 26.213
#pid_ki = 1.304
#pid_kd = 131.721
##  Try to keep pressure_advance below 1.0
pressure_advance: {extruder_config['pressure_advance']}
##  Default is 0.040, leave stock
pressure_advance_smooth_time: {extruder_config['pressure_advance_smooth_time']}

##  Connected to Toolhead
[tmc2209 extruder]
uart_pin: toolhead:{toolhead_board['stepper_pins']['uart']}
interpolate: false
run_current: {e_current}
sense_resistor: 0.110
stealthchop_threshold: 0


#####################################################################
#   Bed Heater
#####################################################################

[heater_bed]
##  SSR Pin - HEATBED
##  Thermistor - TB
heater_pin: {main_board['heater_pins']['bed']}
## Check what thermistor type you have. See https://www.klipper3d.org/Config_Reference.html#common-thermistors for common thermistor types.
## Use "Generic 3950" for Keenovo heaters
sensor_type: ATC Semitec 104NT-4-R025H42
sensor_pin: TB
##  Adjust Max Power so your heater doesn't warp your bed. Rule of thumb is 0.4 watts / cm^2 .
max_power: 1.0
min_temp: 0
max_temp: 120
#control: pid
#pid_kp: 58.437
#pid_ki: 2.347
#pid_kd: 363.769

#####################################################################
#   Probe
#####################################################################

{probe_section}

#####################################################################
#   Fan Control
#####################################################################

[fan]
##  Print Cooling Fan - Part Cooling
pin: toolhead:{toolhead_board['fan_pins']['part_cooling']}
##tachometer_pin: 
kick_start_time: 0.5
##  Depending on your fan, you may need to increase this value
##  if your fan will not start. Can change cycle_time (increase)
##  if your fan is not able to slow down effectively
off_below: 0.10

[heater_fan hotend_fan]
##  Hotend Fan
pin: toolhead:{toolhead_board['fan_pins']['hotend']}
##tachometer_pin: 
max_power: 1.0
kick_start_time: 0.5
heater: extruder
heater_temp: 50.0
##  If you are experiencing back flow, you can reduce fan_speed
#fan_speed: 1.0

[temperature_fan controller_fan]
##  Controller fan - Main Board
pin: {main_board['fan_pins']['controller']}
max_power: 1.0
shutdown_speed: 0.0
cycle_time: 0.010
sensor: temperature_host
control: watermark
max_delta: 2.0
min_temp: 0
max_temp: 85
target_temp: 50

[temperature_sensor chamber_temp]
## Chamber Temperature Sensor
sensor_type: ATC Semitec 104NT-4-R025H42
sensor_pin: TEMPERATURE_SENSOR_1
min_temp: 0
max_temp: 100
gcode_id: chamber_th

[temperature_sensor raspberry_pi]
sensor_type: temperature_host
min_temp: 0
max_temp: 100

[temperature_sensor mcu_temp]
sensor_type: temperature_mcu
min_temp: 0
max_temp: 100

#####################################################################
#   LED Control
#####################################################################

## Chamber Lighting (Optional)
## Connected to LED port
[output_pin caselight]
pin: LED_PIN
pwm:true
hardware_pwm: False
value: 0.20 #startup value
shutdown_value: 0
value: 0.4
cycle_time: 0.00025

#####################################################################
#   Homing and Gantry Adjustment Routines
#####################################################################

[idle_timeout]
timeout: 1800

[safe_z_home]
##  XY Location of the Z Endstop Switch
##  Update to the XY coordinates of your endstop pin
home_xy_position:{bed_x/2},{bed_y/2}
speed:100
z_hop:10

{leveling_section}

[bed_mesh]
speed: 300
horizontal_move_z: 10
mesh_min: 40, 40
mesh_max: {bed_x-40},{bed_y-40}
fade_start: 0.6
fade_end: 10.0
probe_count: 7,7 # Values should be odd, so one point is directly at bed center
algorithm: bicubic

#####################################################################
#   Macros
#####################################################################

[gcode_macro G28]
rename_existing: G28.0
gcode:
    G28.0 {{rawparams}}
    
[gcode_macro M109]
rename_existing: M109.0
gcode:
    M109.0 {{rawparams}}
    
[gcode_macro M190]
rename_existing: M190.0
gcode:
    M190.0 {{rawparams}}

[gcode_macro CANCEL_PRINT]
rename_existing: CANCEL_PRINT.0
gcode:
    G91
    G1 Z5 E-5 F3000
    G90
    TURN_OFF_HEATERS
    M84
    CANCEL_PRINT.0

[gcode_macro PAUSE]
rename_existing: PAUSE.0
gcode:
    PAUSE.0
    G91
    G1 E-5 F3000
    G1 Z10 F3000
    G90

[gcode_macro RESUME]
rename_existing: RESUME.0
gcode:
    G91
    G1 E5 F3000
    G90
    RESUME.0

## Printer-Specific Setup and Macros
"""
    
    # Add printer-specific macros based on print start type
    if printer_type == 'voron2.4':
        config += generate_voron24_macros(bed_x, bed_y, print_start_type)
    else:
        config += generate_trident_macros(bed_x, bed_y, print_start_type)
    
    # Add accelerometer configuration if toolhead has one
    if 'accelerometer_pins' in toolhead_board:
        accel = toolhead_board['accelerometer_pins']
        config += f"""
## Onboard Accelerometer (for Input Shaping)
[adxl345]
cs_pin: toolhead:{accel['cs']}
spi_software_sclk_pin: toolhead:{accel['clk']}
spi_software_mosi_pin: toolhead:{accel['mosi']}
spi_software_miso_pin: toolhead:{accel['miso']}
axes_map: x,y,z  # May need adjustment based on mounting orientation

[resonance_tester]
accel_chip: adxl345
probe_points:
    {bed_x / 2}, {bed_y / 2}, 20  # Center of bed, 20mm above
"""
    
    # Add CAN bus notes if using CAN toolhead
    if is_canbus:
        config += """
# ============================================================================
# CAN BUS SETUP NOTES
# ============================================================================
# 1. Flash your main board with CAN support enabled:
#    - Enable CAN bus in make menuconfig
#    - Use 'can0' interface (or your chosen interface)
#
# 2. Flash your toolhead board (EBB SB2209/EBB36):
#    - Use Katapult/CanBoot for easy updates
#    - Enable CAN in the toolhead firmware
#
# 3. Find your toolhead UUID:
#    - Run: python3 ~/klipper/scripts/canbus_query.py can0
#    - Update the canbus_uuid above with the correct value
#
# 4. Wiring:
#    - Connect CAN_H and CAN_L between main board and toolhead
#    - Ensure 120Ω termination resistor is present (usually on toolhead)
#
# For more info: https://www.klipper3d.org/CANBUS.html
# ============================================================================
"""
    
    return config

def generate_voron24_macros(bed_x, bed_y, print_start_type='standard'):
    """Generate Voron 2.4 specific macros"""
    
    if print_start_type == 'better':
        # Better Print Start Macro (Ellis style)
        return f"""# Voron 2.4 Specific Setup
[gcode_macro G32]
description: Quad gantry level
gcode:
    BED_MESH_CLEAR
    QUAD_GANTRY_LEVEL
    G28
    
# Better Print Start Macro - Based on Ellis' macro
[gcode_macro PRINT_START]
description: Enhanced print start with heat soak and adaptive bed mesh
gcode:
    # Parameters
    {{% set BED_TEMP = params.BED|default(60)|float %}}
    {{% set EXTRUDER_TEMP = params.EXTRUDER|default(200)|float %}}
    {{% set CHAMBER_TEMP = params.CHAMBER|default(0)|float %}}
    {{% set SOAK_TIME = params.SOAK|default(0)|int %}}
    {{% set ADAPTIVE_MESH = params.MESH|default(1)|int %}}
    
    # Initial status
    M104 S150                          # Preheat nozzle to 150C
    M140 S{{{{BED_TEMP}}}}               # Set bed temp
    
    # Home all axes
    G28
    
    # Quad gantry level
    QUAD_GANTRY_LEVEL
    G28 Z
    
    # Park at center for chamber heating
    G1 X{{{bed_x / 2}}} Y{{{bed_y / 2}}} F3000
    G1 Z50 F3000
    
    # Chamber heating (if specified)
    {{% if CHAMBER_TEMP > 0 %}}
        M190 S{{{{BED_TEMP}}}}           # Wait for bed
        # Wait for chamber temp or soak time
        {{% if SOAK_TIME > 0 %}}
            G4 P{{{{SOAK_TIME * 60000}}}}  # Wait in ms
        {{% endif %}}
    {{% else %}}
        M190 S{{{{BED_TEMP}}}}           # Wait for bed
    {{% endif %}}
    
    # Adaptive bed mesh (if enabled)
    {{% if ADAPTIVE_MESH > 0 %}}
        BED_MESH_CALIBRATE
    {{% else %}}
        BED_MESH_PROFILE LOAD=default
    {{% endif %}}
    
    # Final nozzle heat
    M109 S{{{{EXTRUDER_TEMP}}}}
    
    # Smart priming line
    G1 X20 Y20 F3000
    G1 Z0.2 F3000
    G1 X50 Y20 E15 F1500
    G1 X80 Y20 E15 F1500
    G1 X100 Y20 E10 F1500
    G1 Z2 F3000

[gcode_macro PRINT_END]
description: Enhanced print end with part cooling
gcode:
    # Save position
    G91
    G1 E-3 F3000                      # Small retract
    
    # Move away
    G1 Z10 F3000
    G90
    G1 X{{{bed_x / 2}}} Y{{{bed_y - 50}}} F3000
    
    # Turn off heaters
    M104 S0                           # Hotend off
    M140 S0                           # Bed off
    M106 S255                         # Full cooling
    
    # Wait for cooling
    G4 P30000                         # 30s cooling
    M106 S0                           # Fans off
    M84                               # Motors off

[gcode_macro M600]
description: Filament change with parking
gcode:
    PAUSE
    G91
    G1 E-20 F3000                     # Big retract
    G1 Z50 F3000                      # Move up
    G90
    G1 X{{{bed_x / 2}}} Y20 F3000     # Park front
    M109 S200                         # Wait for temp
    
[gcode_macro LOAD_FILAMENT]
description: Load filament with purge
gcode:
    M109 S200
    G91
    G1 E50 F300
    G1 E10 F150
    G90
    
[gcode_macro UNLOAD_FILAMENT]
description: Unload filament
gcode:
    M109 S200
    G91
    G1 E10 F150
    G1 E-60 F3000
    G90
"""
    else:
        # Standard LDO Kit Print Start
        return f"""# Voron 2.4 Specific Setup
[gcode_macro G32]
description: Quad gantry level
gcode:
    BED_MESH_CLEAR
    QUAD_GANTRY_LEVEL
    G28

[gcode_macro PRINT_START]
description: Standard print start sequence
gcode:
    {{% set BED_TEMP = params.BED|default(60)|float %}}
    {{% set EXTRUDER_TEMP = params.EXTRUDER|default(200)|float %}}
    G28
    QUAD_GANTRY_LEVEL
    G28 Z
    M190 S{{{{BED_TEMP}}}}
    M109 S{{{{EXTRUDER_TEMP}}}}
    BED_MESH_PROFILE LOAD=default
    G1 X20 Y20 F3000
    G1 Z0.2 F3000
    G1 X50 Y20 E15 F1500
    G1 X80 Y20 E15 F1500
    G1 X100 Y20 E10 F1500
    G1 Z2 F3000

[gcode_macro PRINT_END]
description: End print sequence
gcode:
    G91
    G1 E-5 F3000
    G1 Z10 F3000
    G90
    G1 X{{{bed_x / 2}}} Y{{{bed_y - 50}}} F3000
    TURN_OFF_HEATERS
    M84
"""

def generate_trident_macros(bed_x, bed_y, print_start_type='standard'):
    """Generate Trident specific macros"""
    
    if print_start_type == 'better':
        # Better Print Start Macro for Trident
        return f"""# Trident Specific Setup
[gcode_macro G32]
description: Z tilt calibration
gcode:
    BED_MESH_CLEAR
    Z_TILT_ADJUST
    G28
    
# Better Print Start Macro for Trident
[gcode_macro PRINT_START]
description: Enhanced print start with heat soak and adaptive bed mesh
gcode:
    # Parameters
    {{% set BED_TEMP = params.BED|default(60)|float %}}
    {{% set EXTRUDER_TEMP = params.EXTRUDER|default(200)|float %}}
    {{% set CHAMBER_TEMP = params.CHAMBER|default(0)|float %}}
    {{% set SOAK_TIME = params.SOAK|default(0)|int %}}
    {{% set ADAPTIVE_MESH = params.MESH|default(1)|int %}}
    
    # Initial status
    M104 S150                          # Preheat nozzle to 150C
    M140 S{{{{BED_TEMP}}}}               # Set bed temp
    
    # Home all axes
    G28
    
    # Z tilt adjust
    Z_TILT_ADJUST
    G28 Z
    
    # Park at center for chamber heating
    G1 X{{{bed_x / 2}}} Y{{{bed_y / 2}}} F3000
    G1 Z50 F3000
    
    # Chamber heating (if specified)
    {{% if CHAMBER_TEMP > 0 %}}
        M190 S{{{{BED_TEMP}}}}           # Wait for bed
        # Wait for chamber temp or soak time
        {{% if SOAK_TIME > 0 %}}
            G4 P{{{{SOAK_TIME * 60000}}}}  # Wait in ms
        {{% endif %}}
    {{% else %}}
        M190 S{{{{BED_TEMP}}}}           # Wait for bed
    {{% endif %}}
    
    # Adaptive bed mesh (if enabled)
    {{% if ADAPTIVE_MESH > 0 %}}
        BED_MESH_CALIBRATE
    {{% else %}}
        BED_MESH_PROFILE LOAD=default
    {{% endif %}}
    
    # Final nozzle heat
    M109 S{{{{EXTRUDER_TEMP}}}}
    
    # Smart priming line
    G1 X20 Y20 F3000
    G1 Z0.2 F3000
    G1 X50 Y20 E15 F1500
    G1 X80 Y20 E15 F1500
    G1 X100 Y20 E10 F1500
    G1 Z2 F3000

[gcode_macro PRINT_END]
description: Enhanced print end with part cooling
gcode:
    # Save position
    G91
    G1 E-3 F3000                      # Small retract
    
    # Move away
    G1 Z10 F3000
    G90
    G1 X{{{bed_x / 2}}} Y30 F3000
    
    # Turn off heaters
    M104 S0                           # Hotend off
    M140 S0                           # Bed off
    M106 S255                         # Full cooling
    
    # Wait for cooling
    G4 P30000                         # 30s cooling
    M106 S0                           # Fans off
    M84                               # Motors off

[gcode_macro M600]
description: Filament change with parking
gcode:
    PAUSE
    G91
    G1 E-20 F3000                     # Big retract
    G1 Z50 F3000                      # Move up
    G90
    G1 X{{{bed_x / 2}}} Y20 F3000     # Park front
    M109 S200                         # Wait for temp
    
[gcode_macro LOAD_FILAMENT]
description: Load filament with purge
gcode:
    M109 S200
    G91
    G1 E50 F300
    G1 E10 F150
    G90
    
[gcode_macro UNLOAD_FILAMENT]
description: Unload filament
gcode:
    M109 S200
    G91
    G1 E10 F150
    G1 E-60 F3000
    G90
"""
    else:
        # Standard LDO Kit Print Start for Trident
        return f"""# Trident Specific Setup
[gcode_macro G32]
description: Z tilt calibration
gcode:
    BED_MESH_CLEAR
    Z_TILT_ADJUST
    G28

[gcode_macro PRINT_START]
description: Standard print start sequence
gcode:
    {{% set BED_TEMP = params.BED|default(60)|float %}}
    {{% set EXTRUDER_TEMP = params.EXTRUDER|default(200)|float %}}
    G28
    Z_TILT_ADJUST
    G28 Z
    M190 S{{{{BED_TEMP}}}}
    M109 S{{{{EXTRUDER_TEMP}}}}
    BED_MESH_PROFILE LOAD=default
    G1 X20 Y20 F3000
    G1 Z0.2 F3000
    G1 X50 Y20 E15 F1500
    G1 X80 Y20 E15 F1500
    G1 X100 Y20 E10 F1500
    G1 Z2 F3000

[gcode_macro PRINT_END]
description: End print sequence
gcode:
    G91
    G1 E-5 F3000
    G1 Z10 F3000
    G90
    G1 X{{{bed_x / 2}}} Y30 F3000
    TURN_OFF_HEATERS
    M84
"""

def generate_z_section(printer_type, bed_x, bed_y, bed_z, z_current, main_board):
    z_pins = main_board['stepper_pins']['z']
    z1_pins = main_board['stepper_pins']['z1']
    z2_pins = main_board['stepper_pins']['z2']
    
    # Generate Z stepper config
    z_stepper = f"""[stepper_z]
step_pin: {z_pins['step']}
dir_pin: {z_pins['dir']}
enable_pin: !{z_pins['enable']}
microsteps: 16
rotation_distance: 40
endstop_pin: probe:z_virtual_endstop
position_max: {bed_z}
position_min: -5
homing_speed: 15
second_homing_speed: 3

[tmc2209 stepper_z]
uart_pin: {z_pins['uart']}
run_current: {z_current}
sense_resistor: 0.110
stealthchop_threshold: 0
interpolate: true"""
    
    # Generate Z1 stepper config
    z1_stepper = f"""
[stepper_z1]
step_pin: {z1_pins['step']}
dir_pin: {z1_pins['dir']}
enable_pin: !{z1_pins['enable']}
microsteps: 16
rotation_distance: 40

[tmc2209 stepper_z1]
uart_pin: {z1_pins['uart']}
run_current: {z_current}
sense_resistor: 0.110
stealthchop_threshold: 0
interpolate: true"""
    
    # Generate Z2 stepper config
    z2_stepper = f"""
[stepper_z2]
step_pin: {z2_pins['step']}
dir_pin: {z2_pins['dir']}
enable_pin: !{z2_pins['enable']}
microsteps: 16
rotation_distance: 40

[tmc2209 stepper_z2]
uart_pin: {z2_pins['uart']}
run_current: {z_current}
sense_resistor: 0.110
stealthchop_threshold: 0
interpolate: true"""
    
    if printer_type == 'trident':
        # Trident has only 3 Z steppers
        leveling_section = f"""
[z_tilt]
z_positions:
    -50, 18
    {bed_x / 2}, {bed_y + 50}
    {bed_x + 50}, 18
points:
    30, 30
    {bed_x / 2}, {bed_y - 30}
    {bed_x - 30}, 30
speed: 100
horizontal_move_z: 10
retries: 5
retry_tolerance: 0.0075"""
        return z_stepper + z1_stepper + z2_stepper + leveling_section
    else:
        # Voron 2.4 has 4 Z steppers
        z3_pins = main_board['stepper_pins']['z3']
        z3_stepper = f"""
[stepper_z3]
step_pin: {z3_pins['step']}
dir_pin: {z3_pins['dir']}
enable_pin: !{z3_pins['enable']}
microsteps: 16
rotation_distance: 40

[tmc2209 stepper_z3]
uart_pin: {z3_pins['uart']}
run_current: {z_current}
sense_resistor: 0.110
stealthchop_threshold: 0
interpolate: true"""
        leveling_section = f"""
[quad_gantry_level]
gantry_corners:
    -60, -10
    {bed_x + 60}, {bed_y + 10}
points:
    30, 30
    30, {bed_y - 30}
    {bed_x - 30}, {bed_y - 30}
    {bed_x - 30}, 30
speed: 100
horizontal_move_z: 10
max_adjust: 10
retries: 5
retry_tolerance: 0.0075"""
        return z_stepper + z1_stepper + z2_stepper + z3_stepper + leveling_section

def generate_probe_section(probe, bed_x, bed_y):
    if probe['type'] == 'probe':
        return f"""[probe]
pin: {probe['pin']}
x_offset: 0.0
y_offset: 0.0
#z_offset: 0.0  # Calibrate with PROBE_CALIBRATE
speed: 3.0
samples: 3
samples_result: median
sample_retract_dist: 3.0
samples_tolerance: 0.006
samples_tolerance_retries: 3

[bed_mesh]
speed: 150
horizontal_move_z: 5
mesh_min: 30, 30
mesh_max: {bed_x - 30}, {bed_y - 30}
probe_count: 7, 7
algorithm: bicubic
bicubic_tension: 0.2
fade_start: 1.0
fade_end: 10.0
fade_target: 0
split_delta_z: 0.01
move_check_distance: 3.0
mesh_pps: 2, 2
zero_reference_position: {bed_x / 2}, {bed_y / 2}

[safe_z_home]
home_xy_position: {bed_x / 2}, {bed_y / 2}
speed: 100
z_hop: 10
z_hop_speed: 15

[gcode_macro PROBE_CALIBRATE]
description: Calibrate probe z_offset
rename_existing: PROBE_CALIBRATE.0
gcode:
    PROBE_CALIBRATE.0"""
    else:
        return f"""[beacon]
serial: {probe['serial_port']}
collision_homing: true
collision_z_homing: true
contact_max_hotend_temperature: 180
home_xy_position: {bed_x / 2}, {bed_y / 2}
home_z_hop: 5
home_z_hop_speed: 15
home_xy_speed: 100
home_z_speed: 15
calibration_method: touch
sensor_mode: contact

[bed_mesh]
speed: 150
horizontal_move_z: 5
mesh_min: 30, 30
mesh_max: {bed_x - 30}, {bed_y - 30}
probe_count: 7, 7
algorithm: bicubic
bicubic_tension: 0.2
fade_start: 1.0
fade_end: 10.0
fade_target: 0
split_delta_z: 0.01
move_check_distance: 3.0
mesh_pps: 2, 2
zero_reference_position: {bed_x / 2}, {bed_y / 2}

[safe_z_home]
home_xy_position: {bed_x / 2}, {bed_y / 2}
speed: 100
z_hop: 10
z_hop_speed: 15

[gcode_macro PROBE_CALIBRATE]
description: Calibrate beacon probe
gcode:
    BEACON_CALIBRATE"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
