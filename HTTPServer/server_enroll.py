from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
import cgi
import urllib
import subprocess
import boto
import sys, os
from boto.s3.key import Key
LOCAL_PATH = ''
AWS_ACCESS_KEY_ID = 'AKIAIEWWLRP3B22DEE4Q' 
AWS_SECRET_ACCESS_KEY = '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'
bucket_name = 'spaycevault'
# connect to the bucket
conn = boto.connect_s3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket(bucket_name)




#Create custom HTTPRequestHandler class
class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        data= cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        urllist=str(data['images'][0])
	urllist_sp=urllist.split(',')
	
	list_no=[]
	for c in range(len(urllist_sp)):
		temp_str=str(c)
		print(urllist_sp[c])
		keyString=bucket.get_key(urllist_sp[c])
		keyString.get_contents_to_filename(temp_str+".jpg")
		#urllib.urlretrieve(urllist_sp[c],temp_str+".jpg")
		if (c==(len(urllist_sp)-1)):
                    list_no.append(str(c)+'.jpg')
                else:
                    list_no.append(str(c)+'.jpg,')
		

	print(list_no)
	list_str = ''.join(list_no)
	print(list_str)
	print(str(data['userId'][0]))
	os.system('date 08/16/2013')
        process = subprocess.Popen(["enroll.exe", "-cfg", "frsdk.cfg","-fir",str(data['userId'][0]),"-imgs",list_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        new_output = process.communicate()
        os.system('date 09/16/2013')
        print(new_output)
#            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
       
            
        try:
                
            result_status=str.splitlines(new_output[0])[4+(3*len(urllist_sp))][0]
            
            if result_status=='s':
                status="success"
                confidence=83
                    
            else:
                status="failure"
                confidence=0
       
                #data3=json.JSONEncoder().encode(data2)
            pre_body={}
            pre_body['userId']=str(data['userId'][0])
            pre_body['result']=status
            pre_body['score']=confidence
            body=json.dumps(pre_body)
            print(body)
            self.send_response( 200 )
            self.send_header( "Content-type", "application/json")
            self.send_header( "Content-length", str(len(body)) )
            self.end_headers()
            self.wfile.write(body)
        except:
            pre_body={}
            pre_body['userId']=str(data['userId'][0])
            pre_body['result']='invalid image/id'
            pre_body['score']=0    
            body=json.dumps(pre_body)
            self.send_response( 200 )
            self.send_header( "Content-type", "application/json")
            self.send_header( "Content-length", str(len(body)) )
            self.end_headers()
            self.wfile.write(body)
#        else:
#            body='{"operation":"invalid"}'
#            self.send_response( 200 )
#            self.send_header( "Content-type", "application/json")
#            self.send_header( "Content-length", str(len(body)) )
#            self.end_headers()
#            self.wfile.write(body)
            
	return


def run():
    print('http server is starting...')
    #ip and port of servr
    #by default http server port is 1000
    server_address = ('ec2-54-218-62-190.us-west-2.compute.amazonaws.com', 1000)
    httpd = HTTPServer(server_address, KodeFunHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()
    print(a(''))

