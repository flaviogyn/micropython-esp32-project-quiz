# Project: ESP32 Model WR2022
# Binary: ESP32_GENERIC-20220117-v1.18.bin

from machine import Pin, PWM, I2C
from time import sleep, sleep_ms
import urequests as requests
import esp8266_i2c_lcd as esp8266_lcd
import network, usys
import dht
import ujson

# # Scan for I2C devices and print their addresses in decimal and hex
# devices = i2c.scan()
# if not devices:
#     print("No I2C device found.")
#     raise Exception("No I2C devices detected.")
# else:
#     print("I2C devices found:")
#     for device in devices:
#         print("  Decimal: {}, Hex: {}".format(device, hex(device)))
# 
# I2C(0) 
# SDA_PIN = 18
# SCL_PIN = 19
# I2C(0) 
# SDA_PIN = 25
# SCL_PIN = 26

LED_PIN_2 = 2
LED_PIN_15 = 15
DHT_PIN_4 = 4
SDA_PIN = 21
SCL_PIN = 22
buzzer = PWM(Pin(15))

# Wifi network station credentials
WIFI_SSID = "iot-home"
WIFI_PASSWORD = "012343210"

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

# Atribuições
led = Pin(LED_PIN_2, Pin.OUT)
pwm = PWM(Pin(LED_PIN_15))
pwm.duty(0)

# Inicializa o I2C (I2C0 nos pinos GP21 e GP22)
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
lcd = esp8266_lcd.I2cLcd(i2c, esp8266_lcd.DEFAULT_I2C_ADDR, 2, 16)

lcd.move_to(0, 0)
lcd.putstr("2x16 LCD Iniciado")
lcd.move_to(0, 1)

# Configuracao do DHT11
sensor_dht = dht.DHT11(Pin(DHT_PIN_4))

def inicializar_lcd():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("2x16 Iniciado...")
    lcd.move_to(0, 1)
    sleep(1)

def lcd_escrever(coluna, linha, texto):
    texto = str(texto[:16])
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

        print("\nTemp.: {} C, Umid.: {} %".format(temperatura, umidade))
    except OSError as e:
        lcd.clear()
        lcd_escrever(0, 0, "Erro na leitura")
        print("Erro ao ler o sensor DHT11:", e)

# def conWiFiNewEsp32():
#     sta_if = network.WLAN(network.WLAN.IF_STA); sta_if.active(True)
#     sta_if.scan()                             # Scan for available access points
#     sta_if.connect(WIFI_SSID, WIFI_PASSWORD) # Connect to an AP
#     sta_if.isconnected()                      # Check for successful connection
#     print('connected!')
#     
#     tentativas = 0
#     while not sta_if.isconnected() and tentativas < 20:
#         utime.sleep(1)
#         tentativas += 1
# 
#     if not sta_if.isconnected():
#         raise OSError("Falha ao conectar no Wi-Fi")
# 
#     print("connected!")
#     print(sta_if.ifconfig())

def conWiFi():
    # This will create a station interface object.
    wlan = network.WLAN(network.STA_IF) 

    wlan.active(True)             # Activate the interface so you can use it.
    if not wlan.isconnected():    # Unless already connected, try to connect.
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)  # Connect to the station using
                                                                   # credentials from the json file.
        if not wlan.isconnected():
            print("Can't connect to network with given credentials.")
            usys.exit(0)  # This will programmatically break the execution of this script and return to shell.
    
    print('network config:', wlan.ifconfig())

    if wlan.isconnected() == True:    # This test is redundant since connection is tested in the do_connect() method
        print("Connected")
        print("My IP address: ", wlan.ifconfig()[0]) # Prints the acquired IP address
        print("---------")
    else:
        print("Not connected")

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

        print("Nomes com melhor desempenho:", nomes)
        return linha2

    except Exception as e:
        lcd.clear()
        lcd_escrever(0, 0, "Erro API")
        lcd_escrever(0, 1, str(e)[:16])
        print("Erro ao buscar resultado da API:", e)
        return "Sem nome"

def tocar(freq, dur, duty=512):
    pwm.freq(freq)
    pwm.duty(duty)
    sleep_ms(dur)
    pwm.duty(0)
    sleep_ms(20)

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
    sleep_ms(10)
    
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

    sleep_ms(80)

    tocar(659, 50, 512)
    tocar(684, 50, 448)
    tocar(712, 50, 384)
    tocar(748, 50, 320)
    tocar(766, 50, 256)
    tocar(787, 50, 192)
    tocar(830, 50, 128)
    tocar(875, 50, 64)

    sleep_ms(80)

    tocar(981, 50, 512)
    tocar(1049, 50, 448)
    tocar(1113, 50, 384)
    tocar(1130, 50, 320)
    tocar(1216, 50, 256)
    tocar(1311, 50, 192)
    tocar(1429, 50, 128)
    tocar(1567, 50, 64)

    sleep_ms(80)

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
    buzzer_pin = Pin(LED_PIN_15, Pin.OUT)  # Ajuste o pino conforme sua montagem
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
    sleep(duration)
    buzzer.duty(0)
    sleep(0.05)

# Inicialização LCD
inicializar_lcd()
#lcd_escrever(0, 0, "Iniciando...")
sleep(1)

# Desligado
pwm.duty(0)
conWiFi()

while True:
    led.on()
    sleep(1)

    # Ler temperatura e humidade
    ler_e_mostrar()
    sleep(1)

    # Busca quem acertou mais pontos
    ganhador = mostrar_nomes_melhor_desempenho()
    if ganhador != "Sem nome":
        print("Ganhador", ganhador)
        som_acerto()
        sleep(3)
        
        # Escrever no LCD
        lcd.clear()
        lcd_escrever(0, 0, ">>> Ganhador <<<")
        lcd_escrever(0, 1, ganhador)

        # Simula a voz humanda
        speak_name(ganhador)
        sleep(5)
        
        # Saudação final
        obrigado()
        sleep(5)
    else:
        # Escrever no LCD
        lcd.clear()
        lcd_escrever(0, 0, "Ganhador")
        lcd_escrever(0, 1, "Nine, Not, ;)")

        som_erro()   
        sleep(5)
    
    led.off()
    sleep(1)
    
    