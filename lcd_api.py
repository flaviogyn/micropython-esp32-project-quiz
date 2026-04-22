from time import sleep_ms


class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02

    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01

    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01

    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04

    LCD_FUNCTION = 0x20
    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_10DOTS = 0x04
    LCD_FUNCTION_RESET = 0x30

    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    LCD_RS_CMD = 0
    LCD_RS_DATA = 1

    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.backlight = True

        if self.num_lines > 4:
            self.num_lines = 4
        if self.num_columns > 40:
            self.num_columns = 40

        self.display_control = self.LCD_ON_DISPLAY
        self.display_mode = self.LCD_ENTRY_INC

        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.display_mode)
        self.show_cursor(False)
        self.blink_cursor_off()
        self.display_on()

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        self.hal_write_command(self.LCD_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self, cursor_on):
        if cursor_on:
            self.display_control |= self.LCD_ON_CURSOR
        else:
            self.display_control &= ~self.LCD_ON_CURSOR
        self.hal_write_command(self.LCD_ON_CTRL | self.display_control)

    def blink_cursor_on(self):
        self.display_control |= self.LCD_ON_BLINK
        self.hal_write_command(self.LCD_ON_CTRL | self.display_control)

    def blink_cursor_off(self):
        self.display_control &= ~self.LCD_ON_BLINK
        self.hal_write_command(self.LCD_ON_CTRL | self.display_control)

    def display_on(self):
        self.display_control |= self.LCD_ON_DISPLAY
        self.hal_write_command(self.LCD_ON_CTRL | self.display_control)

    def display_off(self):
        self.display_control &= ~self.LCD_ON_DISPLAY
        self.hal_write_command(self.LCD_ON_CTRL | self.display_control)

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y

        addr = cursor_x & 0x3F
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += self.num_columns
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putchar(self, char):
        if char == "\n":
            self.cursor_x = self.num_columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1

        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        location &= 0x7
        self.hal_write_command(self.LCD_CGRAM | (location << 3))
        sleep_ms(1)
        for i in range(8):
            self.hal_write_data(charmap[i])
            sleep_ms(1)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError
