#include <Arduino.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <NewPing.h>

#define SERIAL_BAUD 115200

#define DHTPIN 2
#define TRIG_PIN 4
#define ECHO_PIN 5
#define LDR_PIN A0

#define DHTTYPE DHT11
#define MAX_DISTANCE 400

DHT dht(DHTPIN, DHTTYPE);
NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

unsigned long lastReadTime = 0;
const unsigned long readInterval = 2000;

void setupSensors()
{
  dht.begin();
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void readAndSendSensors()
{

  static float temp = 0.0;
  static float hum = 0.0;

  if (millis() - lastReadTime >= readInterval)
  {
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (!isnan(t) && !isnan(h))
    {
      temp = t;
      hum = h;
    }
    lastReadTime = millis();
  }

  int ldr = analogRead(LDR_PIN);

  unsigned int pingTempo = sonar.ping_median(5);
  float distanciaReal = 0.0;

  if (pingTempo > 0)
  {

    float speedOfSound = (331.4 + (0.606 * temp)) / 10000.0;

    distanciaReal = (pingTempo * speedOfSound) / 2.0;
  }

  JsonDocument doc;
  doc["temp"] = temp;
  doc["hum"] = hum;
  doc["ldr"] = ldr;

  if (distanciaReal <= 0.0 || distanciaReal > MAX_DISTANCE)
  {
    doc["distance_cm"] = nullptr;
  }
  else
  {

    doc["distance_cm"] = round(distanciaReal * 100.0) / 100.0;
  }

  serializeJson(doc, Serial);
  Serial.println();
}

void setup()
{
  Serial.begin(SERIAL_BAUD);
  setupSensors();
  delay(2000);
}

void loop()
{
  readAndSendSensors();
  delay(100);
}
