import paho.mqtt.client as mqtt

host = "mqtt.isc.ac.jp"
port = 1883
user = "isc"
password = "iwasaki3_"

client = mqtt.Client()
client.username_pw_set(user, password)
client.connect(host, port, keepalive=60)

# 1 を on にすると Mabeee が回る
client.publish("iottaiken/mabee", "2,on")
print("送信したよ！")
