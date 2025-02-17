import RPi.GPIO as GPIO
import abc
import asyncio


class Device(abc.ABC):

    def __init__(self):
        self.active = False

    def turnon(self):
        self.active = True

    def turnoff(self):
        self.active = False


class Pump(Device):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        super().__init__()

    def turnon(self):
        GPIO.output(self.pin, GPIO.LOW)
        super().turnon()

    def turnoff(self):
        GPIO.output(self.pin, GPIO.HIGH)
        super().turnoff()


class SmallValve(Device):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        super().__init__()

    def turnon(self):
        GPIO.output(self.pin, GPIO.LOW)
        super().turnon()

    def turnoff(self):
        GPIO.output(self.pin, GPIO.HIGH)
        super().turnoff()


class BigValve(Device):
    def __init__(self, pins: tuple[int, int], epsilon: float = 16):
        self.pins = pins
        self.epsilon = epsilon
        self.opened = 0.0
        for pin in self.pins:
            pass
            GPIO.setup(pin, GPIO.OUT)
        super().__init__()

    def turnon(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.HIGH)
        super().turnon()

    def turnoff(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.HIGH)
        super().turnoff()

    def stop(self):
        pass
        GPIO.output(self.pins[0], GPIO.HIGH)
        GPIO.output(self.pins[1], GPIO.HIGH)

    async def open(self, percentage: float):
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage should be between 0 and 100")

        self.opened = percentage
        open_time = self.epsilon * percentage / 100
        self.turnon()
        await asyncio.sleep(open_time)
        self.stop()

    async def close(self, percentage: float):
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage should be between 0 and 100")

        self.opened = 100 - percentage
        open_time = self.epsilon * percentage / 100
        self.turnoff()
        await asyncio.sleep(open_time)
        self.stop()


class PinManager:
    def __init__(self):
        self.pump = Pump(17)
        self.big_valve = BigValve((27, 22))
        self.small_valve = SmallValve(23)

    def active_pump(self, active: bool):
        if active:
            self.pump.turnon()
        else:
            self.pump.turnoff()

    def active_small_valve(self, active: bool):
        if active:
            self.small_valve.turnon()
        else:
            self.small_valve.turnoff()

    async def change_big_valve(self, percentage: float, active: bool):
        if not active and not self.small_valve.active:
            raise ValueError(
                "Cannot close the big valve if the small valve is not active"
            )

        if active:
            await self.big_valve.open(percentage)
        else:
            await self.big_valve.close(percentage)

    def get_big_valve_status(self):
        return self.big_valve.opened
