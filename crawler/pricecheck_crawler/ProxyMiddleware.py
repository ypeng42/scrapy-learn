import random

class ProxyRotator(object):
    proxy_pool = ['208.113.93.66',
                   '208.113.93.67',
                   '208.113.93.68',
                   '208.113.93.69',
                   '208.113.93.70',
                   '208.113.93.71',
                   '208.113.93.72',
                   '208.113.93.73',
                   '208.113.93.74',
                   '208.113.93.75',
                   '208.113.93.76',
                   '216.93.164.26',
                   '216.93.164.28'
                   ]

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://" + self.proxy_pool[random.randint(0, len(self.proxy_pool) - 1)] + ":80"
        #self.logger.warning('proxy %s', request.meta['proxy'])