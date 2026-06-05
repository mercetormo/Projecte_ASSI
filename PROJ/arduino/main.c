#include <avr/io.h>
#include <stdint.h>
#include <stdio.h>

#include "serial_device.h"
#include "printf2serial.h"
#include "adc.h"

#define LED PB5

int main(void)
{
    char cmd;
    uint8_t estat = 0;

    DDRB |= (1 << LED);
    PORTB &= ~(1 << LED); //apagat

    serial_open();
    init_stdout();

    setup_ADC(1, 5, 128); // pin A1, referència 5V, prescaler 128
    start_ADC();

    while (1){
      if (serial_can_read()){
	cmd = serial_get();
	switch (cmd){
	case '1':
	  estat = 1;
	  PORTB |= (1 << LED);
	  printf("1\n");
	  break;

	case '0':
	  estat = 0;
	  PORTB &= ~(1 << LED);
	  printf("0\n");
	  break;

	case '?':
	  printf("%d\n", estat);
	  break;
	case 'P':
	  start_ADC();
	  printf("%u\n", read8_ADC());
	  break;
	      
	}
      }
    }
    return 0;
}
