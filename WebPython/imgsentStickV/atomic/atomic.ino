/*This is an example used ,you can can view gps data by connecting
   to Bluetooth assistant on your mobilephone or Serial Monitor
   the GPS log will be written to SD card

  memo
*/
/*
  ################### メモ
  3秒以上長押しで終了、起動の際、5秒以上長押しで設定モードへの簡易

*/
#include <WiFi.h>
#include <WiFiClient.h>
#include "M5Atom.h"
#include "GPSAnalyse.h"
#include <Preferences.h>
Preferences prefs;

#include <WebServer.h>
#include <HTTPClient.h>
WebServer server(80);
#include <ArduinoJson.h>


String ssid_TH = "";
String password_TH = "";

// SSID設定モードの状態変数
boolean Settingmodestate = false;

//TCP
const char* ssid     = "";
const char* password = "";
//const char *ssid = "";
//const char *password = "";

char host[20] = "192.168.0.9";
int port = 44446;

static const uint8_t packet_begin[3] = { 0xFF, 0xD8, 0xEA };

GPSAnalyse GPS;
#define BTN_pin GPIO_NUM_39
uint64_t chipid;
char chipname[256];
byte MACadress[6];



float Lat;
float Lon;
String Utc;

String getMacAddress() {
  byte mac[6];
 
  WiFi.macAddress(mac);
  String cMac = "";
  for (int i = 0; i < 6; ++i) {
    if (mac[i] < 0x10) {
      cMac += "0";
    }
    cMac += String(mac[i], HEX);
//    if (i < 5)
//      cMac += ":"; // put : or - if you want byte delimiters
  }
  cMac.toUpperCase();
  return cMac;
}
// ファイル名にGPSの情報を追加する関数
String filenameproc(String rcvfilename) {
  unsigned int index = rcvfilename.lastIndexOf('.');
  String filename = rcvfilename.substring(0, index);
  if (Utc == "") Utc = "None";
  filename = filename + "_" + String(Lat) + "_" + String(Lon) + "_" + Utc + ".jpg";
  //Serial.println(filename);
  return filename;
}

