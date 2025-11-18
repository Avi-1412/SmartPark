#include <SPI.h>
#include <MFRC522.h>

// RFID ENTRADA
#define SS_PIN_ENTRADA 10
#define RST_PIN_ENTRADA 9

// Sensores IR (DIGITAL)
#define SENSOR_A 2
#define SENSOR_B 3
#define SENSOR_C 4
#define SENSOR_D 5

// Lector RFID ENTRADA
MFRC522 mfrc522(SS_PIN_ENTRADA, RST_PIN_ENTRADA);
MFRC522::MIFARE_Key key;

// Estados previos de sensores (para detectar cambios)
int estadoAnteriorA = -1;
int estadoAnteriorB = -1;
int estadoAnteriorC = -1;
int estadoAnteriorD = -1;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  
  pinMode(SENSOR_A, INPUT);
  pinMode(SENSOR_B, INPUT);
  pinMode(SENSOR_C, INPUT);
  pinMode(SENSOR_D, INPUT);
  
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  Serial.println("========================================");
  Serial.println("   ARDUINO 1 - RFID ENTRADA + SENSORES");
  Serial.println("========================================");
  Serial.println("Sistema listo...");
  Serial.println("========================================");
  
  delay(1000);
  // Leer estado inicial de sensores
  estadoAnteriorA = digitalRead(SENSOR_A);
  estadoAnteriorB = digitalRead(SENSOR_B);
  estadoAnteriorC = digitalRead(SENSOR_C);
  estadoAnteriorD = digitalRead(SENSOR_D);
}

void loop() {
  // Verificar cambios en sensores
  verificarCambioSensores();

  // LECTOR ENTRADA
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    procesarTarjeta(mfrc522, "ENTRADA");
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    delay(2000);
  }
}

void verificarCambioSensores() {
  int estadoA = digitalRead(SENSOR_A);
  int estadoB = digitalRead(SENSOR_B);
  int estadoC = digitalRead(SENSOR_C);
  int estadoD = digitalRead(SENSOR_D);
  
  // Detectar cambios y enviar solo si hay cambio
  boolean haycambio = false;
  
  if (estadoA != estadoAnteriorA) {
    estadoAnteriorA = estadoA;
    haycambio = true;
  }
  if (estadoB != estadoAnteriorB) {
    estadoAnteriorB = estadoB;
    haycambio = true;
  }
  if (estadoC != estadoAnteriorC) {
    estadoAnteriorC = estadoC;
    haycambio = true;
  }
  if (estadoD != estadoAnteriorD) {
    estadoAnteriorD = estadoD;
    haycambio = true;
  }
  
  // Enviar solo si hay cambio
  if (haycambio) {
    Serial.print("SENSORES: A=");
    Serial.print(estadoA);
    Serial.print(",B=");
    Serial.print(estadoB);
    Serial.print(",C=");
    Serial.print(estadoC);
    Serial.print(",D=");
    Serial.println(estadoD);
  }
}

void procesarTarjeta(MFRC522 &mfrc522, String tipo) {
  Serial.println("\n========================================");
  Serial.print("✓ TARJETA DETECTADA - ");
  Serial.println(tipo);
  Serial.println("========================================");
  
  Serial.print("UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  byte bloque = 1;
  byte buffer[18];
  byte size = 18;
  
  MFRC522::StatusCode status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, bloque, &key, &(mfrc522.uid));
  
  if (status != MFRC522::STATUS_OK) {
    Serial.print("❌ Error de autenticacion: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    delay(2000);
    return;
  }

  status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(bloque, buffer, &size);
  
  if (status == MFRC522::STATUS_OK) {
    String idUsuario = "";
    for (byte i = 0; i < 16; i++) {
      byte b = buffer[i];
      if (b >= 48 && b <= 57) {
        idUsuario += (char)b;
      } else if (b == 0) {
        break;
      }
    }
    
    if (idUsuario.length() > 0) {
      Serial.print("ID USUARIO: ");
      Serial.println(idUsuario);
      
      Serial.print("JSON: {\"id_usuario\":");
      Serial.print(idUsuario);
      Serial.println("}");
      
      Serial.println("========================================\n");
    } else {
      Serial.println("⚠ Tarjeta sin datos validos");
    }
  } else {
    Serial.print("❌ Error al leer: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(2000);
}
