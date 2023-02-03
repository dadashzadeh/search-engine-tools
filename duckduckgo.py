import duckduckgo_search
from typing import List
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from datetime import datetime
import os
import time

scrape = FastAPI(title="duckduckgo.com", debug=False)

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


@scrape.get('/duckduckgo search')
async def duckduckgo(input: List[str] = Query(...),
                     dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    title = []
    body = []
    href = []

    for inputs in input:
        time.sleep(0.50)
        results = duckduckgo_search.ddg(
            inputs, region='wt-wt', safesearch='Moderate')
        for d in results:
            title.append(d["title"])
            body.append(d["body"])
            href.append(d["href"])

    if dataframe == True:
        df = pd.DataFrame({"title": title, "url": href,
                          "dic": body})

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
            "url": href,
            "dic": body,
        }


@scrape.get('/duckduckgo suggestions')
async def duckduckgo_suggestions(query: str, dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    all_results = []

    expanded_terms = _get_expanded_terms(query)
    for term in expanded_terms:
        time.sleep(0.25)
        results = duckduckgo_search.ddg_suggestions(term, region='wt-wt')
        for result in results:
            all_results.append(result["phrase"].strip())

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


@scrape.get('/translator')
async def duckduckgo_translators(input: str = Query(...), from_language: str = Query(default='fa'), to_language: str = Query(default='en')):

    results = duckduckgo_search.ddg_translate(
        input, from_=from_language, to=to_language)

    return results[0]


@scrape.get('/duckduckgo images')
async def duckduckgo_images(input: str = Query(...),
                            dataframe: bool = Query(..., description="<h4 style='text-align:right;'>خروجی به صورت فایل باشد؟</h4>")):

    results = duckduckgo_search.ddg_images(input, region='wt-wt')

    title = []
    image = []
    url = []

    for d in results:
        title.append(d["title"])
        image.append(d["image"])
        url.append(d["url"])

    if dataframe == True:
        df = pd.DataFrame({"title": title, "image": image,
                          "url": url})

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
            "image": image,
            "url": url,
        }
