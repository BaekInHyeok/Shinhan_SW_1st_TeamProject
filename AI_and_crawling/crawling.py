from bs4 import BeautifulSoup
import requests
import urllib.request as download
import os
import json
from selenium import webdriver


highest_categories_eachAll = {"여성":"https://www.ssfshop.com/WOMEN/list?dspCtgryNo=SFMA41",
                              "남성":"https://www.ssfshop.com/MEN/list?dspCtgryNo=SFMA42",
                              "키즈":"https://www.ssfshop.com/KIDS/list?dspCtgryNo=SFMA43",
                              "럭셔리":"https://www.ssfshop.com/LXRY/list?dspCtgryNo=SFME34",
                              "백&슈즈":"https://www.ssfshop.com/BAG-SHOES/list?dspCtgryNo=SFMA46",
                              "스포츠":"https://www.ssfshop.com/SPORTS/list?dspCtgryNo=SFME37"}

with open("C:/Users/jh981/Desktop/category.json") as f:
    category = json.load(f)

with open("C:/Users/jh981/Desktop/ctg_url_matching.json") as f:
    ctg_url_matching = json.load(f)

with open("C:/Users/jh981/Desktop/done.json") as f:
    done = json.load(f)

with open("C:/Users/jh981/Desktop/products_list.json") as f:
    products_list = json.load(f)

with open("C:/Users/jh981/Desktop/businessMans.json") as f:
    businessMans = json.load(f)

my_directory = "C:/Users/jh981/Desktop/products"
ssf_url_base = "https://www.ssfshop.com"
base_bm_num = "199-81-21898"

driver_options = webdriver.ChromeOptions()
driver_options.add_argument("headless")
driver_options.add_argument("--log-level=3")
driver_options.add_argument("--disable-loging")
driver = webdriver.Chrome(options=driver_options)
driver.implicitly_wait(30)

def page_control_by_dfs(depth :int, url :str, mode :str):
    if depth == 0:
        ctgs, _ = get_sub_categories(url)

        for sub_url in ctgs.values():
            page_control_by_dfs(depth+1, sub_url, mode)
    else :
        ctgs, is_lowest = get_sub_categories(url)
        if is_lowest:
            if mode == "json" :
                cur_category = get_categories(url)
                if cur_category in done["done"] : return
                # for n in range(1, get_paging_area(url)+1) :
                #     download_products_json_before_detail(driver, url + f"&currentPage={n}", makeJson, businessMans)
                download_products_json_before_detail(driver, url + f"&currentPage={1}", products_list, businessMans)
                
                done["done"].append(cur_category)
                done["page"]=0
                with open('C:/Users/jh981/Desktop/done.json', 'w') as f:
                    json.dump(done, f, indent=4, ensure_ascii=False)
            return

        for sub_url in ctgs.values():
            page_control_by_dfs(depth, sub_url, mode)

def get_sub_categories(url :str) -> dict :
    is_lowest = False

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    sub_categories = dict([(ctg.text.strip(), ssf_url_base+ctg.find("a").attrs["href"]) for ctg in list(soup.find("div", {"class":"sub-category"}).find_all("li"))])
    categories_now = [sub_directory.text.strip() for sub_directory in soup.find("div", {"class":"breadcrumb"}).find("ol").find_all("li")][1:]
    
    cur = category
    for sub_category in categories_now:
        cur = cur[sub_category]

    if len(cur) == 1: is_lowest = True

    for sub_category in sub_categories.copy().keys():
        if sub_category not in cur.keys():
            sub_categories.pop(sub_category)
    
    return sub_categories, is_lowest

# def get_file_directory(url :str, my_directory :str) -> str:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     categories_now = [sub_directory.text.strip() for sub_directory in soup.find("div", {"class":"breadcrumb"}).find("ol").find_all("li")][1:]
    
#     cur = category
#     rest = ""
#     for sub_category in categories_now:
#         rest += "/" + cur[sub_category]["en"]
#         cur = cur[sub_category]
    
#     print(my_directory + rest)

def get_categories(url :str) -> str :
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    categories_now = [sub_directory.text.strip() for sub_directory in soup.find("div", {"class":"breadcrumb"}).find("ol").find_all("li")][1:]
    
    cur = category
    ctg = ""
    for sub_category in categories_now:
        ctg += "_" + cur[sub_category]["en"]
        cur = cur[sub_category]
    ctg = ctg[1:]
    
    return ctg

def get_paging_area(url :str) -> int :
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    pages = len(list(soup.find("div", {"id":"pagingArea"}).find_all("a")))-4

    return pages

