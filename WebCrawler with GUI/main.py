import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *
import sys
from PyQt5 import QtWidgets, uic

qtCreatorFile = "web_crawler.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class WebCrawler(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.start_crawling.clicked.connect(self.start)
        self.PROJECT_NAME = ''
        self.HOMEPAGE = ''
        self.DOMAIN_NAME = ''
        self.QUEUE_FILE = ''
        self.CRAWLED_FILE = ''
        self.NUMBER_OF_THREADS = 8
        self.queue = Queue()

    def start(self):
        if self.project_name.text() == "":
            self.output.append("Please enter a project name.")
        elif self.home_page.text() == "":
            self.output.append("Please enter a website that you want to crawl.")
        else:
            self.output.clear()
            self.output.append("Crawling " + str(self.home_page.text()))
            self.output.append("(For more informations check the console.)")
            self.output.append("Please wait...")
            self.repaint()
            self.PROJECT_NAME = self.project_name.text()
            self.HOMEPAGE = self.home_page.text()
            self.DOMAIN_NAME = get_domain_name(self.HOMEPAGE)
            self.QUEUE_FILE = self.PROJECT_NAME + '/queue.txt'
            self.CRAWLED_FILE = self.PROJECT_NAME + '/crawled.txt'
            Spider(self.PROJECT_NAME, self.HOMEPAGE, self.DOMAIN_NAME)
            self.create_spiders()
            self.crawl()
            print('Finished crawling!')
            self.output.append('Finished crawling! To see the file with links please open crawled.txt file located in '
                               + self.PROJECT_NAME + ' folder.')

    # Create worker threads (will die when main exits)
    def create_spiders(self):
        for _ in range(self.NUMBER_OF_THREADS):
            t = threading.Thread(target=self.work)
            t.daemon = True
            t.start()

    # Do the next job in the queue
    def work(self):
        while True:
            url = self.queue.get()
            # self.output.append(threading.current_thread().name + ' now crawling ' + url)
            # self.output.append('Queue: ' + str(len(Spider.queue)) + ' | Crawled: ' + str(len(Spider.crawled)))
            Spider.crawl_page(threading.current_thread().name, url)
            self.queue.task_done()

    # Each queued link is a new job
    def create_jobs(self):
        for link in file_to_set(self.QUEUE_FILE):
            self.queue.put(link)
        self.queue.join()
        self.crawl()

    # Check if there are items in the queue, if so then crawl them
    def crawl(self):
        queued_links = file_to_set(self.QUEUE_FILE)
        if len(queued_links) > 0:
            print(str(len(queued_links)) + ' links in the queue')
            self.create_jobs()


app = QtWidgets.QApplication(sys.argv)
window = WebCrawler()
window.show()
sys.exit(app.exec())
