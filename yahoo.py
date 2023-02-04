import requests
from bs4 import BeautifulSoup
from typing import List
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from datetime import datetime
import os
import time
from random import randint

scrape = FastAPI(title="yahoo.com", debug=False)
seq = randint(1000000, 9999999)
_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'referer': 'https://search.yahoo.com/',
    'cache-control': 'no-cache'
}

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


@scrape.get('/yahoo search')
async def yahoo_search(input: List[str] = Query(...),
                       dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    title = []
    url = []
    dic = []

    for input_list in input:
        time.sleep(0.50)

        url_bing = f"https://search.yahoo.com/search;_ylt=AwrNZ2RvmN1jAg{seq}oA;_ylc=X1MDMjc2NjY3OQRfcgMyBGZyAwRmcjI{seq}tc2VhcmNoBGdwcmlkA1BCSVRfcURqVGh5a2ZKbWE5SHEzYUEEbl9yc2x0AzAEbl9zdWdnAzEwBG9yaWdpbgNzZWFyY2gueWFob28uY29tBHBvcwMxBHBxc3RyAyVEOCVCMSVEOSU4OCVEOCVCMiUyMCVEOSU4NSVEOCVBNyVEOCVBRiVEOCVCMQRwcXN0cmwDOARxc3RybAM4BHF1ZXJ5AyVEOCVCMSVEOSU4OCVEOCVCMiUyMCVEOSU4NSVEOCVBNyVEOCVBRiVEOCVCMQR0X3N0bXADMTY3NTQ2Njk3OQR1c2VfY2FzZQM-?p={input_list}&fr2=sa-gp-search"

        try:
            with requests.Session() as s:
                response = s.get(url_bing, timeout=50, headers=_headers)
        except requests.exceptions.RequestException as e:
            print(e)

        soup = BeautifulSoup(response.content, 'lxml')
        html = soup.find("ol", class_="reg searchCenterMiddle")

        for data in html:
            try:
                title.append(data.find("h3", "title").find(
                    "span").next_sibling.text)
            except:
                title.append(None)
            try:
                url.append(data.find("h3", "title").find("a").get("href"))
            except:
                url.append(None)
            try:
                dic.append(data.find("span", "fc-falcon").text)
            except:
                dic.append(data.find("span", "fc-falcon"))

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


@scrape.get('/yahoo suggestions')
async def yahoo_suggestions(query: str, dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    all_results = []

    expanded_terms = _get_expanded_terms(query)

    for term in expanded_terms:
        time.sleep(0.25)

        url = f"https://search.yahoo.com/sugg/gossip/gossip-us-fastbreak/?l=1&bm=3&output=sd1&appid=syc&bck=1ol0a11hi1gm6%26b%3D4%26d%3DKtZxC8VtYFn40yYywy.O%26s%3Dg7%26i%3DBVugFqBc3uP0BUoKISs4&mtestid=30356%3DLOCUI036BRMP%2625824%3DTGPC2203%2629944%3DADTESTSC%26304{seq}&pq={term}&command={term}&t_stmp=1675464894&nresults=20&ll=53.682361%2C32.42065&geoid=23424851&csrcpvid=aZHF9DEwLjIcVAoIYyDCxgIqOTMuMQAAAACRSZyA&spaceId=119{seq}"

        try:
            with requests.Session() as s:
                response = s.get(url, timeout=50, headers=_headers).json()
        except:
            print("none")

        [all_results.append(data["k"]) for data in response["r"]]

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