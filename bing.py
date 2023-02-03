import translators as ts
from typing import List, Union
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import requests
from bs4 import BeautifulSoup
from random import randint
import pandas as pd
from datetime import datetime
import os
import time

scrape = FastAPI(title="bing.com", debug=False)

seq = randint(1000000, 9999999)

# Add CORS middleware to enable cross-origin requests
scrape.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Handle HTTPException
@scrape.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """:class:`HTTPException` error handler."""
    ecode_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        406: "NOT_ACCEPTABLE",
        409: "CONFLICT",
        500: "INTERNAL_SERVER_ERROR"
    }
    content = {
        "error_type": ecode_mapping.get(exc.status_code, "UNKNOWN_ERROR"),
        "message": exc.detail
    }
    return JSONResponse(content, exc.status_code, exc.headers)


@scrape.get('/bing search')
async def bing_search(input: List[str] = Query(...),
                      dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    headers_url = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://www.bing.com/',
    }

    title = []
    url = []
    dic = []

    for input_list in input:
        time.sleep(0.50)

        url_bing = f"https://www.bing.com/search?q={input_list}&qs=HS&pq={input_list}&sc=10-8&cvid=B69DCD8{seq}45DDA0286DBD1867F&FORM=QBRE&sp=1"

        try:
            with requests.Session() as s:
                response = s.get(url_bing, timeout=50, headers=headers_url)
        except requests.exceptions.RequestException as e:
            print(e)

        soup = BeautifulSoup(response.content, 'lxml')
        html = soup.findAll("li", class_="b_algo")

        for data in html:
            title.append(data.find("h2").text)

            url.append(data.find("h2").find("a").get("href"))
            try:
                dic.append(str(data.find("p").text).replace("Web", ""))
            except AttributeError:
                dic.append("None")

    if dataframe == True:
        df = pd.DataFrame({"title": title, "url": url,
                          "dic": dic})

        curr_datetime = datetime.now().strftime('%Y-%m-%d%H-%M-%S')
        splitted_path = os.path.splitext('file/example.xlsx')
        modified_xlsx_path = splitted_path[0] + \
            curr_datetime + splitted_path[1]
        df.to_excel(modified_xlsx_path, index=False)

        headers = {
            'Content-Disposition': f'attachment; filename="{modified_xlsx_path}.xlsx"'}
        return FileResponse(modified_xlsx_path, headers=headers)
        # return ("http://127.0.0.1:8080/" + modified_xlsx_path)

    else:
        return {
            "title": title,
            "url": url,
            "dic": dic,
        }


@scrape.get('/bing suggestions')
async def bing_suggestions(query: str, dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    headers_url = {
        'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.4240.183',
        'referer': 'https://www.bing.com/',
    }

    all_results = []

    expanded_terms = _get_expanded_terms(query)
    for term in expanded_terms:
        time.sleep(0.50)

        url = f"https://www.bing.com/AS/Suggestions?pt=page.home&mkt=fa-ir&qry={term}&cp=1&msbqf=false&cvid=B69DCD8{seq}45DDA0286DBD1867F"
        try:
            with requests.Session() as s:
                response = s.get(url, timeout=50, headers=headers_url)
        except:
            print("none")

        BS_Parser = BeautifulSoup(response.text, 'lxml')

        items = BS_Parser.find_all('span', attrs={'class', 'sa_tm_text'})

        for result in items:
            all_results.append(result.text.strip())

    if dataframe == True:
        df = pd.DataFrame({"suggestions": all_results})

        curr_datetime = datetime.now().strftime('%Y-%m-%d%H-%M-%S')
        splitted_path = os.path.splitext('file/example.xlsx')
        modified_xlsx_path = splitted_path[0] + \
            curr_datetime + splitted_path[1]
        df.to_excel(modified_xlsx_path, index=False)

        headers = {
            'Content-Disposition': f'attachment; filename="{modified_xlsx_path}.xlsx"'}
        return FileResponse(modified_xlsx_path, headers=headers)
        # return ("http://127.0.0.1:8080/" + modified_xlsx_path)

    else:
        return {
            "suggestions": all_results,
        }


def _get_expanded_terms(query: str):

    expanded_term_prefixes = ['چیست', 'نحوه', 'چگونه', 'بهترین', 'قیمت',
                              'ارزان', 'آموزش', 'کدام', 'چرا', 'روش', 'خرید']

    expanded_term_suffixes = ['آ', 'ا', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
                              'ژ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و', 'ه', 'ی']

    terms = [query]

    for term in expanded_term_prefixes:
        terms.append(term + ' ' + query)

    for term in expanded_term_suffixes:
        terms.append(query + ' ' + term)

    return terms


@scrape.get('/Related searches keyword')
async def related_searches(input: List[str] = Query(...),
                           dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    headers_url = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://www.bing.com/',
    }

    suggestionText = []

    for input_list in input:
        time.sleep(0.50)

        url_bing = f"https://www.bing.com/search?q={input_list}&qs=HS&pq={input_list}&sc=10-8&cvid=B69DCD8{seq}45DDA0286DBD1867F&FORM=QBRE&sp=1"

        try:
            with requests.Session() as s:
                response = s.get(url_bing, timeout=50, headers=headers_url)
        except requests.exceptions.RequestException as e:
            print(e)

        soup = BeautifulSoup(response.content, 'lxml')
        html = soup.findAll("div", class_="b_suggestionText")

        for data in html:
            suggestionText.append(data.text)

    if dataframe == True:
        df = pd.DataFrame({"suggestionText": suggestionText})

        curr_datetime = datetime.now().strftime('%Y-%m-%d%H-%M-%S')
        splitted_path = os.path.splitext('file/example.xlsx')
        modified_xlsx_path = splitted_path[0] + \
            curr_datetime + splitted_path[1]
        df.to_excel(modified_xlsx_path, index=False)

        headers = {
            'Content-Disposition': f'attachment; filename="{modified_xlsx_path}.xlsx"'}
        return FileResponse(modified_xlsx_path, headers=headers)
        # return ("http://127.0.0.1:8080/" + modified_xlsx_path)

    else:
        return {
            "suggestionText": suggestionText,
        }


@scrape.get('/translator suggestions')
async def tsuggestions(input: str = Query(...), from_language: str = Query(default="fa")):

    headers_url = {
        'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.4240.183',
        'referer': 'https://www.bing.com/',
    }

    url = f"https://www.bing.com/tsuggestions?text={input}&lang={from_language}"

    try:
        with requests.Session() as s:
            response = s.get(url, timeout=50, headers=headers_url)

        return BeautifulSoup(response.text, 'lxml').find("span").text

    except:

        return "none"


@scrape.get('/translators')
async def translators(input: str = Query(...), from_language: str = Query(default="fa"), to_language: str = Query(default='en')):

    return ts.translate_text(input, from_language=from_language, to_language=to_language, translator='bing',
                             if_ignore_empty_query=False, if_ignore_limit_of_length=False)
