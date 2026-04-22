# Projeto do uso do MicroPython em Sistemas Embarcados

## Integrantes do grupo
* Afrain da Silva Calixto
* Alexandre Damaso Costa
* Flávio Lourenço da Silva
* Gustavo Adolpho Souteras Barbosa

## Seminário sobre Python: Técnicas e Abordagens Atuais 
- INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA - GOIÁS 
- CAMPUS GOIÂNIA
- PÓS-GRADUAÇÃO EM INTELIGÊNCIA ARTIFICIAL APLICADA 
- DISCIPLINA: LINGUAGEM DE PROGRAMAÇÃO APLICADA 
- TURMA: 2026
- PROFESSOR: Otávio Calaça Xavier

## Material  
- ESP32 Wrown
- DHT11
- LCD 16x2 I2C

## 🔧 Passo 1: Preparação para uso no VSCode
  1. Abra o VS Code.
    1.2. Vá ao ícone de Extensions (ou aperte Ctrl+Shift+X).
    1.3. Procure por "MicroPico" (antiga Pico-W-Go) e clique em Install.
    1.4. Certifique-se de que você tem o Python instalado no seu Windows (baixe na Microsoft Store ou em python.org).

  2. Configurando o Raspberry Pi Pico
    Para o VS Code "conversar" com a placa, ela precisa estar rodando o firmware do MicroPython:
    2.1. Segure o botão BOOTSEL do Pico e conecte-o ao USB.
    2.2. Ele aparecerá como um pendrive chamado RPI-RP2.
    2.3. Arraste o arquivo .uf2 do MicroPython para dentro dele (baixe o mais recente no site oficial do Raspberry Pi). 
    2.4. Acesse o link: https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
    2.5. A placa vai reiniciar e o "pendrive" vai sumir.

  3. Conectando e Programando
    3.1. Com o MicroPico instalado, você verá uma barra azul na parte inferior do VS Code.
    3.2. Clique em "Pico Disconnected" (ou use o Command Palette Ctrl+Shift+P e digite MicroPico: Connect).
    3.3. Assim que aparecer "Pico Connected", o terminal do VS Code se tornará o REPL do MicroPython (onde você pode digitar comandos diretamente na placa).

## 🎞 Passo 2: Instalando as Bibliotecas no Pico via VSCode
  Usando a extensão MicroPico:

  1. Crie um novo arquivo no seu projeto no VS Code chamado pico_i2c_lcd.py.

  2. Cole o conteúdo da biblioteca I2C LCD. Como não posso fornecer arquivos diretamente, você pode encontrar a biblioteca padrão "MicroPython I2C LCD" de terceiros pesquisando por esp8266-python/pico_i2c_lcd.py no GitHub ou repositórios similares. Ela é essencial para interpretar os comandos para o módulo I2C.
  
  3. Upload: Clique com o botão direito no arquivo pico_i2c_lcd.py e escolha "MicroPico: Upload current file to Pico". Isso salva a biblioteca dentro da placa.

## 🛠️ Esquema de Ligação (Pinagem)
Abaixo estão as conexões necessárias para o Raspberry Pi Pico (2020), o sensor DHT11 e o Display LCD 16x2 com módulo I2C.

| Componente | Pino no Componente | Pino no Raspberry Pi Pico | Descrição |
| :--- | :--- | :--- | :--- |
| **DHT11** | VCC | 3V3 (Pino 36) | Alimentação 3.3V |
| | DATA | GP28 (Pino 34) | Sinal de Dados |
| | NC | - | Não Conectado (apenas p/ módulo 4 pinos) |
| | GND | GND (Pino 38 ou 3) | Terra |
| **LCD 16x2 I2C** | VCC | VBUS (Pino 40) | Alimentação 5V (Recomendado p/ o LCD) |
| | GND | GND (Pino 38 ou 3) | Terra |
| | SDA | GP4 (Pino 6) | Dados I2C0 SDA |
| | SCL | GP5 (Pino 7) | Clock I2C0 SCL |

---  
