/*
 * Enhanced LoRa Receiver - CORRECTED for 128x32 OLED
 * With ACK/retransmit and ID-based messaging
 */

#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// LoRa pins
#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

// OLED Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET -1

// Node Configuration
#define MY_NODE_ID 0x01      // This node's ID

// Message Types
#define MSG_TYPE_DATA 0x01
#define MSG_TYPE_ACK  0x02
#define MSG_TYPE_NACK 0x03

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

int messagesReceived = 0;
bool oledWorking = false;

void setup() {
  Serial.begin(9600);
  delay(100);
  
  Serial.println(F("LoRa Receiver Starting..."));
  
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
  
  Serial.println(F("LoRa Receiver Ready!"));
  Serial.print(F("My Node ID: 0x"));
  Serial.println(MY_NODE_ID, HEX);
  Serial.println(F("Listening for messages..."));
  
  displayStatus("Setup Successful", false);
  delay(2000);
  displayStatus("Waiting for Reply", false);
}

void loop() {
  if (rf95.available()) {
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    
    if (rf95.recv(buf, &len)) {
      Message msg;
      if (parseMessage(buf, len, &msg)) {
        if (msg.destID == MY_NODE_ID || msg.destID == 0xFF) {
          
          uint8_t calculatedChecksum = calculateChecksum(&msg);
          
          if (calculatedChecksum == msg.checksum) {
            messagesReceived++;
            
            Serial.println(F("========================================"));
            Serial.print(F("Message from Node 0x"));
            Serial.println(msg.nodeID, HEX);
            Serial.print(F("Message Type: "));
            Serial.println(msg.msgType == MSG_TYPE_DATA ? "DATA" : "OTHER");
            Serial.print(F("Payload: "));
            Serial.println(msg.payload);
            Serial.print(F("RSSI: "));
            Serial.println(rf95.lastRssi(), DEC);
            Serial.println(F("Checksum: OK"));
            Serial.println(F("========================================"));
            
            displayStatus("Message Received", false);
            displayReceivedMessage(&msg);
            
            sendAck(msg.nodeID);
            
          } else {
            Serial.println(F("Checksum FAILED - Sending NACK"));
            displayStatus("Checksum Error", true);
            sendNack(msg.nodeID);
            delay(1000);
          }
          
        } else {
          Serial.print(F("Message for Node 0x"));
          Serial.print(msg.destID, HEX);
          Serial.println(F(" - Ignored"));
        }
      }
      
      delay(2000);
      displayStatus("Waiting for Reply", false);
    }
  }
}

bool parseMessage(uint8_t *buf, uint8_t len, Message *msg) {
  if (len < 5) return false;
  
  int idx = 0;
  msg->nodeID = buf[idx++];
  msg->destID = buf[idx++];
  msg->msgType = buf[idx++];
  msg->payloadLen = buf[idx++];
  
  if (msg->payloadLen > 40) return false;
  if (len < idx + msg->payloadLen + 1) return false;
  
  memcpy(msg->payload, &buf[idx], msg->payloadLen);
  msg->payload[msg->payloadLen] = '\0';
  idx += msg->payloadLen;
  
  msg->checksum = buf[idx++];
  
  return true;
}

void sendAck(uint8_t destNodeID) {
  Message ackMsg;
  ackMsg.nodeID = MY_NODE_ID;
  ackMsg.destID = destNodeID;
  ackMsg.msgType = MSG_TYPE_ACK;
  strcpy(ackMsg.payload, "ACK");
  ackMsg.payloadLen = strlen(ackMsg.payload);
  ackMsg.checksum = calculateChecksum(&ackMsg);
  
  sendMessage(&ackMsg);
  
  Serial.print(F("ACK sent to Node 0x"));
  Serial.println(destNodeID, HEX);
}

void sendNack(uint8_t destNodeID) {
  Message nackMsg;
  nackMsg.nodeID = MY_NODE_ID;
  nackMsg.destID = destNodeID;
  nackMsg.msgType = MSG_TYPE_NACK;
  strcpy(nackMsg.payload, "NACK");
  nackMsg.payloadLen = strlen(nackMsg.payload);
  nackMsg.checksum = calculateChecksum(&nackMsg);
  
  sendMessage(&nackMsg);
  
  Serial.print(F("NACK sent to Node 0x"));
  Serial.println(destNodeID, HEX);
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
  
  display.print(F("RX 0x"));
  display.println(MY_NODE_ID, HEX);
  display.println();
  
  if (isError) {
    display.setTextSize(2);
  }
  display.println(status);
  
  if (!isError) {
    display.print(F("Msgs: "));
    display.println(messagesReceived);
  }
  
  display.display();
}

void displayReceivedMessage(Message *msg) {
  if (!oledWorking) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  
  display.println(F("MSG RECEIVED!"));
  display.print(F("From: 0x"));
  display.println(msg->nodeID, HEX);
  display.print(F("RSSI: "));
  display.println(rf95.lastRssi());
  
  display.display();
}
