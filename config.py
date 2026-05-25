SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
FULLSCREEN = False  # True no R36S
EXIT_KEY   = 97    # pygame.K_a — botão A no R36S / tecla 'a' no PC

MOCK_MODE = True    # True para testar sem adaptador OBD

OBD_HOST          = "localhost"
OBD_PORT          = 35000
OBD_POLL_INTERVAL = 0.1   # segundos entre ciclos de leitura (0.1 = 10 Hz, 0.5 = 2 Hz)

ESP32_PORT = "auto"    # "auto" detecta a porta automaticamente; ou força ex: "COM3" / "/dev/ttyUSB0"
ESP32_BAUD = 115200

COLORS = {
    "bg":      (5,   5,   10),
    "primary": (0,   255, 200),
    "danger":  (255, 60,  50),
    "warning": (255, 190, 0),
    "text":    (240, 245, 255),
    "muted":   (80,  105, 115),
    "panel":   (18,  22,  28),
    "arc_bg":  (22,  32,  42),
    "divider": (35,  55,  65),
}

ALARM_SOUND  = True   # False para silenciar os beeps (útil em testes)

LOG_ENABLED  = True
LOG_DIR      = "logs"
LOG_INTERVAL = 1.0   # segundos entre cada linha gravada no CSV

RPM_MAX      = 7000
RPM_REDLINE  = 5500
TEMP_MIN     = 40
TEMP_MAX     = 120
TEMP_HISTORY = 120  # amostras no gráfico
