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

# Danh sách từ khóa
keywords = [
    "Data Engineer", "Data Analyst", "Data Scientist", "Machine Learning",
    "Artificial Intelligence", "MLOps", "LLM Engineer", "NLP Engineer",
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps", "Cloud Engineer", "SRE",
    "Platform Engineer", "Security Engineer", "Big Data Engineer"
]

# Cấu hình Selenium
options = Options()
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
# File output
output_path = f"/opt/airflow/data/raw/vietnamworks_jobs_{timestamp}.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
output_file = open(output_path, "w", encoding="utf-8")
output_file.write("[\n")
first_job = True

# Dùng để kiểm tra job trùng
seen_job_links = set()

# Hàm lấy mô tả hoặc yêu cầu
def extract_section(soup, title):
    header = soup.find("h2", string=lambda t: t and title.lower() in t.lower())
    if header:
        content = header.find_next_sibling("div")
        if content:
            return content.get_text(separator="\n", strip=True)
    return "Không có"

# Hàm lấy chi tiết job
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

# Bắt đầu crawl từng keyword
for keyword in keywords:
    encoded_keyword = urllib.parse.quote(keyword)
    page = 1
    print(f"\n🔍 Bắt đầu crawl keyword: {keyword}")

    while True:
        print(f"  👉 Trang {page}")
        url = f"https://www.vietnamworks.com/viec-lam?q={encoded_keyword}&page={page}"
        driver.get(url)

        # Scroll để load thêm job
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
            print("  ✅ Không còn công việc nào.")
            break

        for job in jobs:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "h2 a[href*='-jv']")
                job_link = title_element.get_attribute("href")

                # ❌ Nếu đã gặp link này thì bỏ qua
                if job_link in seen_job_links:
                    print("    ⚠️ Bỏ qua job trùng:", job_link)
                    continue
                seen_job_links.add(job_link)

                title = re.sub(r"^Mới\s*", "", title_element.text.strip())

                try:
                    company_element = job.find_element(By.CSS_SELECTOR, "a[href*='/nha-tuyen-dung/']")
                    company = company_element.text.strip()
                    company_link = company_element.get_attribute("href")
                except:
                    company = "Không rõ"
                    company_link = "Không rõ"


                mo_ta, yeu_cau, salary, location, deadline, orther = extract_job_details(job_link)

                job_info = {
                    "Từ khóa": keyword,
                    "Tiêu đề": title,
                    "Link công việc": job_link,
                    "Công ty": company,
                    "Link công ty": company_link,
                    "Lương": salary,
                    "Địa điểm": location,
                    "Ngày hết hạn": deadline,
                    "Mô tả công việc": mo_ta,
                    "Yêu cầu công việc": yeu_cau,
                    "jd": orther,
                }

                if not first_job:
                    output_file.write(",\n")
                output_file.write(json.dumps(job_info, ensure_ascii=False, indent=2))
                first_job = False

                print(f"    ✅ {title} @ {company}")

            except Exception as e:
                print("    ❌ Lỗi job:", e)
                continue

        page += 1

# Kết thúc
output_file.write("\n]\n")
output_file.close()
driver.quit()

print(f"\n🎉 Crawl hoàn tất. Tổng số job duy nhất: {len(seen_job_links)}")
print(f"Dữ liệu được lưu tại: {output_path}")