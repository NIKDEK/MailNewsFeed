# from flask import Flask // For future update

import requests, time, os, json, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

global last, last_mail

last, last_mail = '', True

with open('Mail_list.json', 'r') as lst:
    maillist = json.loads(lst.read())['emails']
    lst.close()

class news:
    
    news_update = ''

    def read(self):
        with open('fl.txt', 'r') as info:
            fl = info.read()
            info.close()
            self.news_update = fl
    
    def update(self):
        res = requests.get(url='https://www.livio.com/noticias/')
        with open('fl.txt', 'w') as fl:
            fl.write(res.text)
            fl.close()
        self.read()

    #Future update
    def update_list(self, mail):
        maillist['emails'].append(mail)
        with open('Mail_list.json', 'w') as lst:
            lst.write(json.dumps(maillist))
            lst.close()

class mail(news):

    global last_send

    def __init__(self, port, sender, sender_pass, snmp_server="smtp.gmail.com"):
        self.port = port
        self.sender = sender
        self.sender_pass = sender_pass
        self.snmp_server = snmp_server

    def send(self, reciver, last_send, last_mail):
        port = self.port
        smtp_server = self.snmp_server
        sender_email = self.sender        
        receiver_email = reciver
        password = self.sender_pass

        new = self.news_update
        new = new.split('<gcse:search></gcse:search><br>')[1].split('<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div')[0].split('class="txt_inner">')[1]
        nws = new.split('<br><br>')

        message = MIMEMultipart("alternative")
        message["Subject"] = 'Noticias'
        message["From"] = sender_email
        message["To"] = receiver_email
        
        nw = new.split('</span></em><br>')

        LIMIT_NEWS = 6
        
        plain = ''

        for x in range(LIMIT_NEWS):
            if x%2 == 0:
                plain += nw[x].split('</a>: <em><span class="ft_size2">')[0].split('">')[1] + '\n'
            else: 
                plain += f'{nw[x]}\n'

        htm = ''
        
        for x in range(LIMIT_NEWS):
            if x%2 == 0:
                htm += nw[x] 
            else:
                htm += f'<br></span></em>{nw[x]}'
       
        html = f"""
        <html>
            <body>
                {htm}
            </body>
            <br>
            <br>
            <br>
            <footer>
            <a href='/unsub'>Dejar de recibir noticias</a>
            </footer>
        </html>
        """
        msg = MIMEText(plain, "text")   
        msg = MIMEText(html, "html")       
        message.attach(msg) 
        context = ssl.create_default_context()

        if last_send != html and last_mail == True:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print('SENT')
        else:
            print('No Updates')
        return html
        
def send_updates():
    global last, last_mail
    update = mail(465, os.environ['Mail'] , os.environ['Mail_pass'])
    while True:
        update.update()
        lst = ''
        for user in maillist:
            lst =  update.send(user, last, last_mail)
            if user == maillist[len(maillist) - 1]:
               last_mail = False
               last = lst
        last_mail = True
        time.sleep(180)

if __name__ == '__main__':
    send_updates()