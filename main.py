import json
import os.path

from meta_ai_api import MetaAI
import easyocr
import os
import time
import pandas as pd

def ocr(file_path):
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(file_path)
    res = []
    for (_, text, _) in result:
        res.append(text)
    return " ".join(res)


def meta_llama(response):
    ai = MetaAI()
    result = ai.prompt(message="""
    extract  product purchased, prices and total as json from this text, with this format infering the category field from product name
    e.g
    {products: [{ name: xxx,price: 111, quantity:4,category:Food},{ name: yy,price: 221, quantity:5,category:Food},.......],taxes: 10, total: 342}

    respond only with the extracted json nothing else
    }

    """ + response)
    return result["message"]

def process_files(path):
    res = []
    if os.path.exists(path):
        for file_name in os.listdir(path):
            file_path = os.path.join(path,file_name)
            content = ocr(file_path)
            json_res = meta_llama(content)
            time.sleep(2)
            res.append(json_res)
        return res

def save_to_csv(file_path):
    rows_to_insert = []
    res_lst = process_files(file_path)
    for row in res_lst:
        rows_to_insert.append(json.loads(row))
    df = pd.json_normalize(rows_to_insert,'products',['taxes','total'])
    df["new_total"] = df['price'] * df['quantity']

    df.to_csv("report.csv")
    print("Done")

if __name__ == '__main__':
    save_to_csv("receipts/")