import threading
import subprocess
import re 
import os
import json
import time

MAX_CURLS = 40

pages = "_temp_pages"
ordered = "_temp_ordered"

def run_curl(item):
    name = str(item['leafNum'])
    p = None
    try:
        p = subprocess.Popen(f"""curl -s '{item["uri"]}{get_comm()} --output {pages}/{name}.jpg > /dev/null""", shell=True)
        p.wait(30)
    except subprocess.TimeoutExpired:
        if p:
            p.kill()

def get_comm():
    while True:
        with open("image_curl.txt", "r") as f:
            curl_comm = f.read()
        search = re.search(r"\&scale=", curl_comm)
        with open("token.txt", "r") as f:
            token = f.read()
        if not search:
            print("curl request not in file")
            time.sleep(3)
            continue

        curl_comm = curl_comm[search.span()[0]:]
        tok_search = re.search(r"( loan-[^=]*=)([^';]*)", curl_comm)

        if not tok_search:
            print("tok req not in file")
            time.sleep(3)
            continue

        return curl_comm[:search.span()[0]] + tok_search.group(1) + token + curl_comm[search.span()[1]:]


def getd(dic):
    for d in dic['data']['brOptions']['data']:
        for k in d:
            yield k

awk_rm = "find " + pages + r""" -iname "*.jpg" -exec jpeginfo -c {} \; | grep -E "WARNING|ERROR" | awk '{split($0,a," "); print "rm " a[1] | "sh" }'"""

print("downloading images")
keep = True
while keep:
    keep = False
    subprocess.Popen(awk_rm, shell=True).wait()
    done_names = list(map(lambda x: x[:-4], os.listdir(pages)))
    print(f"{len(done_names)} images downloaded thus far")
    threads = []

    with open("data.json", "r") as data:
        dic = json.load(data)
        for i, item in enumerate(getd(dic)):
            name = str(item['leafNum'])
            if name not in done_names:
                print(f"downloading image {name}")
                keep = True
                threads.append(threading.Thread(target=run_curl, args=[item]))
                threads[-1].start()
                if len(threads) == MAX_CURLS:
                    threads[0].join()
                    threads.pop(0)

    print("waiting")
    for i, t in enumerate(threads):
        t.join()
    subprocess.Popen(awk_rm, shell=True).wait()


a = os.listdir(pages)
nums = list(map(lambda x: int(x[:-4]), a))
nums = sorted(nums)
ognums = nums.copy()
for i in range(1, len(nums) - 1, 2):
    nums[i], nums[i + 1] = nums[i + 1], nums[i]
    
for a, b in zip(ognums, nums):
    os.popen(f"cp {pages}/{a}.jpg {ordered}/{b}.jpg").read()
