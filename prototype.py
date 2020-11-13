#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

broker     = "insert mqtt server"
port       = 1883
username   = "insert username"
password   = "insert password"
endpoint   = "insert endpoint"
mqttclient = "python1"

def on_log(client, userdata, level, buf):
    print(buf)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Connected")
    else:
        print("Connection error: ", rc)
        client.loop.stop()

def on_disconnect(client, userdata, rc):
    print("Disonnected")

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed")

def on_message(client, userdata, message):
    topic = message.topic
    msgr = str(message.payload.decode("utf-8"))
    msgr = "Message received " + msgr
    print(msgr)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def reset():
    ret = client.publish(endpoint, "", 0, True)

mqtt.Client.connected_flag = False

client               = mqtt.Client(mqttclient)
client.on_log        = on_log
client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_publish    = on_publish
client.on_subscribe  = on_subscribe
client.on_message    = on_message

client.username_pw_set(username,password)
client.connect(broker, port)
client.loop_start()

while not client.connected_flag:
    print("Waiting loop")
    time.sleep(1)

time.sleep(0.5)
print("Publishing")

i = 0;
while 1 < 100:
    i = i + 1
    
    try:
        GPIO.setmode(GPIO.BOARD)
        
        PIN_TRIGGER = 7
        PIN_ECHO    = 11
        
        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO,    GPIO.IN )
        
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        print("Waiting for sensor to settle")
        
        time.sleep(0.5)
        
        print("Calculating distance")
        
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        
        time.sleep(0.00001)
        
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time   = time.time()
        
        pulse_duration = pulse_end_time - pulse_start_time
        distance       = round(pulse_duration * 17150, 2)
        
        print("Distance:", distance, "cm")
        
        if distance > 12 and distance < 100:
            print("Object detected")            
            ret = client.publish(endpoint, '{"distance":distance}', 0)
            
            print("Publish return = ", ret)
            time.sleep(0.5)
        
    
    finally:
        GPIO.cleanup()
    

reset()
client.loop_stop()
client.disconnect()