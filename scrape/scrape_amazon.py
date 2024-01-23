#import libraries

from bs4 import BeautifulSoup
import requests
import json
from csv import writer
import pandas as pd
import re

def get_currency(soup):
    try:
        currency1 = soup.find("a", attrs= {"id":"icp-touch-link-cop"})
        currency = currency1.find("span", attrs={"class":"icp-color-base"}).text.strip()
        
    except AttributeError: 
        currency = ""
        
    if currency == "":
        currency = soup.find("span", attrs= {"class":"a-price-symbol"}).text.strip().encode("UTF-8")
        if currency == b'\xc2\xa3':
            currency = "GBP"
            
    
    return currency

def get_uk_currency(soup):
    try:
        uk_currency = soup.find("span", attrs= {"id":"tp-tool-tip-subtotal-price-currency-symbol"}).string.strip()
        
    except AttributeError: 
        uk_currency = "N/A"
    
    return uk_currency

def get_title(soup):
    try:
        title = soup.find("span", attrs={"id":"productTitle"}).text.strip()
    except AttributeError: 
        title = "N/A"
    
    return title

def get_selling_price(soup):
    try:
        s_price = soup.find("div", id="corePrice_feature_div")
        s_price = s_price.find("span", attrs={"class":"a-offscreen"}).text.strip()
    except AttributeError:
        s_price = ""
        
    if s_price == "":
        try:
            s_price = soup.find("div", attrs={"id": "exports_desktop_undeliverable_buybox_priceInsideBuybox_feature_div"})
            s_price = s_price.find("span", attrs={"id":"price_inside_buybox"}).text.strip()
        except AttributeError:
            s_price = "N/A"

    return s_price

def get_original_price(soup): 
    try:
        o_price = soup.find("span", attrs={"class":"a-size-base a-color-secondary"})
        o_price = o_price.find("span",attrs={"class":"a-offscreen"}).text.strip()
     
    except AttributeError:
        o_price = "" 
    
    return o_price

def get_discount(soup): 
    try:
        discount = soup.find("span", attrs={"class":"a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"}).string.strip()
        
    except AttributeError:
        discount = ""
        
    return discount

