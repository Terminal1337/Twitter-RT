import random
def getProxy():
    proxies = open("input/proxies.txt", "r",encoding='utf-8').read().split("\n")
    return f"http://{random.choice(proxies)}"