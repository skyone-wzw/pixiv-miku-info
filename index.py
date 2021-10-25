import requests
from lxml import html
import json
import os
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/95.0.4638.54 Safari/537.36 "
}

# file range : 0 ~ 1999
start = int(os.getenv("P_START")) - 1
end = int(os.getenv("P_END"))
index = start * 60 + 1
images = None

files = sorted(os.listdir('dataset'))
task = []
fail = []

for i in range(start, end):
    file = files[i]
    with open("dataset/" + file, "r", encoding="utf-8") as f:
        images = json.loads(f.read())
    for image in images:
        image["index"] = index
        image["fail"] = 0
        task.append(image)
        index = index + 1

task.reverse()
while len(task) > 0:
    image = task.pop()
    url = "https://www.pixiv.net/artworks/" + image["id"]
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        selector = html.fromstring(response.text)
        image_info = selector.xpath(r'//*[@id="meta-preload-data"]/@content')[0]
        image_info = json.loads(image_info)
        user_info = image_info["user"][list(image_info["user"].keys())[0]]
        illust_info = image_info["illust"][list(image_info["illust"].keys())[0]]
        json_data = json.dumps({"id": image["index"], "user": user_info, "image": illust_info, "pid": image["id"]},
                               ensure_ascii=False)
        save_path = "output/" + "{:0>6}".format(image["index"]) + "_" + image["id"] + ".json"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(json_data)
        print("[info]\t%d\t%s\t%s" % (image["index"], image["id"], illust_info["title"]))
        time.sleep(1)
    except Exception:
        print("[error]\t%d\t%s\t try again" % (image["index"], image["id"]))
        time.sleep(10)
        image["fail"] += 1
        if image["fail"] <= 5:
            task.insert(0, image)
        else:
            print("[error]\t can't load %d\t%s" % (image["index"], image["id"]))
            fail.append(image)

with open("dataset/fail.json", "w") as f:
    f.write(json.dumps(fail))
