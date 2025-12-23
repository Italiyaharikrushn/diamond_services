import enum

class StoneType(str, enum.Enum):
    natural = "natural"
    lab = "lab"
    gemstones = "gemstones"


class Color(str, enum.Enum):
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"


class Clarity(str, enum.Enum):
    FL = "FL"
    IF = "IF"
    VVS1 = "VVS1"
    VVS2 = "VVS2"
    VS1 = "VS1"
    VS2 = "VS2"
    SI1 = "SI1"
    SI2 = "SI2"
    I1 = "I1"
    I2 = "I2"
    I3 = "I3"
