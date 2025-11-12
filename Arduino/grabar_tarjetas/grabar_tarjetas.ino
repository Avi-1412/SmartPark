#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  
  // Inicializar clave por defecto (FFFFFFFFFFFF)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  Serial.println("========================================");
  Serial.println("   GRABADOR DE TARJETAS RFID");
  Serial.println("========================================");
  Serial.println("Acerca una tarjeta para grabar el ID usuario");
  Serial.println("Ingresa el ID (100, 200, 300, etc.)");
  Serial.println("========================================");
}

void loop() {
  // Verificar si hay una nueva tarjeta
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Intentar leer la tarjeta
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  Serial.println("\n✓ Tarjeta detectada!");
  
  // Mostrar UID
  Serial.print("UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Pedir ID usuario
  Serial.println("\n¿Qué ID de usuario deseas grabar? (ej: 100, 200, 300)");
  Serial.println("Ingresa el número y presiona ENTER:");
  
  // Esperar a que el usuario ingrese datos
  while (!Serial.available()) {
    delay(100);
  }
  
  String idUsuario = Serial.readStringUntil('\n');
  idUsuario.trim();
  
  Serial.print("ID a grabar: ");
  Serial.println(idUsuario);

  // Grabar el ID en el bloque 1
  byte bloque = 1;
  byte datos[16];
  
  // Limpiar el array
  memset(datos, 0, 16);
  
  // Copiar el ID usuario al array (convertir string a bytes)
  for (byte i = 0; i < idUsuario.length() && i < 16; i++) {
    datos[i] = (byte)idUsuario[i];
  }
  
  // Autenticar
  MFRC522::StatusCode status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, bloque, &key, &(mfrc522.uid));
  
  if (status != MFRC522::STATUS_OK) {
    Serial.print("❌ Error de autenticación: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    return;
  }

  // Escribir datos
  status = mfrc522.MIFARE_Write(bloque, datos, 16);
  
  if (status == MFRC522::STATUS_OK) {
    Serial.println("✓ ¡Tarjeta grabada exitosamente!");
    Serial.print("ID guardado: ");
    Serial.println(idUsuario);
    Serial.println("========================================\n");
  } else {
    Serial.print("❌ Error al grabar: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
  }

  // Detener lectura
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  // Esperar 2 segundos antes de siguiente lectura
  delay(2000);
  Serial.println("Acerca otra tarjeta...");
}
