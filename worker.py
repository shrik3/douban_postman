from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import dbnew

def my_job():
    print('test on schedule')

def update():
    k = dbnew.Kir(db_name='newpost',user='root',password='',host='localhost')
    db = k.db_connect()
    k.queue(db)

def post_mail():
    k = dbnew.Kir(db_name='newpost',user='root',password='',host='localhost')
    db = k.db_connect()
    k.post(db)

def crawler_test():
    k = dbnew.Kir(db_name='newpost',user='root',password='',host='localhost')
    db = k.db_connect()
    data = k.get_data('波斯语','翻译')
    print(data)

executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(3)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}



scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults)

scheduler.add_job(update, 'cron', minute=23)
scheduler.add_job(post_mail, 'cron', hour=22,minute=10)


try:
    scheduler.start()
except SystemExit:
    client.close()