def get_shipping(soup):
    try:
        shipping_fee = soup.find("div", id="amazonGlobal_feature_div")
        
        shipping_fee = shipping_fee.find("span", attrs={"class":"a-size-base a-color-secondary"})
        shipping_fee = ' '.join(shipping_fee.get_text().split())
    except AttributeError:
        shipping_fee = ""
        
    if shipping_fee == "":
        try:
            shipping_fee = soup.find("div", id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE")
            shipping_fee = shipping_fee.find("span", attrs={"class":"a-color-error"})
            shipping_fee = ' '.join(shipping_fee.get_text().split())
        except AttributeError:
            shipping_fee = "N/A"
        
    return shipping_fee

def get_availability(soup):
    try:
        stock = soup.find("div", id='availability')
        stock = stock.find("span").text.strip()
        if len(stock) == 0:
            stock = "N/A"
    except AttributeError:
        stock = "N/A"
    return stock

def get_amazon_identifier(soup): 
    ASIN = ''
    try:
        for ASIN in soup.find_all(attrs={"data-asin":True}):
            return ASIN["data-asin"]
    except AttributeError:
        ASIN = "N/A"
        
    return ASIN 

def get_variation(soup):
    url_li = ['']
    try:
        for url in soup.find_all(attrs={"data-dp-url":True}):
            url_suffix = url["data-dp-url"][4:]
            if url_suffix[0:2] == 'B0':
                url_li.append(url_suffix)
    except Exception:
        pass
    url_li = list(dict.fromkeys(url_li))
    return url_li

def get_links_to_photo_to_album(soup):
     try:
        image = soup.find(id="imgTagWrapperId")
        img_str = image.img.get('data-a-dynamic-image')
        # make dict
        img_dict = json.loads(img_str)
        # first link 
        img_link = list(img_dict.keys())[0]
    
     except AttributeError:
        img_link = ""
        
     return img_link


if __name__ == '__main__':
    # headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", 
    #            "Accept-Encoding":"gzip, deflate", 
    #            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    #            "DNT":"1",
    #            "Connection":"close", 
    #            "Upgrade-Insecure-Requests":"1"}
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "zh-CN,zh-HK;q=0.9,zh-TW;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", 
        "X-Amzn-Trace-Id": "Root=1-64ec4d54-3aaf020b5b80ebc42b02bd9f"
    }
    # source_path = input("plz input the source path: ")
    source_path = r"D:\learning\python_workspace\intern\scrape\amazon_source.csv"
    urls_csv = pd.read_csv(source_path)
    urls = urls_csv.iloc[:, 0].tolist()
    # urls = ["https://www.amazon.co.uk/AmazonBasics-Wireless-Mouse-Receiver-Black/dp/B005EJH6Z4?ref_=ast_sto_dp&th=1&psc=1"]

    title_each_page, currency_each_page, sellingprice_each_page = [], [], []
    originalprice_each_page, discount_each_page, shipping_each_page, availability_each_page =[], [], [], []
    ASIN_each_page, image_each_page = [], []

    for url in urls:
        response_each_page = requests.get(url, headers=headers)
        if  response_each_page.status_code != 200: #change a bit
            print("Status code:", response_each_page)
            raise Exception("Failed to link to web page " + url)

        else:
            print("Status code:", response_each_page)
            print("Successfully retrieving information from", url, ":")
            soup_each_page1 = BeautifulSoup(response_each_page.content, 'html.parser')
            soup_i = BeautifulSoup(soup_each_page1.prettify(),'html.parser')
            
            variation_root_url = url[:re.search("/dp/", url).span()[1]]
            variation_li = get_variation(soup_i)
            if len(variation_li) == 0:
                variation_li.append('')
            for suffix in variation_li:
                if suffix == '':
                    soup_i_variation = soup_i
                else: 
                    url_variation = variation_root_url + suffix
                    response_variation = requests.get(url_variation, headers=headers)
                    temp = BeautifulSoup(response_variation.content, 'html.parser')
                    soup_i_variation = BeautifulSoup(temp.prettify(),'html.parser')
                    
                #title
                title_i = get_title(soup_i_variation)
                title_each_page.append(title_i)
                #currency
                currency_i = get_currency(soup_i_variation)
                currency_each_page.append(currency_i)
                #selling price
                sellingprice_i = get_selling_price(soup_i_variation)
                sellingprice_each_page.append(sellingprice_i)
                #original price
                originalprice_i = get_original_price(soup_i_variation)
                originalprice_each_page.append(originalprice_i)
                #discount
                discount_i = get_discount(soup_i_variation)
                discount_each_page.append(discount_i)
                
                shipping_each_page.append(get_shipping(soup_i_variation))
                
                #availability
                availability_i = get_availability(soup_i_variation)
                availability_each_page.append(availability_i)
                #ASIN
                ASIN_i = get_amazon_identifier(soup_i_variation)
                ASIN_each_page.append(ASIN_i)
                #Image
                Image_i = get_links_to_photo_to_album(soup_i_variation)
                image_each_page.append(Image_i)

    header = ['title', 'currency', 'selling price', 'original price', 'discount', 'shipping fee', 'availability', 'ASIN', 'image']
    # print(title_each_page, currency_each_page, sellingprice_each_page, originalprice_each_page, discount_each_page, shipping_each_page, availability_each_page, ASIN_each_page, image_each_page)
    r = zip(title_each_page, currency_each_page, sellingprice_each_page, originalprice_each_page, discount_each_page, shipping_each_page, availability_each_page, ASIN_each_page, image_each_page)
    with open(r'intern\scrape\amazon_output.csv', 'w', encoding='utf8', newline='') as f:
        w = writer(f)
        w.writerow(header)
        for row in r:
            # print(row)
            # exit()
            if row[6] == 'N/A' and row[2] != 'N/A' and row[5] != 'N/A' and 'cannot' not in row[5]:
                row = list(row)
                row[6] = 'In Stock'
                row = tuple(row)
            w.writerow(row)
        w.writerow('\n')
        