import can
from time import sleep
from can.bus import BusState


def uint16_to_bytes(uint16_val):
    assert isinstance(uint16_val, int)
    assert 0 <= uint16_val <= 65535
    high_byte = 0
    hex_val = hex(uint16_val)
    hex_len = len(hex_val)
    if hex_len <= 4:
        # 0-255
        low_byte = uint16_val
    else:
        low_byte_str = '0x' + hex_val[-2:]
        high_byte_str = hex_val[0: -2]
        low_byte = int(low_byte_str, base=16)
        high_byte = int(high_byte_str, base=16)
    return low_byte, high_byte


def tx_10ms(rpm_val):
    try:
        bus.send(msg_rpm)
        bus.send(msg_speed)
        bus.send(msg_engine)
        bus2.send(msg_toyota_rpm)
    except can.CanError:
        print("Message NOT sent")
    rpm_val = 28500
    msg_rpm.data[2], msg_rpm.data[3] = uint16_to_bytes(rpm_val)
    rpm_val = 20000
    if rpm_val > 65535:
        rpm_val = 0
    return rpm_val


def tx_500ms():
    try:
        bus.send(msg_turn)
        bus2.send(msg_toyota_temp)
        bus2.send(msg_toyota_brake)
        bus2.send(msg_toyota_abs)
        bus.send(msg_toyota)
    except can.CanError:
        print("Message NOT sent")
    pass
    msg_turn.data[0] ^= 3
    #msg_turn.data[1] ^= 3
    #msg_turn.data[2] = 0x00
    msg_toyota_brake.data[0] ^= 0x60


if __name__ == "__main__":
    bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)
    bus2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate=500000)
    bus2.state = BusState.ACTIVE
    rpm_val = 1000
    toyota_id_start = 0x200
    toyota_id = toyota_id_start
    toyota_id_end = 0x299
    msg_turn = can.Message(arbitration_id=0x470,
                          data=[3, 3, 3, 3, 0, 0, 0, 0], is_extended_id=False)
    msg_rpm = can.Message(arbitration_id=0x280,
                          data=[0x49, 0x0E, 0, 0, 0x0E, 0x00, 0x1B, 0x0E], is_extended_id=False)

    msg_engine = can.Message(arbitration_id=0xDA0,
                            data=[0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                            is_extended_id=False)
    msg_speed = can.Message(arbitration_id=0x320,
                          data=[0x00, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                            is_extended_id=False)

    toyota_rpm = 0x14  # = 4000RPM 100ms
    msg_toyota_rpm = can.Message(arbitration_id=0x1c4,
                             data=[toyota_rpm, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                             is_extended_id=False)

    msg_toyota_temp = can.Message(arbitration_id=0x3b0,
                             data=[0x00, 0x00, 0x00, 0x10, 0x00, 0x10, 0x00, 0x00],
                             is_extended_id=False)

    msg_toyota_brake = can.Message(arbitration_id=0x3b7,
                             data=[0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                             is_extended_id=False)

    msg_toyota_abs = can.Message(arbitration_id=toyota_id,
                             data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                             is_extended_id=False)

    msg_toyota = can.Message(arbitration_id=toyota_id,
                          data=[0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F],
                             is_extended_id=False)
    TIMER_PERIOD = 0.001
    timer_10ms = 0
    timer_500ms = 0
    while True:
        sleep(TIMER_PERIOD)
        timer_10ms += TIMER_PERIOD
        if timer_10ms >= 0.01:
            timer_10ms = 0
            rpm_val = tx_10ms(rpm_val)
        timer_500ms += TIMER_PERIOD
        if timer_500ms >= 0.5:
            timer_500ms = 0
            tx_500ms()
            toyota_id = toyota_id + 1 if toyota_id < toyota_id_end else toyota_id_start
            print(f"Toyota ID: {hex(toyota_id)}")
            msg_toyota.arbitration_id = toyota_id

        # try:
        #    msg = bus2.recv(1)
        #    if msg is not None:
        #        print(msg)
        # except KeyboardInterrupt:
        #    pass
