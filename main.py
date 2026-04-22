from machine import Pin, PWM, I2C
from time import sleep
from i2c_lcd import I2cLcd
import network
import dht
import ujson

# Define ESP32 I2C pins
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# Scan for I2C devices and print their addresses in decimal and hex
devices = i2c.scan()
if not devices:
    print("No I2C device found.")
    raise Exception("No I2C devices detected.")
else:
    print("I2C devices found:")
    for device in devices:
        print("  Decimal: {}, Hex: {}".format(device, hex(device)))


LED_PIN_2 = 2
LED_PIN_15 = 15
DHT_PIN_27 = 27
SDA_PIN = 21
SCL_PIN = 22
DHT_PIN = 14;
buzzer = PWM(Pin(15))

# Wifi network station credentials
WIFI_SSID = "EVWE"
WIFI_PASSWORD = "EVWE@2024"

# API
URL = "https://projetoquiz.onrender.com/api/resultados"

# Configuracao do I2C e LCD
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Mapeamento das letras A-Z para frequências (em Hz)
# Baseado na escala cromática a partir de Lá4 (440 Hz)
# Letras fora do intervalo viram 0 (silêncio)
note_map = {
    'a': 440,  # Lá4
    'b': 494,  # Si4
    'c': 523,  # Dó5
    'd': 587,  # Ré5
    'e': 659,  # Mi5
    'f': 698,  # Fá5
    'g': 784,  # Sol5
    'h': 880,  # Lá5
    'i': 988,  # Si5
    'j': 1047, # Dó6
    'k': 1175, # Ré6
    'l': 1319, # Mi6
    'm': 1397, # Fá6
    'n': 1568, # Sol6
    'o': 1760, # Lá6
    'p': 1976, # Si6
    'q': 2093, # Dó7
    'r': 2349, # Ré7
    's': 2637, # Mi7
    't': 2794, # Fá7
    'u': 3136, # Sol7
    'v': 3520, # Lá7
    'w': 3951, # Si7
    'x': 4186, # Dó8
    'y': 4699, # Ré8
    'z': 5274, # Mi8
    ' ': 0,    # Espaço = silêncio
}

try:
    from LiquidCrystal_I2C import LiquidCrystal_I2C
except ImportError:
    LiquidCrystal_I2C = None

try:
    from pico_i2c_lcd import I2cLcd
except ImportError:
    I2cLcd = None

try:
    import urequests as requests
except ImportError:
    requests = None

# Atribuições
led = Pin(LED_PIN_2, Pin.OUT)
pwm = PWM(Pin(LED_PIN_15))
pwm.duty(0)

# Inicializa o I2C (I2C0 nos pinos GP21 e GP22)
i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)

# Configuracao do DHT11
sensor_dht = dht.DHT11(DHT_PIN_27)

def inicializar_lcd():
    if LiquidCrystal_I2C is not None:
        lcd_obj = LiquidCrystal_I2C(I2C_ADDR, I2C_NUM_COLS, I2C_NUM_ROWS, i2c)
        if hasattr(lcd_obj, "begin"):
            lcd_obj.begin()
        if hasattr(lcd_obj, "backlight"):
            lcd_obj.backlight()
        return lcd_obj

    if I2cLcd is not None:
        return I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

    raise ImportError("Nenhuma biblioteca de LCD I2C disponivel.")

try:
    lcd = inicializar_lcd()
except OSError:
    print("Erro: LCD nao encontrado no endereco I2C", hex(I2C_ADDR))
    machine.reset()

def lcd_escrever(coluna, linha, texto):
    texto = str(texto).ljust(16)[:16]
    if hasattr(lcd, "move_to") and hasattr(lcd, "putstr"):
        lcd.move_to(coluna, linha)
        lcd.putstr(texto)
    else:
        lcd.setCursor(coluna, linha)
        lcd.print(texto)

def ler_e_mostrar():
    try:
        sensor_dht.measure()
        temperatura = sensor_dht.temperature()
        umidade = sensor_dht.humidity()

        lcd.clear()
        lcd_escrever(0, 0, "Temp: {:.1f}C".format(temperatura))
        lcd_escrever(0, 1, "Umid: {:.1f}%".format(umidade))

        print("Lido: T={}C, U={}%".format(temperatura, umidade))
    except OSError as e:
        lcd.clear()
        lcd_escrever(0, 0, "Erro na leitura")
        print("Erro ao ler o sensor DHT11:", e)

def conWiFi():
    sta_if = network.WLAN(network.WLAN.IF_STA); sta_if.active(True)
    sta_if.scan()                             # Scan for available access points
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD) # Connect to an AP
    sta_if.isconnected()                      # Check for successful connection
    print('connected!')
    
    tentativas = 0
    while not sta_if.isconnected() and tentativas < 20:
        utime.sleep(1)
        tentativas += 1

    if not sta_if.isconnected():
        raise OSError("Falha ao conectar no Wi-Fi")

    print("connected!")
    print(sta_if.ifconfig())

