import enum
import cv2

class State(enum.Enum):
    lifting = "YUKSEL"
    lowing = "ALCAL"
    staying = "SABIT"

class Text(enum.Enum):
    text1 = ""

