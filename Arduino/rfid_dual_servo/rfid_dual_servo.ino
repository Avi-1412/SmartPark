#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

// ===== CONFIGURACIÓN RFID =====
#define SS_PIN_ENTRADA 10  // SS para RFID ENTRADA
#define SS_PIN_SALIDA 8    // SS para RFID SALIDA
// SCK = 13, MOSI = 11, MISO = 12 (compartidos)

// ===== CONFIGURACIÓN SERVO =====
#define SERVO_PIN 5        // PWM pin para servo
#define SERVO_OPEN_ANGLE 90    // Ángulo abierto
#define SERVO_CLOSE_ANGLE 0    // Ángulo cerrado
#define SERVO_OPEN_TIME 3000   // 3 segundos abierto

// ===== CONFIGURACIÓN SENSORES IR =====
#define SENSOR_A 2
#define SENSOR_B 3
#define SENSOR_C 4
#define SENSOR_D 5  // NOTA: Si usas pin 5 para servo, cambiar a pin 6
// Para evitar conflicto, cambiaremos SENSOR_D a pin 6

#undef SENSOR_D
#define SENSOR_D 6

// ===== OBJETOS =====
MFRC522 rfidEntrada(SS_PIN_ENTRADA, UINT8_MAX);  // RFID ENTRADA (sin RST)
MFRC522 rfidSalida(SS_PIN_SALIDA, UINT8_MAX);    // RFID SALIDA (sin RST)
Servo servoPluma;

// ===== VARIABLES GLOBALES =====
unsigned long lastServoTime = 0;
bool servoActive = false;
char tipoAcceso = 'X';  // 'E' = ENTRADA, 'S' = SALIDA

// ===== ESTRUCTURA PARA SENSOR STATE CHANGE =====
bool lastSensorState[4] = {HIGH, HIGH, HIGH, HIGH};
int sensorPins[4] = {SENSOR_A, SENSOR_B, SENSOR_C, SENSOR_D};
char sensorNames[4] = {'A', 'B', 'C', 'D'};

void setup() {
  Serial.begin(9600);
  SPI.begin();
  
  // Inicializar RFID módulos
  rfidEntrada.PCD_Init();
  rfidSalida.PCD_Init();
  
  // Inicializar servo
  servoPluma.attach(SERVO_PIN);
  servoPluma.write(SERVO_CLOSE_ANGLE);  // Cerrado al inicio
  
  // Inicializar sensores IR
  pinMode(SENSOR_A, INPUT);
  pinMode(SENSOR_B, INPUT);
  pinMode(SENSOR_C, INPUT);
  pinMode(SENSOR_D, INPUT);
  
  delay(100);
  Serial.println("{\"evento\": \"SISTEMA_INICIADO\"}");
}

void loop() {
  // === MANEJO DE SERVO ===
  if (servoActive && millis() - lastServoTime > SERVO_OPEN_TIME) {
    servoPluma.write(SERVO_CLOSE_ANGLE);
    servoActive = false;
    Serial.println("{\"evento\": \"SERVO_CERRADO\"}");
  }
  
  // === LECTURA RFID ENTRADA ===
  if (rfidEntrada.PICC_IsNewCardPresent() && rfidEntrada.PICC_ReadCardSerial()) {
    String uid = getUIDString(rfidEntrada);
    Serial.print("{\"tipo\": \"ENTRADA\", \"id_usuario\": ");
    Serial.print(uid);
    Serial.println("}");
    rfidEntrada.PICC_HaltA();
    tipoAcceso = 'E';
  }
  
  // === LECTURA RFID SALIDA ===
  if (rfidSalida.PICC_IsNewCardPresent() && rfidSalida.PICC_ReadCardSerial()) {
    String uid = getUIDString(rfidSalida);
    Serial.print("{\"tipo\": \"SALIDA\", \"id_usuario\": ");
    Serial.print(uid);
    Serial.println("}");
    rfidSalida.PICC_HaltA();
    tipoAcceso = 'S';
  }
  
  // === LECTURA SENSORES IR (STATE CHANGE DETECTION) ===
  for (int i = 0; i < 4; i++) {
    bool currentState = digitalRead(sensorPins[i]);
    if (currentState != lastSensorState[i]) {
      // Solo enviar cuando cambia (no continuamente)
      int ocupado = (currentState == LOW) ? 1 : 0;  // LOW = ocupado, HIGH = libre
      Serial.print("{\"tipo\": \"SENSOR\", \"sensor\": \"");
      Serial.print(sensorNames[i]);
      Serial.print("\", \"ocupado\": ");
      Serial.print(ocupado);
      Serial.println("}");
      lastSensorState[i] = currentState;
      delay(50);  // Debounce
    }
  }
  
  // === LECTURA DE COMANDOS DEL BACKEND ===
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    if (comando == "ABRIR_ENTRADA") {
      abrirServo('E');
    } else if (comando == "ABRIR_SALIDA") {
      abrirServo('S');
    }
  }
  
  delay(100);  // Pequeña pausa para evitar lectura constante
}

// ===== FUNCIONES AUXILIARES =====

String getUIDString(MFRC522 &rfid) {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}

void abrirServo(char tipo) {
  servoPluma.write(SERVO_OPEN_ANGLE);
  servoActive = true;
  lastServoTime = millis();
  
  String evento = (tipo == 'E') ? "SERVO_ABIERTO_ENTRADA" : "SERVO_ABIERTO_SALIDA";
  Serial.print("{\"evento\": \"");
  Serial.print(evento);
  Serial.println("\"}");
}
