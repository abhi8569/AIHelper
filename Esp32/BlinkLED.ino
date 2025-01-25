#include <Arduino.h>

void setup() {
  // Initialize digital pin IO8 as an output
  pinMode(8, OUTPUT);
}

void loop() {
  digitalWrite(8, HIGH);   // Turn the LED on
  delay(1000);             // Wait for a second
  digitalWrite(8, LOW);    // Turn the LED off
  delay(1000);             // Wait for a second
}