void getvideo() {
  int state = 1;
  unsigned long count = 0;
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    return;
  }
  Serial.println("getvideo");
  const unsigned int avitmpbufsize = 12000;
  uint8_t *aviFile_buf = (uint8_t *) malloc(sizeof(uint8_t) * avitmpbufsize);

  boolean started_download_video = false;
  unsigned long int videofilesizecnt = 0;
  //  client.print("sample.jpg"); //filename
  Serial.print("G");
  Serial2.print('G');
  boolean namesendflag = false;
  while (state) {
    if (Serial2.available()) {
      count = 0;
      uint8_t rx_buffer[50];
      int rx_size = Serial2.readBytes(rx_buffer, 50);
      if ((rx_buffer[0] == packet_begin[0]) && (rx_buffer[1] == packet_begin[1]) && (rx_buffer[2] == packet_begin[2])) {
        int datalength = (uint32_t)(rx_buffer[4] << 16) | (rx_buffer[5] << 8) | rx_buffer[6];
        rx_size = Serial2.readBytes(aviFile_buf, datalength);
        String rcvfilename = (char*)(rx_buffer + 10);
        rcvfilename = filenameproc(rcvfilename);
        if (!namesendflag) {
          //client.print(rcvfilename); //filename ;
          //          char rcvbuff[30];
          //          rcvfilename.toCharArray(rcvbuff,rcvfilename.length());
          client.write(rcvfilename.c_str(), rcvfilename.length()); //filename ;
          delay(3);
          Serial.println(rcvfilename);
          String MACandPASS = getMacAddress() + ",0hqhf0j==fak;=0fq";
          client.write(MACandPASS.c_str(), MACandPASS.length()); //filename ;
          delay(10);
          Serial.println(MACandPASS);
        } else {
          namesendflag = true;
        }
        Serial.print(videofilesizecnt); Serial.print("  ");
        delay(3);
        client.write(aviFile_buf, datalength);
        videofilesizecnt += rx_size;
        delay(3);
        Serial2.print('+');
      }

      if (rx_size > 100) {
        started_download_video = true;
      } else if (rx_size == 0 && started_download_video) {
        Serial.println("");
        Serial.print("finish sending video:");
        Serial.println(videofilesizecnt);
        client.stop();
        break;
      }
    } else {
      count++;
    }
    delay(1);
    if (count > 5000) {
      if (started_download_video) {
        Serial.println("");
        Serial.print("send video:");
        Serial.println(videofilesizecnt);
        client.stop();
        break;
      }
      state = 0;
      Serial.println("count is up");
      Serial.println("time up");
    }
  }
}
void wifisettingmode() {
  Serial.println(F("MODE: set up..."));
  Settingmodestate = true;
  //いらない変数の解放（しないと処理できない）
  /* You can remove the password parameter if you want the AP to be open. */
  //アクセスポイントを起動する
  const char *ssid_AP = "Ficy_AICAM";
  const char *password_AP = "";
  WiFi.persistent(false);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid_AP, password_AP);
  //WiFi.softAPConfig(IPAddress(192, 168, 4, 2), IPAddress(192, 168, 4, 1), IPAddress(255, 255, 255, 0));
  IPAddress myIP = WiFi.softAPIP();
  Serial.print(F("AP IP address: "));
  Serial.println(myIP);

  /* Start Web Server server */
  server.on("/", onRoot);
  server.on("/set", setdata_SSID_PW);

  server.begin();
  Serial.println(F("Web server started"));
  while (1) {
    server.handleClient();
    if (checkbtn() > 30) { //over 3sec, 3秒以上長押しで終了
      esp_restart();//ESPのリセットにより、Wifiなどをクリアしてスリープに入る
    }
  }
}
unsigned int IntoSleep() {
  esp_light_sleep_start();
  esp_sleep_wakeup_cause_t wakeup_reason;
  wakeup_reason = esp_sleep_get_wakeup_cause();
  switch (wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0      : Serial.printf("外部割り込み(RTC_IO)で起動\n"); break;
    case ESP_SLEEP_WAKEUP_EXT1      : Serial.printf("外部割り込み(RTC_CNTL)で起動 IO=%llX\n", esp_sleep_get_ext1_wakeup_status()); break;
    case ESP_SLEEP_WAKEUP_TIMER     : Serial.printf("タイマー割り込みで起動\n"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD  : Serial.printf("タッチ割り込みで起動\n"); break;
    case ESP_SLEEP_WAKEUP_ULP       : Serial.printf("ULPプログラムで起動\n"); break;
    case ESP_SLEEP_WAKEUP_GPIO      : Serial.printf("ライトスリープからGPIO割り込みで起動\n"); break;
    case ESP_SLEEP_WAKEUP_UART      : Serial.printf("ライトスリープからUART割り込みで起動\n"); break;
    default                         : Serial.printf("スリープ以外からの起動\n"); break;
  }
  unsigned long  cnt = 0;
  int inputvalue = digitalRead(BTN_pin);
  delay(500);//CPUがまだ起きていない場合
  while (0 == digitalRead(BTN_pin)) {//ボタンを話した時に抜ける
    cnt++;
    delay(100);
  }
  Serial.print("cnt:"); Serial.println(cnt);
  if (cnt > 60) { //over 6ssec
    wifisettingmode();//この関数は最終的にESPのリセットで終了する
  }
  return cnt;
}

void setup() {

  M5.begin(true, false, true);
  //M5.dis.fillpix(0x00004f);

  // GPIO39をボタン
  pinMode(BTN_pin, INPUT);
  gpio_wakeup_enable(BTN_pin, GPIO_INTR_LOW_LEVEL);
  esp_sleep_enable_gpio_wakeup();

  IntoSleep();

  //不揮発性メモリに保存された内容を確認
  prefs.begin("wifisetting", false);
  ssid_TH = prefs.getString("ssid_TH" , ""); //登録されていない場合””空文字が入る
  password_TH = prefs.getString("pw_TH" , "");
  prefs.end();

  Serial1.begin(9600, SERIAL_8N1, 22, -1);
  Serial2.begin(1152000, SERIAL_8N1, 26, 32);

  Serial.println("start gps");
  GPS.setTaskName("GPS");
  GPS.setTaskPriority(2);
  GPS.setSerialPtr(Serial1);
  GPS.start();

  //wifi set up
  WiFi.begin((char*)ssid_TH.c_str(), (char*)password_TH.c_str());

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (checkbtn() > 30) { //over 3sec, 3秒以上長押しで終了
      esp_restart();//ESPのリセットにより、Wifiなどをクリアしてスリープに入る
    }
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  Serial.print("Mac:");
  Serial.println(getMacAddress());
  
  
  delay(140);

  Serial.println("start sending video");

}
unsigned long checkbtn() {
  if (digitalRead(BTN_pin) == 0) {
    delay(100);
    if (digitalRead(BTN_pin) == 0) {
      unsigned long  cnt = 0;
      while (0 == digitalRead(BTN_pin)) {//ボタンを話した時に抜ける
        cnt++;
        delay(100);
      }
      Serial.print("cnt:"); Serial.println(cnt);
      return cnt;
    }
  }
  return 0;
}
void loop() {
  // 起動方法取得
  if (checkbtn() > 30) { //over 3sec, 3秒以上長押しで終了
    esp_restart();//ESPのリセットにより、Wifiなどをクリアしてスリープに入る
  }

  GPS.upDate();
  Lat = GPS.s_GNRMC.Latitude;
  Lon = GPS.s_GNRMC.Longitude;
  Utc = GPS.s_GNRMC.Utc;
  Serial.printf("Latitude= %.5f \r\n", Lat);
  Serial.printf("Longitude= %.5f \r\n", Lon);
  Serial.printf("DATA= %s \r\n", Utc);
  delay(1000);
  getvideo();
}

//
// ################## ここからAPサーバーの関数
void onRoot() {
  prefs.begin("wifisetting", false);
  String SSIDPWinpt = "";
  SSIDPWinpt += "<meta http-equiv=\"content-type\"charset=\"utf-8\">";
  SSIDPWinpt += "<html><head><title>Ficy device</title></head>";
  SSIDPWinpt += "<body>";
  SSIDPWinpt += "<form action=\"/set\" method=\"get\">";
  SSIDPWinpt += "<h3>設定したいSSIDを入力してください</h1>";
  SSIDPWinpt += "<p>メールアドレス：<br>";
  SSIDPWinpt += "<input type=\"text\" name=\"mail\" value=\"" + prefs.getString("mail" , "@gmail.com") + "\"></p>";
  SSIDPWinpt += "<p>テザリング SSID：<br>";
  SSIDPWinpt += "<input type=\"text\" name=\"ssid_TH\" value=\"" + prefs.getString("ssid_TH" , "") + "\"></p>";
  SSIDPWinpt += "<p>テザリング パスワード：<br>";
  SSIDPWinpt += "<input type=\"password\" name=\"pw_TH\" value=\"" + prefs.getString("pw_TH" , "") + "\"></p>";
  SSIDPWinpt += "<p>Wifi SSID：<br>";
  SSIDPWinpt += "<input type=\"text\" name=\"wifi_ssid\" value=\"" + prefs.getString("wifi_ssid" , "") + "\"></p>";
  SSIDPWinpt += "<p>パスワード：<br>";
  SSIDPWinpt += "<input type=\"password\" name=\"wifi_pw\" value=\"" + prefs.getString("wifi_pw" , "") + "\"></p>";
  SSIDPWinpt += "<input type=\"submit\" value=\"送信\">";
  SSIDPWinpt += "<input type=\"reset\" value=\"入力内容をリセット\">";
  SSIDPWinpt += "</form>";
  SSIDPWinpt += "</body>";
  SSIDPWinpt += "</html>";

  prefs.end();
  server.send(200, "text/html", SSIDPWinpt);
}

void setdata_SSID_PW() {
  prefs.begin("wifisetting", false);
  for (uint8_t i = 0; i < server.args(); i++) {
    if ((String)"mail" == server.argName(i)) prefs.putString("mail", server.arg(i));
    if ((String)"ssid_TH" == server.argName(i)) prefs.putString("ssid_TH", server.arg(i));
    if ((String)"pw_TH" == server.argName(i)) prefs.putString("pw_TH", server.arg(i));
    if ((String)"wifi_ssid" == server.argName(i)) prefs.putString("wifi_ssid", server.arg(i));
    if ((String)"wifi_pw" == server.argName(i)) prefs.putString("wifi_pw", server.arg(i));
  }
  prefs.end();

  String msg = F("<meta http-equiv=\"content-type\"charset=\"utf-8\"><html><head><title>Ficy device</title></head><body> <script>alert(\'デバイスに登録されました.再起動します\');</script></body></html>");
  server.send(200, "text/html", msg);
  delay(1000);
  esp_restart();
}
