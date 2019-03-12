import getopt
import sys

from crawler import Worker, Crawler

GET_PAGE_KEY = 'get_page_key'
workers = 5

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'w:')
    for o, a in opts:
        if o in ('-w', '--workers'):
            workers = int(a)

    print(workers)


    def callback(html):
        print(html)


    for i in range(workers):
        workers = Worker(GET_PAGE_KEY, callback)
        workers.ready()

    crawler = Crawler(GET_PAGE_KEY)

    urls = [
        f'http://mirfactov.com/page/{i}/'
        for i in range(1, 4)
    ]

    crawler.get(urls)
