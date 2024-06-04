import time
import requests
import random


class Requester:
    last_request_time = 0
    session = requests.Session()
    request_rate_per_second = 0
    min_sleep_time_sec = 1
    max_sleep_time_sec = 2
    long_sleep_time_sec = 5
    long_sleep_after_requests = 10
    req_counter = 0

    @staticmethod
    def request(rr: requests.Request) -> requests.Response:
        Requester.req_counter += 1
        if Requester.req_counter % Requester.long_sleep_after_requests == 0:
            time.sleep(Requester.long_sleep_time_sec)
        if Requester.request_rate_per_second > 0:
            elapsed = time.time() - Requester.last_request_time
            if elapsed < Requester.request_rate_per_second:
                random_number_sleep = random.randint(
                    Requester.min_sleep_time_sec, Requester.max_sleep_time_sec
                )
                time.sleep(random_number_sleep)
        resp = Requester.session.send(rr.prepare())
        Requester.last_request_time = time.time()
        return resp
