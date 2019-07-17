# hardware configuration
config = {
    "hx711": {
        "CLK": 29,
        "DAT": 31,
        "ref": 2145  # calibration yields 100 g <-> readout 214500
    },
    "pca9685": {
        "freq": 60,
        "valvechannels": range(12),  # 0..11
        "valvepositions": [  # (open, closed)
            (375, 535),  # ch 0
            (375, 510),  # ch 1
            (375, 515),  # ch 2
            (375, 515),  # ch 3
            (375, 520),  # ch 4
            (375, 520),  # ch 5
            (375, 235),  # ch 6
            (375, 250),  # ch 7
            (375, 250),  # ch 8
            (375, 240),  # ch 9
            (375, 235),  # ch 10
            (375, 250)  # ch 11
        ],
        "fingerchannel": 12,
        "fingerpositions": (280, 430, 450),  # retracted, above bell, bell
        "lightpin": 22,
        "lightpwmchannel": 13,
        "lightpositions": (0, 500)
    },
    "pump": {
        "MOTOR": 18
    }
}
