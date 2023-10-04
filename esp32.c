#include <HardwareSerial.h>

#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "63";
const char* password = "06129521";
const char* serverURL = "http://192.168.0.200:5000/update";
AsyncWebServer server(80);

/* Отправка информации полученный с STM32 на сервер flask*/
void sendToServer(String data) {
  float temperature = -128.0;
  float humidity = -128.0;
  int adcValue = -128;
  int soilMoisture = -128;
  String jsonData = "{\"data\": \"none\"}";

  int parsedValues = sscanf(data.c_str(), "%f, %f, %d, %d", &temperature, &humidity, &adcValue, &soilMoisture);
  if (parsedValues == 4) {
    temperature *= 0.1f;
    humidity *= 0.1f;
    if (temperature >= -30 && temperature <= 50 && 
        humidity >= 0 && humidity <= 100 &&
        adcValue >=0 && adcValue <=5000 &&
        soilMoisture >= 0 && soilMoisture <=100
        ) {
      jsonData = "{\"temperature\":" + String(temperature, 1) +
                 ", \"humidity\":" + String(humidity, 1) +
                 ", \"adc\":" + String(adcValue) +
                 ", \"moisture\":" + String(soilMoisture) + "}";
    }
  }
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      String response = http.getString(); 
      Serial.println(response);

    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }    
}

/* Обработка запроса прешедшего с сервера flask*/
void handleCommand(AsyncWebServerRequest *request) {
  if (request->hasParam("relay")) {
    String relayValue = request->getParam("relay")->value();

    for (size_t i = 0; i < relayValue.length(); i++) {
      if (!isDigit(relayValue[i])) {
        Serial.println("Relay value is not a valid number");
        request->send(400, "application/json", "{\"status\":\"not a number\"}");
        return;
      }
    }
    int relayIntValue = relayValue.toInt();
    if (relayIntValue == 1) {
      Serial.println("Relay value: " + String(relayIntValue));
      Serial2.println(String(relayIntValue));
      request->send(200, "application/json", "{\"status\":\"success\"}");
    } else {
      Serial.println("Relay value is not in the range [1, 10]");
      request->send(400, "application/json", "{\"status\":\"not in range\"}");
    }
  } else {
      request->send(400, "application/json", "{\"status\":\"Is not relay\"}");
  } 
}

void setup() {

  Serial.begin(115200);
  Serial2.begin(115200);

  // Настройка статического IP-адреса
  IPAddress staticIP(192, 168, 0, 201); // ip-адрес
  IPAddress gateway(192, 168, 0, 1);   // основной шлюз
  IPAddress subnet(255, 255, 255, 0);  // маска подсети
  WiFi.config(staticIP, gateway, subnet);

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Подключение к Wi-Fi...");
  }
  Serial.println("Подключение прошло успешно");

  Serial.print("IP-адрес ESP32: ");
  Serial.println(WiFi.localIP()); // Вывод IP-адреса ESP32
  
  server.on("/command", HTTP_GET, handleCommand);
  server.begin();

  
  //xTaskCreate(sendDataToServerTask, "SendDataTask", 10000, NULL, 1, NULL);
  //xTaskCreate(httpServerTask, "httpServerTask", 10000, NULL, 1, NULL);
}


void loop() {

  String receivedData = Serial2.readStringUntil('\n');
  if (receivedData.length() > 0 && receivedData.length() < 100) {
    Serial.println(receivedData);
    Serial.println(receivedData.length());
    sendToServer(receivedData);
  }
  Serial2.flush();
}