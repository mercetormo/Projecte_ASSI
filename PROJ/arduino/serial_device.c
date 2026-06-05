#include <avr/io.h>//it includes <avr/sfr_defs.h>, <avr/portpins.h>, <avr/common.h>, <avr/version.h>
 
#include "serial_device.h"

//#define BAUD_9600

void serial_open(void){
  //table 20-7 pg. 190
#ifdef BAUD_9600
  //set baud rate to 9600bps
  UBRR0=103;
#else
  //set baud rate to 115200bps
  UBRR0=16;
  UCSR0A=UCSR0A|(1<<U2X0);
#endif
  UCSR0B |=(1<<RXEN0)|(1<<TXEN0);
}

void serial_close(void){
    //disable reception, transmission 
  UCSR0B &=~((1<<RXEN0)|(1<<TXEN0));
}

uint8_t serial_get(void) {
  // polling on RXC until data received
  loop_until_bit_is_set(UCSR0A, RXC0);
  return UDR0;
}

bool serial_can_read(void) {
  // test whether there is something to read
  return bit_is_set(UCSR0A, RXC0);
}

void serial_put(uint8_t c) {
  // wait last transmision finishes
  loop_until_bit_is_set(UCSR0A, UDRE0);
  // send new byte
  UDR0 = c;
}
