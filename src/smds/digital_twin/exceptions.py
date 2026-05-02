class DigitalTwinError(Exception):
    pass


class SyncError(DigitalTwinError):
    pass


class SimulationError(DigitalTwinError):
    pass


class CommunicationError(DigitalTwinError):
    pass
