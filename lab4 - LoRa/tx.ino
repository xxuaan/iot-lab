/*
 * Enhanced LoRa Transmitter - CORRECTED for 128x32 OLED
 * With ACK/retransmit and ID-based messaging
 */

#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// LoRa pins for Cytron LoRa-RFM Shield
#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

// OLED Display settings - CORRECTED TO 128x32
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32  // Changed from 64 to 32!F
#define OLED_RESET -1

// Node Configuration
#define MY_NODE_ID 0x02      // This node's ID
#define DEST_NODE_ID 0x01    // Destination node ID

// Message Types
#define MSG_TYPE_DATA 0x01
#define MSG_TYPE_ACK  0x02
#define MSG_TYPE_NACK 0x03

// Transmission settings
#define MAX_RETRIES 3
#define ACK_TIMEOUT 10000     // 10 seconds

// RF95 frequency
#define RF95_FREQ 915.5

// Message structure
struct Message {
  uint8_t nodeID;
  uint8_t destID;
  uint8_t msgType;
  uint8_t payloadLen;
  char payload[40];
  uint8_t checksum;
};

RH_RF95 rf95(RFM95_CS, RFM95_INT);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

int messageCounter = 0;
bool oledWorking = false;

void setup() {
  Serial.begin(9600);
  delay(100);
  
  Serial.println(F("LoRa Transmitter Starting..."));
  
  // Initialize OLED first
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    Serial.println(F("Continuing without OLED..."));
  } else {
    Serial.println(F("OLED OK!"));
    oledWorking = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.println(F("Initializing..."));
    display.display();
  }
  
  // Reset LoRa module
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  
  // Initialize LoRa
  if (!rf95.init()) {
    Serial.println(F("LoRa init failed"));
    displayStatus("Setup Failed", true);
    while (1);
  }
  
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println(F("setFrequency failed"));
    displayStatus("Setup Failed", true);
    while (1);
  }
  
  rf95.setTxPower(23, false);
  
  Serial.println(F("LoRa Transmitter Ready!"));
  Serial.print(F("My Node ID: 0x"));
  Serial.println(MY_NODE_ID, HEX);
  
  displayStatus("Setup Successful", false);
  delay(2000);
}

void loop() {
  // Create message
  Message msg;
  msg.nodeID = MY_NODE_ID;
  msg.destID = DEST_NODE_ID;
  msg.msgType = MSG_TYPE_DATA;
  
  sprintf(msg.payload, "payload #%d from Node %d", messageCounter++, MY_NODE_ID);
  msg.payloadLen = strlen(msg.payload);
  msg.checksum = calculateChecksum(&msg);
  
  // Send message with retries
  bool ackReceived = false;
  int retries = 0;
  
  while (!ackReceived && retries < MAX_RETRIES) {
    Serial.print(F("Sending (Attempt "));
    Serial.print(retries + 1);
    Serial.print(F("/"));
    Serial.print(MAX_RETRIES);
    Serial.println(F(")..."));
    
    displayStatus("Sending Message", false);
    
    sendMessage(&msg);
    
    displayStatus("Waiting for Reply", false);
    ackReceived = waitForAck(ACK_TIMEOUT);
    
    if (ackReceived) {
      Serial.println(F("ACK Received!"));
      displayStatus("Message Received", false);
    } else {
      Serial.println(F("No ACK - Retrying..."));
      retries++;
      if (retries < MAX_RETRIES) {
        delay(500);
      }
    }
  }
  
  if (!ackReceived) {
    Serial.println(F("Message failed after max retries"));
    displayStatus("Send Failed", true);
    delay(2000);
  }
  
  delay(3000);
}

void sendMessage(Message *msg) {
  uint8_t buf[60];
  int len = 0;
  
  buf[len++] = msg->nodeID;
  buf[len++] = msg->destID;
  buf[len++] = msg->msgType;
  buf[len++] = msg->payloadLen;
  memcpy(&buf[len], msg->payload, msg->payloadLen);
  len += msg->payloadLen;
  buf[len++] = msg->checksum;
  
  rf95.send(buf, len);
  rf95.waitPacketSent();
  
  Serial.print(F("Sent to Node 0x"));
  Serial.print(msg->destID, HEX);
  Serial.print(F(": "));
  Serial.println(msg->payload);
}

bool waitForAck(unsigned long timeout) {
  unsigned long startTime = millis();
  
  while (millis() - startTime < timeout) {
    if (rf95.available()) {
      uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
      uint8_t len = sizeof(buf);
      
      if (rf95.recv(buf, &len)) {
        if (len >= 5) {
          uint8_t nodeID = buf[0];
          uint8_t destID = buf[1];
          uint8_t msgType = buf[2];
          
          if (destID == MY_NODE_ID && msgType == MSG_TYPE_ACK) {
            Serial.print(F("ACK from Node 0x"));
            Serial.println(nodeID, HEX);
            return true;
          }
        }
      }
    }
    delay(10);
  }
  return false;
}

uint8_t calculateChecksum(Message *msg) {
  uint8_t checksum = 0;
  checksum ^= msg->nodeID;
  checksum ^= msg->destID;
  checksum ^= msg->msgType;
  checksum ^= msg->payloadLen;
  for (int i = 0; i < msg->payloadLen; i++) {
    checksum ^= msg->payload[i];
  }
  return checksum;
}

void displayStatus(const char* status, bool isError) {
  if (!oledWorking) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  
  display.print(F("TX 0x"));
  display.println(MY_NODE_ID, HEX);
  display.println();
  
  if (isError) {
    display.setTextSize(2);
  }
  display.println(status);
  display.display();
}