def get_product_detail_urls(url :str) -> list :
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    detail_urls = []
    prods = soup.find("ul", {"id":"dspGood"}).find_all("li")

    for prod in prods:
        prod = prod.find("a").attrs["href"]
        prod = prod[prod.index("(")+1:prod.rindex(")")].replace(" ","").replace("'","")
        brndNm, godNm, dpos, _, _ = prod.split(",")
        utag = url[url.find("=")+1:]
        detail_urls.append(ssf_url_base + f"/{brndNm}/{godNm}/good?dspCtgryNo={utag}/&brandShopNo=&brndShopId=&keyword=&leftBrandNM=&utag=ref_cat:{utag}$dpos:{dpos}")

    return detail_urls

def download_products_json_before_detail(driver :webdriver.Chrome, url :str, makeJson :dict, businessMans :dict) -> None:
    cur_ctg = get_categories(url)

    for i, detail_url in enumerate(get_product_detail_urls(url)) :
        if int(url[url.rfind('=')+1:]) <= done["page"] : continue

        driver.get(detail_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        gods_price = soup.find("span", {"class":"gods-price"})
        cost = gods_price.find("span", {"class":"cost"})
        if cost == None :
            price = gods_price.find("span", {"class":"sale"}).find("em", {"class":"price"}).text.strip().replace(",","")
        else :
            price = cost.find("del").text.strip().replace(",","")

        img_name = soup.find("div", {"id":"goodDtlTitle"}).get_text().strip().replace("_", "-").replace("/", "-")
        brand_name = soup.find("h2", {"class":"brand-name"}).find("a")
        if brand_name == None : brand_name = soup.find("h2", {"class":"brand-name"}).text.strip()
        else : brand_name = brand_name.text.strip()

        if brand_name not in businessMans.keys():
            businessMans[brand_name] = "199-81-"+str(int(base_bm_num.split("-")[2])+len(businessMans))
        
        makeJson[f"{img_name}_{businessMans[brand_name]}"] = {}
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["img_name"] = img_name
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["brand_name"] = brand_name
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["bm_num"] = businessMans[brand_name]
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["category"] = ctg_url_matching[cur_ctg]
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["category_name"] = cur_ctg
        makeJson[f"{img_name}_{businessMans[brand_name]}"]["price"] = price

        print(f"진행도 : 현재 {cur_ctg} 카테고리 {url[url.rfind('=')+1:]}page {i+1}번째 상품 완료.")

    done["page"] = int(url[url.rfind('=')+1:])

    with open('C:/Users/jh981/Desktop/done.json', 'w') as f:
        json.dump(done, f, indent=4, ensure_ascii=False)

    with open('C:/Users/jh981/Desktop/products_list.json', 'w') as f:
        json.dump(products_list, f, indent=4, ensure_ascii=False)
    with open('C:/Users/jh981/Desktop/business_mans.json', 'w') as f:
        json.dump(businessMans, f, indent=4, ensure_ascii=False)

def download_products_images_before_detail(driver :webdriver.Chrome, url :str) -> None:

    for detail_url in get_product_detail_urls(url) :
        driver.get(detail_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        img_name = soup.find("div", {"id":"goodDtlTitle"}).get_text().strip().replace("_", "-").replace("/", "-")
        
        image_urls = [img.attrs["src"] for img in soup.find("div", {"id":"godImgWrap"}).find_all("img")]
        
        gods_detail_desc_img_urls = [img.attrs["src"] if "src" in img.attrs.keys() else img.attrs["data-original"] for img in soup.find("div", {"class":"gods-detail-img"}).find_all("img")]
        gods_detail_desc_jsp = '<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>' + str(soup.find("div", {"class", "gods-detail-desc"}))

        print(image_urls)
        print(gods_detail_desc_img_urls)
        print(gods_detail_desc_jsp)

        driver.quit()

# download.urlretrieve(li[1].find("img").attrs["src"], f"C:/Users/jh981/Downloads/{img_name}_199-81-21898_image_1.jpg")

if __name__ == "__main__" :
    for highest_url in highest_categories_eachAll.values():
        page_control_by_dfs(depth=0, url=highest_url, mode="json")
    driver.quit()
    # download_products_images_before_detail("https://www.ssfshop.com/Coats/list?dspCtgryNo=SFMA41A07A02A01")
    # download_products_json_before_detail("https://www.ssfshop.com/Coats/list?dspCtgryNo=SFMA41A07A02A01", {})
    # get_categories("https://www.ssfshop.com/Coats/list?dspCtgryNo=SFMA41A07A02A01")

    # print(get_paging_area("https://www.ssfshop.com/Coats/list?dspCtgryNo=SFMA41A07A02A01"))
