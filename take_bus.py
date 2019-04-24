import json
import math
import requests

line_name = 927
line_id = "092700"
stop_id = 18
direction = 1

url = "http://xxbs.sh.gov.cn:8080/weixinpage/HandlerBus.ashx?action=Three&name={}路&lineid={}&stopid={}&direction={}"

wait_time = 3
max_retry_times = 5
import time

from functools import wraps


def retry_for_errors(errors=Exception, retry_times=max_retry_times,
                     poll_time=wait_time):
    """
    Decorator to retry for multiple errors.

    Example::

        @retry_for_errors(errors=(RuntimeError,NameError))
        def func():
            pass
    """

    assert retry_times > 0, 'retry_times must larger than 0!'

    def wrapper_(func):
        @wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            retry = 1
            while retry <= retry_times:
                try:
                    return func(*args, **kwargs)
                except errors as exc:
                    msg = "Retry for {} for {} time...".format(type(exc).__name__, retry)
                    print(msg)
                    retry += 1

                    if retry > retry_times:
                        raise exc
                    else:
                        time.sleep(poll_time)

        return wrapper

    return wrapper_

@retry_for_errors()
def get_cars_detail(line_name, line_id, stop_id, direction):
    my_url = url.format(line_name, line_id, stop_id, direction)
    get_response = requests.get(my_url)
    if get_response.status_code == 200:

        result = json.loads(get_response.text)

        cars = result["cars"]

        if len(cars) >= 1:
            car_info_list = []
            for i in range(len(cars)):
                terminal = cars[i]["terminal"]
                stopdis = int(cars[i]["stopdis"])
                time = math.ceil(int(cars[i]["time"]) / 60)
                car_info_list.append([terminal, stopdis, time])
            return cars, car_info_list

        else:
            print("no information")


    else:
        print("Didn't kick off, please realex!")


def get_cars_info():
    current_car, car_list = get_cars_detail(line_name, line_id, stop_id, direction)

    car_info = []

    if len(current_car) == 1:

        print("The nearest car is {}, and has {} stop, about {} minutes".format(car_list[0][0],
                                                                                (car_list[0][1]),
                                                                                car_list[0][2]))

        car_info.append([car_list[0][0], car_list[0][1], car_list[0][2]])
        try:
            next_car, next_car_list = get_cars_detail(line_name, line_id, stop_id - car_list[0][1], direction)
            print("The second nearest car is {}, and has {} stop, about {} minutes".format(next_car_list[0][0],
                                                                                           (car_list[0][1] +
                                                                                            next_car_list[0][1]),
                                                                                           (car_list[0][2] +
                                                                                            next_car_list[0][2])))
            car_info.append([next_car_list[0][0], car_list[0][1] + next_car_list[0][1],
                           car_list[0][2] + next_car_list[0][2]])
        except Exception as e:
            print(e)

        return car_info

    else:
        print("More than 1 car are coming, the car are: {}".format(car_list))


if __name__ == "__main__":
    car_info = get_cars_info()

    import tkinter.messagebox

    if len(car_info) == 1:

        tkinter.messagebox.showinfo('重要提醒',
                                    "你等的车，终于来了！the first one {} has {} stops, about {} minutes".format(
                                        car_info[0][0], car_info[0][1], car_info[0][2]))
    else:
        tkinter.messagebox.showinfo('重要提醒',
                                    "你等的车，终于来了！the first one {} has {} stops, about {} minutes; \n The second one {} has {} stops, about {} minutes".format(
                                        car_info[0][0], car_info[0][1], car_info[0][2], car_info[1][0], car_info[1][1], car_info[1][2]))

