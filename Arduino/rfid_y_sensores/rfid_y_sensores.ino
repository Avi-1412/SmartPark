#include <SPI.h>
#include <MFRC522.h>

// RFID ENTRADA
#define SS_PIN_ENTRADA 10
#define RST_PIN_ENTRADA 9

// RFID SALIDA
#define SS_PIN_SALIDA 8
#define RST_PIN_SALIDA 7

// Pines de los sensores IR (DIGITAL)
#define SENSOR_A 2
#define SENSOR_B 3
#define SENSOR_C 4
#define SENSOR_D 5

// Lectores RFID
MFRC522 mfrc522_entrada(SS_PIN_ENTRADA, RST_PIN_ENTRADA);
MFRC522 mfrc522_salida(SS_PIN_SALIDA, RST_PIN_SALIDA);
MFRC522::MIFARE_Key key;

// Timers para no bloquear
unsigned long ultimoEnvioSensores = 0;
const unsigned long INTERVALO_SENSORES = 10000; // 10 segundos

void setup() {
  Serial.begin(9600);
  SPI.begin();
  
  // Inicializar ambos lectores RFID
  mfrc522_entrada.PCD_Init();
  mfrc522_salida.PCD_Init();
  
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
  Serial.println("   RFID ENTRADA + SALIDA + SENSORES");
  Serial.println("========================================");
  Serial.println("Sistema listo...");
  Serial.println("========================================");
  
  // Enviar primer lectura de sensores
  delay(1000);
  enviarEstadoSensores();
}

void loop() {
  // Enviar estado de sensores cada 10 segundos
  if (millis() - ultimoEnvioSensores >= INTERVALO_SENSORES) {
    enviarEstadoSensores();
    ultimoEnvioSensores = millis();
  }

  // LECTOR ENTRADA
  if (mfrc522_entrada.PICC_IsNewCardPresent() && mfrc522_entrada.PICC_ReadCardSerial()) {
    procesarTarjeta(mfrc522_entrada, "ENTRADA");
    mfrc522_entrada.PICC_HaltA();
    mfrc522_entrada.PCD_StopCrypto1();
    delay(2000);
  }

  // LECTOR SALIDA
  if (mfrc522_salida.PICC_IsNewCardPresent() && mfrc522_salida.PICC_ReadCardSerial()) {
    procesarTarjeta(mfrc522_salida, "SALIDA");
    mfrc522_salida.PICC_HaltA();
    mfrc522_salida.PCD_StopCrypto1();
    delay(2000);
  }
}

// Función para procesar tarjeta (entrada o salida)
void procesarTarjeta(MFRC522 &mfrc522, String tipo) {
  Serial.println("\n========================================");
  Serial.print("✓ TARJETA DETECTADA - ");
  Serial.println(tipo);
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
      
      // Enviar en formato JSON para el backend con tipo de transacción
      Serial.print("JSON: {\"id_usuario\":");
      Serial.print(idUsuario);
      Serial.print(",\"tipo\":\"");
      Serial.print(tipo);
      Serial.println("\"}");
      
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

// FUNCIÓN para leer y enviar estado de sensores
void enviarEstadoSensores() {
  // Leer valores DIGITALES
  int estadoA = digitalRead(SENSOR_A);
  int estadoB = digitalRead(SENSOR_B);
  int estadoC = digitalRead(SENSOR_C);
  int estadoD = digitalRead(SENSOR_D);
  
  // ENVIAR SIEMPRE (no solo cuando hay cambios)
  Serial.print("SENSORES: A=");
  Serial.print(estadoA);
  Serial.print(",B=");
  Serial.print(estadoB);
  Serial.print(",C=");
  Serial.print(estadoC);
  Serial.print(",D=");
  Serial.println(estadoD);
}
