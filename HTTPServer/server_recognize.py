from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
import cgi
import urllib
import subprocess
import os.path

def a(string):
    if not hasattr(a,"b"):a.b="adi"
    a.b=a.b+string
    return a.b

def remove(x):
    return x.replace("'", "")


#Create custom HTTPRequestHandler class
class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        #length = int(self.headers.getheader('content-length'))
        #data = cgi.parse_qs(self.rfile.read(int(self.headers['Content-Length'])), keep_blank_values=1)
        
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        data=cgi.parse_multipart(self.rfile, pdict)
	#print(data)

#       self.data_string = self.rfile.read(int(self.headers['Content-Length']))
       
#       body=json.dumps("{'userid':'agangidi','operation':'enroll','result':'success','enrollpercentage':45}")
        data2=data.get('image')
        f=open('reco-name.jpg','wb')
        f.write(str(data2[0]))
        f.close()
#        elif data['operation']=='fr':
        sentence=str(data.get('withinIds')[0])
	new_list=sentence.replace(" ", "")
	print(new_list)
	string2=new_list.split(',')
        size_string2=len(string2)
        print(string2)
        print(size_string2)
        corrected_string_id=''
        cnt=0     #counter to count the number of valid existing DB
        for i in range(size_string2):
            tempstr=string2[i]
            print(tempstr)
            if os.path.isfile(tempstr):
                cnt=cnt+1
                if cnt==1:
                    corrected_string_id=corrected_string_id+tempstr
                else:
                    corrected_string_id=corrected_string_id+','+tempstr
        print(corrected_string_id)
        os.system('date 08/17/2013')
	process = subprocess.Popen(["identify.exe", "-cfg", "frsdk.cfg","-img","reco-name.jpg","-firs",corrected_string_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fr_output = process.communicate()
	os.system('date 09/17/2013')
        print(fr_output[0])           
        try:
	    db_size=len(str.split(corrected_string_id,","))
            print(db_size)
            result_string=str.splitlines(fr_output[0])[db_size+6]      #according to the structure of identity.exe response ... 6 lines down the database list is the output
            print(result_string)
            result_status=result_string[0]
            if result_status=='m':
                status="success"
                confidence=str.split((str.split(result_string,"r[")[1]),"]")[0]
                score=92
            else:
                status="failure"
                confidence="invalid"
                score=0

            pre_body={}
            pre_body['userId']=confidence
            pre_body['code']=status
            pre_body['score']=score
            print(pre_body)
            body=json.dumps(pre_body)                
            self.send_response( 200 )
            self.send_header( "Content-type", "application/json")
            self.send_header( "Content-length", str(len(body)) )
            self.end_headers()
            self.wfile.write(body)
        except:
            pre_body={}
            pre_body['userId']='invalid'
            pre_body['code']='invalid url/list'
            pre_body['score']=0
            print(pre_body)
            body=json.dumps(pre_body) 
            self.send_response( 200 )
            self.send_header( "Content-type", "application/json")
            self.send_header( "Content-length", str(len(body)) )
            self.end_headers()
            self.wfile.write(body)
            
            
	return
    #handle POST command
    
def run():
    print('http server is starting...')

    #ip and port of servr
    #by default http server port is 80
    server_address = ('ec2-54-218-62-190.us-west-2.compute.amazonaws.com', 2000)
    httpd = HTTPServer(server_address, KodeFunHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()
    print(a(''))

