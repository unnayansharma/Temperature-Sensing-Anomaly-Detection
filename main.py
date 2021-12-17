""" TWILIO CONFIGURATION """
SSID = 'AC051c1cc8f7deb24b151477e9ef73f77e' 
AUTH_TOKEN = 'b7b78e5fbccb219d8ac65f2c7fc962fe' 
FROM_NUMBER='+12512501646'
TO_NUMBER = '+91**********'
  
""" MAILGUN CONFIGURATION """
MAILGUN_API_KEY = '190f96b46676f5fccc3bff592ec42151-73ae490d-989437cc'
SANDBOX_URL = 'sandboxadb67c45bc0d43d483c056b5a1f2034c.mailgun.org'
SENDER_MAIL = 'test@sandboxadb67c45bc0d43d483c056b5a1f2034c.mailgun.org'
RECIPIENT_MAIL = '*******@gmail.com  
""" BOLT IOT CONFIGURATION """
API_KEY = '*****************************'
DEVICE_ID = 'BOLT6097300'
FRAME_SIZE = 10
MUL_FACTOR = 6 


import json,time,math,statistics,conf,requests  
from boltiot import Bolt,Sms,Email         
def compute_bounds(history_data,frame_size,factor):  
   if len(history_data)<frame_size :        
       return None      
   if len(history_data)>frame_size :       
       del history_data[0:len(history_data)-frame_size]  
   Mn=statistics.mean(history_data)  
   Variance=0   
   for data in history_data:   
       Variance += math.pow((data-Mn),2)  
   Zn=0  
   Zn = factor*math.sqrt(history_data[frame_size-1])+Zn      
   Low_bound = history_data[frame_size-1]-Zn  
   High_bound = history_data[frame_size-1]+Zn  
   return [High_bound,Low_bound]   
mybolt = Bolt(API_KEY, DEVICE_ID)  
sms = Sms(SSID, AUTH_TOKEN, TO_NUMBER, FROM_NUMBER)  
mailer = Email(MAILGUN_API_KEY, SANDBOX_URL,SENDER_MAIL,RECIPIENT_MAIL)  
history_data=[]  
while True:      
   response = mybolt.analogRead('A0')  
   data = json.loads(response)    
   if data['success'] != 1:       
       print("There was an error while retriving the data.")     
       print("This is the error:"+data['value'])         
       time.sleep(5)     
       continue    
   sensor_value= int(data['value'])     
   sensor_valuec = sensor_value/10.24      
   print ("The current sensor value is : "+str(sensor_valuec))  
   sensor_value=0    
   try:        
       sensor_value = int(data['value'])   
   except e:   
       print("There was an error while parsing the response: ",e)      
       continue    
   bound = compute_bounds(history_data,FRAME_SIZE,MUL_FACTOR)   
   if not bound:      
       required_data_count=FRAME_SIZE-len(history_data)     
       print("Not enough data to compute Z-score. Need ",required_data_count," more data points")       
       history_data.append(int(data['value']))      
       time.sleep(5)       
       continue  
   try:     
       if sensor_value > bound[0] :  
           buzz=mybolt.digitalWrite('1',"HIGH")  
           print(buzz)  
           print("Anomaly of the temperature occured because of increase in temperature sending an alert messages")   
           """ SMS """  
           print ("The temperature level increased suddenly. Sending an SMS")     
           response = sms.send_sms("The temperature has raised to:"+str(sensor_valuec)+"degree celcius")            
           print("This is the response ",response)     
           """ MAIL """  
           print("Making request to Mailgun to send an email")       
           response = mailer.send_email("Alert","The Current temperature sensor value is " +str(sensor_valuec))       
           response_text = json.loads(response.text)        
           print("Response received from Mailgun is:"+str(response_text['message']))             
           print(message.sid)  
       elif sensor_value < bound[1]:  
            buzz=mybolt.digitalWrite('1',"HIGH")  
            print(buzz)  
            print("Anomaly of the temperature occured because of increase in temperature sending an alert messages")   
            """ SMS """  
            print ("The temperature level decreased suddenly. Sending an SMS")      
            response = sms.send_sms("The temperature has decreased to : "+str(sensor_valuec)+"degree celcius")            
            print("This is the response ",response)      
            """ MAIL """  
            print("Making request to Mailgun to send an email")       
            response = mailer.send_email("Alert","The Current temperature sensor value is " +str(sensor_valuec))            
            response_text = json.loads(response.text)             
            print("Response received from Mailgun is:"+str(response_text['message']))         
       history_data.append(sensor_value);     
   except Exception as e:        
       print ("Error",e)    
   time.sleep(5)

