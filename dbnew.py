from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import urllib.error
import urllib
import re
import pymysql
import mail

class Kir():

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
               "Cache-Control": "max-age=0",
               "Connection": "keep-alive",
               "Content-Length": "443",
               "Content-Type": "application/x-www-form-urlencoded",
               "Host": "wlsy.xidian.edu.cn",
               "Origin": "http://wlsy.xidian.edu.cn",
               "Referer": "http://wlsy.xidian.edu.cn/phyEws/default.aspx",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"}

    def __init__(self,db_name,user,password,host):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

    def get_page(self, key_word):
        url = "https://www.douban.com/group/search?cat=1013&q="
        url = url + urllib.parse.quote(key_word)+'&sort=time'
        try:
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            page = res.read().decode("utf-8")
            return page
        except urllib.error as e:
            print(e.code)

    def get_data(self, key_word1, key_word2):

        data = []
        html = self.get_page(key_word1)
        soup = BeautifulSoup(html, "html.parser")
        for i in soup.find_all('tr', class_="pl"):
            entry = {}

            subject = i.find_all('td',class_='td-subject')[0]
            ##print(subject.a['title'])
            if not re.findall(key_word2, subject.a['title']):
                continue

            entry['url'] = i.td.a['href']
            entry['title'] = i.td.a['title']
            tdtime = i.find_all('td',class_='td-time')[0]
            entry['time'] = tdtime['title']
            data.append(entry)
        return data

    def db_migrate(self):
        db = self.db_connect()
        cursor = db.cursor()

        check_sql = """
        SELECT table_name FROM information_schema.TABLES WHERE table_name ='queue';
        """

        create_table_sql = """CREATE TABLE queue (
        title  CHAR(100) NOT NULL,
        url  CHAR(100) PRIMARY KEY,
        post_time DATETIME,
        status     int) """

        cursor.execute(check_sql)

        if (cursor.fetchall()):
            print("table exists")
        else:
            cursor.execute(create_table_sql)
            print('table created')

        db.close
        return

    def db_connect(self):
        db = pymysql.connect(host=self.host,user=self.user,passwd=self.password,db=self.db_name ,charset='utf8')
        return db

    def check_entry_existance(self,db,url):
        sql = "SELECT url FROM queue WHERE url = '%s'"%(url)
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return 1
        else:
            return 0

    def new_entry(self,db,url,title,time):
        cursor = db.cursor();
        title =  u''.join(title)

        # insert_sql = "INSERT INTO queue (title,url,post_time,status) VALUES(%s,%s,%s,0)"
        # cursor.execute(insert_sql,(title,url,time))

        insert_stmt = (
            "INSERT INTO queue (title, url, post_time, status) "
            "VALUES (%s, %s, %s , %s )"
        )
        data = (title,url,time,0)
        cursor.execute(insert_stmt, data)
        db.commit()
        print('inserted ')

    def mark_as_pended(self,db):
        update_stmt = (
            "UPDATE queue SET status=1 WHERE status=0 "
        )
        cursor = db.cursor()
        cursor.execute(update_stmt )
        db.commit()

    def queue(self,db):
        data = self.get_data('波斯语','翻译')
        for i in data:
            if not  self.check_entry_existance(db,i['url']):
                ## if i does not exists in the database , then create it
                self.new_entry(db,i['url'],i['title'],i['time'])
            else:
                print('not inserted')
                continue

    def postman(self,db):
        content = self.fetch_unposted_content(db)
        if not content:
            print('nothing new to post')
            return 2
        sender = mail.sender()
        sender.edit_content('豆瓣小组波斯语翻译更新',content)
        if sender.go():
            return 1
        else:
            return 0


    def fetch_unposted_content(self,db):
        sql = "SELECT * FROM queue WHERE status = 0"
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            return 0
        content = "<h1>来自某个昊的摘录机器人</h1>"
        for i in results:
            line = '<a href="'+i[1]+'">' + i[0] + '</a>' +' @ '+str(i[2].date()) + '<br>'
            content += line

        content +="<br><br> 这个邮件总是神tm被当成垃圾邮件拦截掉，所以我在这儿加点文不对题的话，来混淆一下w<br>"
        content += ""
        return content

    def post(self,db):
        print('test from a kir instance')
        if (self.postman(db)==1):
            self.mark_as_pended(db)
