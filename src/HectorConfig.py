# hardware configuration
config = {
    "hx711": {
        "CLK": 29,
        "DAT": 31,
        "ref": 960  # calibration yields 100 g <-> readout 214500
    },
    "pca9685": {
        "freq": 60,
        "valvechannels": range(12),  # 0..11
        "valvepositions": [  # (open, closed)
            (300, 550),  # ch 0
            (300, 680),  # ch 1
            (300, 515),  # ch 2
            (300, 460),  # ch 3
            (300, 480),  # ch 4
            (300, 540),  # ch 5
            (300, 520),  # ch 6
            (300, 580),  # ch 7
            (300, 420),  # ch 8
            (300, 570),  # ch 9
            (300, 540),  # ch 10
            (300, 550)  # ch 11
        ],
        "fingerchannel": 12,
        "fingerpositions": (280, 430, 450),  # retracted, above bell, bell
        "lightpin": 22,
        "lightpwmchannel": 13,
        "lightpositions": (0, 500)
    },
    "a4988": {
        "ENABLE": 11,
        "MS1": 13,
        "MS2": 15,
        "MS3": 19,
        "RESET": 21,
        "SLEEP": 23,
        "STEP": 37,
        "DIR": 33,
        "numSteps": 260
    },
    "arm": {
        "SENSE": 16
    },
    "pump": {
        "MOTOR": 18
    },
    "ws2812": {
        "DIN": 12
    }
}
