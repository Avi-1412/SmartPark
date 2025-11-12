#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

// Pines de los sensores IR
#define SENSOR_A A0
#define SENSOR_B A1
#define SENSOR_C A2
#define SENSOR_D A3

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

unsigned long ultimoMensaje = 0;
unsigned long ultimoEnvioSensores = 0;
const unsigned long INTERVALO_SENSORES = 10000; // 10 segundos

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  
  // Configurar pines de sensores como entrada
  pinMode(SENSOR_A, INPUT);
  pinMode(SENSOR_B, INPUT);
  pinMode(SENSOR_C, INPUT);
  pinMode(SENSOR_D, INPUT);
  
  // Inicializar clave por defecto
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  Serial.println("========================================");
  Serial.println("   LECTOR RFID + SENSORES IR");
  Serial.println("========================================");
  Serial.println("Sistema listo. Acerca una tarjeta...");
  Serial.println("========================================");
}

void loop() {
  // Mostrar mensaje cada 3 segundos si no hay tarjeta
  if (millis() - ultimoMensaje >= 3000) {
    Serial.println("Esperando tarjeta...");
    ultimoMensaje = millis();
  }

  // Enviar estado de sensores cada 10 segundos
  if (millis() - ultimoEnvioSensores >= INTERVALO_SENSORES) {
    enviarEstadoSensores();
    ultimoEnvioSensores = millis();
  }

  // Verificar si hay una nueva tarjeta
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  Serial.println("\n========================================");
  Serial.println("✓ TARJETA DETECTADA");
  Serial.println("========================================");
  
  // Mostrar UID
  Serial.print("UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Leer el ID usuario del bloque 1
  byte bloque = 1;
  byte buffer[18];
  byte size = 18;
  
  // Autenticar
  MFRC522::StatusCode status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, bloque, &key, &(mfrc522.uid));
  
  if (status != MFRC522::STATUS_OK) {
    Serial.print("❌ Error de autenticación: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    delay(2000);
    return;
  }

  // Leer datos
  status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(bloque, buffer, &size);
  
  if (status == MFRC522::STATUS_OK) {
    // Extraer el ID usuario (solo números 0-9)
    String idUsuario = "";
    for (byte i = 0; i < 16; i++) {
      byte b = buffer[i];
      // Validar que sea un número ASCII (48-57)
      if (b >= 48 && b <= 57) {
        idUsuario += (char)b;
      } else if (b == 0) {
        // Fin de la cadena
        break;
      }
    }
    
    if (idUsuario.length() > 0) {
      Serial.print("ID USUARIO: ");
      Serial.println(idUsuario);
      
      // Enviar en formato JSON para el backend
      Serial.print("JSON: {\"id_usuario\":");
      Serial.print(idUsuario);
      Serial.println("}");
      
      Serial.println("========================================\n");
    } else {
      Serial.println("⚠ Tarjeta sin datos válidos");
    }
  } else {
    Serial.print("❌ Error al leer: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
  }

  // Detener lectura
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  // Esperar 2 segundos
  delay(2000);
}

// FUNCIÓN para enviar estado de sensores
void enviarEstadoSensores() {
  // Leer valores analógicos RAW
  int rawA = analogRead(SENSOR_A);
  int rawB = analogRead(SENSOR_B);
  int rawC = analogRead(SENSOR_C);
  int rawD = analogRead(SENSOR_D);
  
  Serial.print("[DEBUG] RAW VALUES - A:");
  Serial.print(rawA);
  Serial.print(" B:");
  Serial.print(rawB);
  Serial.print(" C:");
  Serial.print(rawC);
  Serial.print(" D:");
  Serial.println(rawD);
  
  // INVERTIR LÓGICA: < 100 = ocupado (en lugar de > 100)
  int ocupadoA = (rawA < 100) ? 1 : 0;
  int ocupadoB = (rawB < 100) ? 1 : 0;
  int ocupadoC = (rawC < 100) ? 1 : 0;
  int ocupadoD = (rawD < 100) ? 1 : 0;
  
  // Enviar formato simple: SENSORES: A=1,B=0,C=1,D=0
  Serial.print("SENSORES: A=");
  Serial.print(ocupadoA);
  Serial.print(",B=");
  Serial.print(ocupadoB);
  Serial.print(",C=");
  Serial.print(ocupadoC);
  Serial.print(",D=");
  Serial.println(ocupadoD);
}
