import smtplib
from email.mime.text import MIMEText
from email.header import Header

class sender():

    from_addr = 'e@shrik3.com'
    password = 'passwd'
    sender = 'e@shrik3.com'
    receivers = ['86@qq.com']

    def edit_content(self,subject,content):

        self.message = MIMEText(content, 'html', 'utf-8')
        self.message['From'] = "Hao"
        self.message['To'] =  "1"
        self.message['Subject'] = Header(subject, 'utf-8')

    def go(self):
        try:
            server = smtplib.SMTP('smtp.shrik3.com')
            server.set_debuglevel(1)
            server.login(self.from_addr, self.password)
            server.sendmail(self.sender, self.receivers, self.message.as_string())
            print("邮件发送成功")
            return 1
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
            return 0
