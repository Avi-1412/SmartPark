#include <SPI.h>
#include <MFRC522.h>

// RFID SALIDA
#define SS_PIN_SALIDA 10
#define RST_PIN_SALIDA 9

// Lector RFID SALIDA
MFRC522 mfrc522(SS_PIN_SALIDA, RST_PIN_SALIDA);
MFRC522::MIFARE_Key key;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  Serial.println("========================================");
  Serial.println("   ARDUINO 2 - RFID SALIDA");
  Serial.println("========================================");
  Serial.println("Sistema listo...");
  Serial.println("========================================");
}

void loop() {
  // LECTOR SALIDA
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    procesarTarjeta(mfrc522, "SALIDA");
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    delay(2000);
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
