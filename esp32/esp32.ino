#include "WiFi.h"
#include "WebServer.h"
#include "ArduinoJson.h"
#include "HTTPClient.h"
#include "DHT.h"

#define dhtPin 4
#define dhtType DHT11

const char* ssid = ""; //wifi name 
const char* password = ""; //wifi pass
WebServer server(80);

DHT dht(dhtPin, dhtType);

int pin1 = 23;
int pin2 = 22;
int pin3 = 21;

bool bulb1=false;
bool bulb2=false;
bool fan=false;
float temperature = 0.0;

void handlePost();
void sendPostRequest();
void Bulb1Change();
void Bulb2Change();
void FanChange();

unsigned long previousMillis = 0;
const long interval = 2000;

void setup() {
  Serial.begin(115200);
  //-------------------------------------------------wifi part-----------------------------------------
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());
  server.on("/data", HTTP_POST, handlePost);
  server.begin();
  Serial.println("Server started");

  // ------------------------------------------------connection-----------------------------------------

  dht.begin();

  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  pinMode(pin3, OUTPUT);
  Bulb1Change();
  Bulb2Change();
  FanChange();

}

 //-----------------------------------------------------loop-------------------------------------------
void loop() {
  unsigned long currentMillis = millis();

  server.handleClient();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    Bulb1Change();
    Bulb2Change();
    FanChange();
    sendPostRequest();
  }

}


 //--------------------------------------------------functions---------------------------------------------

void Bulb1Change()  {
  if(!bulb1){
    digitalWrite(pin1, HIGH);
  } else {
    digitalWrite(pin1, LOW);
  }
}

void Bulb2Change()  {
  if(!bulb2){
    digitalWrite(pin2, HIGH);
  } else {
    digitalWrite(pin2, LOW);
  }
}

void FanChange()  {
  if((fan) && (temperature>33.0)){
    digitalWrite(pin3, LOW);
  } else {
    digitalWrite(pin3, HIGH);
  }
}

//----------------------------------------------getting states(bulb, fan)  ---------------------------------------------------------


void handlePost() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "No body received");
    return;
  }

  String json = server.arg("plain");
  Serial.println("Received JSON: " + json);

  // Parse JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, json);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  bulb1 = doc["bulb1"];
  bulb2 = doc["bulb2"];
  fan = doc["fan"];

  server.send(200, "application/json", "{\"status\":\"received\"}");
}


//----------------------------------------------sending temperature ---------------------------------------------------------
void sendPostRequest() {

  temperature = dht.readTemperature();

  if (isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Skipping POST request.");
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  String postData = "{\"temperature\": " + String(temperature, 2) + "}";

  HTTPClient http;
  String serverUrl = "http://192.xxx.xx.x/sendTemp";  // add your ip address
  http.begin(serverUrl);

  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(postData);

  if (httpResponseCode > 0) {
    Serial.print("POST Request sent successfully. Response code: ");
    Serial.println(httpResponseCode);
    String response = http.getString();
    Serial.println("Response: " + response);
  } else {
    Serial.print("Error sending POST request. Response code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}