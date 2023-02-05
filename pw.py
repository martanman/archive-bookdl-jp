import asyncio
import json
import os
import subprocess
import re
from playwright.async_api import Cookie, async_playwright
from playwright.async_api import expect
from playwright.async_api import Request, Frame
from typing import List, Tuple
import sys

import config  # config.py file in directory

async def handle_token_and_json(request: Request):
    if "format=jsonp" in request.url or "services/loans/loan" in request.url:
        resp = await request.response()
        if resp:
            try:
                jsn = await resp.json()
                if "services/loans/loan" in request.url and jsn['success'] == True and 'token' in jsn:
                    print(f"got token: {jsn['token']}")
                    with open("token.txt", "w") as f:
                        f.write(jsn['token'])
                elif "format=jsonp" in request.url:
                    with open("data.json", "w") as f:
                        json.dump(jsn, f)

            except Exception as e:
                print("exception:", e)

made_curl = False

def remove_temps():
    os.popen("rm image_curl.txt token.txt data.json").read()

def make_curl(url: str, headers: List[Tuple[str, str]], file_path: str):
    with open(file_path, "w") as f:
        f.write(f"""curl '{url}' \\\n""")
        for n, v in headers:
            f.write(f"  -H '{n}: {v}' \\\n")
        f.write("  --compressed")


async def handle_image_req(request: Request):
    if "scale=1" in request.url:
        headers = await request.headers_array()
        hdrs = list(map(lambda h: (h["name"], h["value"]), filter(
            lambda h: not h["name"][0].startswith(":"), headers)))
        global made_curl
        if made_curl:
            return
        make_curl(request.url, hdrs, "image_curl.txt")
        made_curl = True

async def handle_frame(frame: Frame):
    print("changed to frame: ", frame.url)

def get_auth_cookies():
    try:
        with open("auth_cookies.txt", "r") as f:
            return json.load(f)
    except Exception:
        return None


async def main(title_name: string, page_url: string, eng=False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        page.on("framenavigated", handle_frame)

        # add auth cookies before navigating
        auth_cookies = get_auth_cookies()
        if auth_cookies:
            print("Adding saved auth cookies")
            await context.add_cookies(auth_cookies)
        else:
            print("Logging in")
            await page.goto("https://archive.org/account/login")

            # sign in
            print("Filling auth details")
            await page.get_by_label("Email address").fill(config.email)
            await page.get_by_label("Password").fill(config.passwd)
            async with page.expect_navigation():
                await page.get_by_role("button", name="Log in").click()

            # save auth cookies
            print("Saving auth cookies")
            with open("auth_cookies.txt", "w") as f:
                json.dump(await context.cookies(), f) 

        print("Going to the book's page")
        await page.goto(page_url)
        print(f"page title: {await page.title()}")

        # borrow
        print("borrowing")
        locator = page.get_by_role("button", name=re.compile("Borrow for .*"))
        await locator.click()

        # token and book data will soon be requested
        page.on("request", handle_token_and_json)

        # wait for return button to be visible (good indicator that it's loaded)
        return_button = page.get_by_role(
            "button", name=re.compile("Return now"))
        await expect(return_button).to_be_visible(timeout=10000)

        try:
            page.on("request", handle_image_req)
            # focus BookReader to zoom
            await page.focus("#BookReader > div.BRcontainer")
            for _ in range(6):
                await page.keyboard.press("=", delay=1)

            print("waiting for curl request to be created")
            while not made_curl:
                await asyncio.sleep(1)
                print(".")

            print("calling fetch.sh")
            fetchp = subprocess.Popen(f"sh fetch.sh {title_name} {int(eng)}", shell=True)

            i = 0
            while True:
                await asyncio.sleep(1)
                if fetchp.poll() != None:
                    break
                if i % 160 == 0:
                    await page.keyboard.press("ArrowRight")
                i += 1

        except Exception as e:
            print(e)

        finally:
            print("Returning book")
            await return_button.click()
            locator = page.get_by_role(
                "button", name=re.compile("Borrow for .*"))
            await expect(return_button).to_be_visible(timeout=15000)

            print("Closing browser")
            await context.close()
            await browser.close()

            remove_temps()

if __name__ == "__main__":
    kwargs = {}
    if "--eng" in sys.argv:
        sys.argv.remove("--eng")
        kwargs["eng"] = True
    assert len(sys.argv) == 3
    asyncio.run(main(sys.argv[-2], sys.argv[-1], **kwargs))
