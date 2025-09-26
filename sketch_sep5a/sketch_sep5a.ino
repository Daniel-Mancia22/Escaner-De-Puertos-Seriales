void setup() {
  Serial.begin(115200);   // Velocidad de comunicación con el puerto serial
}

void loop() {
  Serial.println("Hola desde Arduino @115200");
  delay(500); // Espera 500ms antes de enviar el siguiente mensaje
}
