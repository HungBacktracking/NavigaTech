import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import requests
from bs4 import BeautifulSoup
import datetime
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, unquote




# Load environment variables
load_dotenv("/opt/airflow/utils/.env")

# Keywords list
keywords = [
    "Data Engineer", "Data Analyst", "Data Scientist", "Machine Learning",
    "Artificial Intelligence", "MLOps", "LLM Engineer", "NLP Engineer",
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps", "Cloud Engineer", "SRE",
    "Platform Engineer", "Security Engineer", "Big Data Engineer"
]

# Selenium configuration
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

timestamp = datetime.datetime.now().strftime("%Y%m%d")
output_path = f"/opt/airflow/data/raw/vietnamworks_jobs_{timestamp}.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
output_file = open(output_path, "w", encoding="utf-8")
output_file.write("[\n")
first_job = True
seen_job_links = set()

def extract_section(soup, title):
    header = soup.find("h2", string=lambda t: t and title.lower() in t.lower())
    if header:
        content = header.find_next_sibling("div")
        if content:
            return content.get_text(separator="\n", strip=True)
    return "Không có"

def extract_job_details(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(link, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return "Không có", "Không có", "Không rõ", "Không rõ", "Không rõ", "Không có"

    soup = BeautifulSoup(response.text, "html.parser")
    mo_ta = extract_section(soup, "Mô tả công việc")
    yeu_cau = extract_section(soup, "Yêu cầu công việc")
    benefit = extract_section(soup, "Quyền lợi")
    salary = location = deadline = orther = "Không rõ"

    try:
        container = soup.select_one("div.vnwLayout__container")
        if container:
            level = container
            for _ in range(7):
                level = level.find("div")
            level8 = level.find_all("div")
            level9 = level8[0].find_all("div")
            salary_span = level9[3].find("span") if len(level9) > 3 else None
            salary = salary_span.text.strip() if salary_span else "Không rõ"

        mo_ta_header = soup.find("h2", string=lambda t: t and "mô tả công việc" in t.lower())
        if mo_ta_header:
            mo_ta_parent = mo_ta_header.find_parent("div")
            top_level_div = mo_ta_parent.find_parent("div") if mo_ta_parent else None
            if top_level_div:
                sibling_divs = top_level_div.find_all("div", recursive=False)
                orther = "\n\n".join(div.get_text(separator="\n", strip=True) for div in sibling_divs)
    except Exception as e:
        print("Lỗi trong quá trình xử lý:", e)

    spans = soup.find_all("span")
    for i, span in enumerate(spans):
        if "Hết hạn" in span.text:
            deadline = span.text.strip()
        if "lượt xem" in span.text and i + 1 < len(spans):
            location = spans[i + 1].text.strip()
            break

    return mo_ta, yeu_cau, salary, location, deadline, orther

# Start crawling
for keyword in keywords:
    encoded_keyword = urllib.parse.quote(keyword)
    page = 1
    print(f"\n🔍 Crawling keyword: {keyword}")

    while True:
        print(f"  Page {page}")
        url = f"https://www.vietnamworks.com/viec-lam?q={encoded_keyword}&page={page}"
        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        jobs = driver.find_elements(By.CSS_SELECTOR, "div.search_list.view_job_item")
        if not jobs:
            print("  No more jobs.")
            break

        for job in jobs:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "h2 a[href*='-jv']")
                job_link = title_element.get_attribute("href")

                if job_link in seen_job_links:
                    print("    Skipping duplicate job:", job_link)
                    continue
                seen_job_links.add(job_link)

                title = re.sub(r"^Mới\s*", "", title_element.text.strip())

                try:
                    company_element = job.find_element(By.CSS_SELECTOR, "a[href*='/nha-tuyen-dung/']")
                    company = company_element.text.strip()
                    company_link = company_element.get_attribute("href")
                    try:
                        img_element = job.find_element(By.CSS_SELECTOR, "img")
                        srcset = img_element.get_attribute("srcset")
                        if srcset:
                            last_url = srcset.split(',')[-1].strip().split(' ')[0]
                            parsed_url = urlparse(last_url)
                            query = parse_qs(parsed_url.query)
                            company_logo_link = unquote(query['url'][0]) if 'url' in query else last_url
                        else:
                            company_logo_link = img_element.get_attribute("src")
                    except:
                        company_logo_link = "Không rõ"
                except:
                    company = "Không rõ"
                    company_link = "Không rõ"

                mo_ta, yeu_cau, salary, location, deadline, orther = extract_job_details(job_link)

                # job_info = {
                #     "Từ khóa": keyword,
                #     "Tiêu đề": title,
                #     "Link công việc": job_link,
                #     "Công ty": company,
                #     "Link công ty": company_link,
                #     "Lương": salary,
                #     "Địa điểm": location,
                #     "Ngày hết hạn": deadline,
                #     "Mô tả công việc": mo_ta,
                #     "Yêu cầu công việc": yeu_cau,
                #     "jd": orther,
                #     "Logo công ty": company_logo_link,
                # }


                job_info = {
                    "keyword": keyword,
                    "title": title,
                    "job_url": job_link,
                    "company": company,
                    "company_url": company_link,
                    "salary": salary,
                    "location": location,
                    "expiration_date": deadline,
                    "responsibilities": mo_ta,
                    "qualifications & skills": yeu_cau,
                    "jd": orther,
                    "company_logo": company_logo_link,
                }


                if not first_job:
                    output_file.write(",\n")
                output_file.write(json.dumps(job_info, ensure_ascii=False, indent=2))
                first_job = False

                print(f"    ✅ {title} @ {company}")

            except Exception as e:
                print("Job error:", e)
                continue

        page += 1

output_file.write("\n]\n")
output_file.close()
driver.quit()

print(f"\nCrawl completed. Total unique jobs: {len(seen_job_links)}")
print(f"Data saved at: {output_path}")

# --- S3 UPLOAD LOGIC ---
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    bucket_name = os.getenv("AWS_S3_BUCKET")
    s3_key = f"raw/vietnamworks_jobs_{timestamp}.json"

    print(f"Uploading {output_path} to s3://{bucket_name}/{s3_key}...")
    s3.upload_file(output_path, bucket_name, s3_key)
    print(f"Upload completed: s3://{bucket_name}/{s3_key}")

except ClientError as e:
    print(f"Failed to upload to S3: {e}")