def obter_nomes_melhor_desempenho():
    if requests is None:
        raise ImportError("Biblioteca 'urequests' nao esta disponivel no Pico.")

    resposta = requests.get(URL)
    try:
        if resposta.status_code != 200:
            raise OSError("Erro HTTP {}".format(resposta.status_code))

        try:
            dados = resposta.json()
        except AttributeError:
            dados = ujson.loads(resposta.text)

        melhor_desempenho = dados.get("melhor_desempenho", {})
        return melhor_desempenho.get("nomes", [])
    finally:
        resposta.close()

def mostrar_nomes_melhor_desempenho():
    try:
        nomes = obter_nomes_melhor_desempenho()
        nome = str(nomes[0]).strip() if nomes else "Sem nome"

        linha1 = "Melhor:"
        linha2 = nome[:16]

        if len(nome) > 16:
            linha1 = nome[:16]
            linha2 = nome[16:32]

        print(linha1)
        print(linha2)
        #lcd.clear()
        #lcd_escrever(0, 0, linha1)
        #lcd_escrever(0, 1, linha2)

        print("Nomes com melhor desempenho:", nomes)
    except Exception as e:
        lcd.clear()
        lcd_escrever(0, 0, "Erro API")
        lcd_escrever(0, 1, str(e)[:16])
        print("Erro ao buscar resultado da API:", e)

def tocar(freq, dur, duty=512):
    pwm.freq(freq)
    pwm.duty(duty)
    time.sleep_ms(dur)
    pwm.duty(0)
    time.sleep_ms(20)

def som_acerto():
    ''' O som de acerto é o som da bandeirada
        no Enduro do Atari
    '''
    tocar(181, 140)
    tocar(225, 170)
    tocar(269, 200)
    tocar(355, 330)
    tocar(269, 200)
    tocar(355, 700)
    time.sleep_ms(10)
    
def som_erro():
    ''' O som de erro é o som do Pacman morrendo
    '''
    tocar(492, 50, 512)
    tocar(507, 50, 448)
    tocar(527, 50, 384)
    tocar(540, 50, 320)
    tocar(568, 50, 256)
    tocar(580, 50, 192)
    tocar(610, 50, 128)
    tocar(624, 50, 64)

    time.sleep_ms(80)

    tocar(659, 50, 512)
    tocar(684, 50, 448)
    tocar(712, 50, 384)
    tocar(748, 50, 320)
    tocar(766, 50, 256)
    tocar(787, 50, 192)
    tocar(830, 50, 128)
    tocar(875, 50, 64)

    time.sleep_ms(80)

    tocar(981, 50, 512)
    tocar(1049, 50, 448)
    tocar(1113, 50, 384)
    tocar(1130, 50, 320)
    tocar(1216, 50, 256)
    tocar(1311, 50, 192)
    tocar(1429, 50, 128)
    tocar(1567, 50, 64)

    time.sleep_ms(80)

    tocar(1963, 50, 512)
    tocar(2247, 50, 448)
    tocar(2616, 50, 384)
    tocar(3142, 50, 320)
    tocar(3931, 50, 256)
    tocar(5230, 50, 192)
    tocar(7800, 50, 128)
    tocar(8000, 50, 64)

def play_tone(pin, frequency, duration):
    """Toca uma frequência por um tempo (em segundos)."""
    if frequency == 0:
        sleep(duration)  # Silêncio
        return
    buzzer = PWM(pin)
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% duty cycle = volume médio
    sleep(duration)
    buzzer.deinit()
    sleep(0.03)  # Pequena pausa entre notas

def speak_name(name, duration=0.3):
    """
    Converte um nome (string) em uma sequência de tons.
    Cada letra vira uma nota (mapeada pelo alfabeto).
    Parâmetro opcional: duration (duração de cada nota em segundos).
    """
    buzzer_pin = Pin(25, Pin.OUT)  # Ajuste o pino conforme sua montagem
    name_lower = name.lower()
    
    for char in name_lower:
        freq = note_map.get(char, 0)  # Caracteres não mapeados viram silêncio
        play_tone(buzzer_pin, freq, duration)

def obrigado():
    # "o" (grave, curto)
    tone(300, 0.2)
    
    # "bri" (subida rápida)
    tone(400, 0.1)
    tone(600, 0.15)
    
    # "ga" (queda)
    tone(500, 0.15)
    tone(350, 0.2)
    
    # "do" (final descendente)
    tone(300, 0.2)
    tone(250, 0.25)

def tone(freq, duration):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep(duration)
    buzzer.duty(0)
    time.sleep(0.05)

# Inicialização
lcd_escrever(0, 0, "Iniciando...")
sleep(2)
conWiFi()

while True:
    led.on()
    #som_acerto()
    sleep(1)
    #som_erro()

    # Ler temperatura e humidade
    ler_e_mostrar()

    # Busca quem acertou mais pontos
    mostrar_nomes_melhor_desempenho()
    sleep(2)
    
    # Exemplo de uso:
    #speak_name("Ana")     # Toca as notas para A, n, a
    #speak_name("João")    # Toca J, o, a, o (note que ç vira silêncio)
    #speak_name("Maria", duration=0.2)  # Notas mais rápidas
    
    #obrigado()
    led.off()
    sleep(1)
    
    