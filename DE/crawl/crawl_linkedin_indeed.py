
import csv
import os
import datetime
import logging
import time
import pandas as pd
from jobspy import scrape_jobs
import random
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
    ]
    return random.choice(agents)


def extract_company_info(url: str) -> dict:
    # time.sleep(random.uniform(2, 5))  # Delay ngẫu nhiên để tránh bị phát hiện

    response = requests.get(url, timeout=10, headers={
        "User-Agent": random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
    })
    soup = BeautifulSoup(response.text, 'html.parser')

    def extract_text_by_test_id(test_id):
        tag = soup.find('div', {'data-test-id': test_id})
        return tag.find('dd').get_text(strip=True) if tag and tag.find('dd') else ""

    # Mô tả công ty
    description_tag = soup.find('p', attrs={'data-test-id': 'about-us__description'})
    description = description_tag.get_text(strip=True) if description_tag else ""

    # Website
    website_tag = soup.find('div', {'data-test-id': 'about-us__website'})
    website = ""
    if website_tag:
        a_tag = website_tag.find('a', href=True)
        website = a_tag['href'] if a_tag else ""

    info = {
        'description': description,
        'headquarters': extract_text_by_test_id('about-us__headquarters'),
        'website': website,
    }

    return info



# Create directories for logs and output
log_dir = "logs"
output_dir = "output"
for directory in [log_dir, output_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Configure timestamp for logs and output
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"{log_dir}/jobspy_scraper_{timestamp}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("JobSpy Scraper")

# Define search keywords (same as in your original crawler)
keywords = [
    "Data Engineer", "Data Analyst", "Data Scientist", "Machine Learning",
    "Artificial Intelligence", "MLOps", "LLM Engineer", "NLP Engineer",
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps", "Cloud Engineer", "SRE",
    "Platform Engineer", "Security Engineer", "Big Data Engineer"
]

# Record start time
start_time = datetime.datetime.now()
logger.info(f"Starting JobSpy scraper at {start_time}")
logger.info(f"Will search for {len(keywords)} keywords: {', '.join(keywords)}")

# Initialize empty DataFrame to store all results
all_jobs = pd.DataFrame()

# Specify Vietnam as the country for Indeed
country = "Vietnam"

# To avoid rate limiting, use a delay between queries
delay_between_queries = 5  # seconds

# Loop through each keyword and scrape jobs
for index, keyword in enumerate(keywords):
    logger.info(f"Processing keyword {index+1}/{len(keywords)}: '{keyword}'")
    
    try:
        # Scrape jobs from LinkedIn and Indeed (adjust based on your needs)
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=keyword,
            location="Vietnam",
            country_indeed=country,  # Important for Indeed searches
            results_wanted=500,       # Number of jobs per keyword
            # hours_old=72,            # Jobs posted in the last 3 days
            linkedin_fetch_description=True,  # Get full descriptions
            # description_format="markdown",
            # Uncomment if you have proxies
            # proxies=["proxy1:port", "proxy2:port"],
            verbose=2  # Full logging
        )
        
        # Add search keyword as a column
        if not jobs.empty:
            jobs["search_keyword"] = keyword
            
            # Log example job to see structure
            if len(jobs) > 0 and index == 0:
                logger.info(f"Example job structure: {jobs.iloc[0].to_dict()}")
                logger.info(f"Available columns: {jobs.columns.tolist()}")
            
            # Append to the combined DataFrame
            all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
            
            logger.info(f"Found {len(jobs)} jobs for '{keyword}'. Total jobs so far: {len(all_jobs)}")
        else:
            logger.warning(f"No jobs found for keyword '{keyword}'")
            
        # Add delay to avoid rate limiting
        if index < len(keywords) - 1:  # Don't delay after the last query
            logger.info(f"Waiting {delay_between_queries} seconds before next query...")
            time.sleep(delay_between_queries)
            
    except Exception as e:
        logger.error(f"Error scraping jobs for '{keyword}': {str(e)}")
        logger.error("Consider using proxies if rate limited")







if not all_jobs.empty:
    if 'job_url' in all_jobs.columns:
        original_count = len(all_jobs)
        all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')
        logger.info(f"Removed {original_count - len(all_jobs)} duplicate job listings based on job_url")
    else:
        logger.warning(f"'job_url' column not found. Available columns: {all_jobs.columns.tolist()}")

        url_columns = [col for col in all_jobs.columns if 'url' in col.lower()]
        if url_columns:
            url_column = url_columns[0]
            logger.info(f"Using column '{url_column}' for duplicate removal")

            original_count = len(all_jobs)
            all_jobs = all_jobs.drop_duplicates(subset=[url_column], keep='first')
            logger.info(f"Removed {original_count - len(all_jobs)} duplicate job listings")

    # === Giãn cách request khi scrape LinkedIn company ===
    for idx, row in tqdm(all_jobs.iterrows(), total=all_jobs.shape[0], desc="Enriching LinkedIn company info"):
        if str(row.get("site", "")).lower() == "linkedin":
            company_url = row.get("company_url", "")
            if company_url:
                try:
                    info = extract_company_info(company_url)
                    all_jobs.at[idx, "company_description"] = info.get("description", "")
                    all_jobs.at[idx, "company_addresses"] = info.get("headquarters", "")
                    all_jobs.at[idx, "company_url_direct"] = info.get("website", "")

                    # Delay ngẫu nhiên từ 2 đến 5 giây giữa các request
                    time.sleep(random.uniform(3, 10))

                except Exception as e:
                    logger.warning(f"Failed to extract info from {company_url}: {e}")








# Calculate duration
end_time = datetime.datetime.now()
duration = end_time - start_time

# Generate output filenames with timestamp
csv_output = f"{output_dir}/vietnam_jobs_{timestamp}.csv"
excel_output = f"{output_dir}/vietnam_jobs_{timestamp}.xlsx"
json_output = f"{output_dir}/vietnam_jobs_{timestamp}.json"






# Save results to CSV, Excel, and JSON (if there are any jobs)
if not all_jobs.empty:
    # Save to CSV with proper escaping
    all_jobs.to_csv(csv_output, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    # Save to Excel
    # all_jobs.to_excel(excel_output, index=False)
    
    # # Save to JSON
    # # Convert DataFrame to list of dictionaries for JSON export
    # jobs_json = all_jobs.to_dict(orient='records')
    # import json
    # with open(json_output, 'w', encoding='utf-8') as f:
    #     json.dump(jobs_json, f, ensure_ascii=False, indent=2, default=str)


    import json
    import pandas as pd
    import numpy as np

    # Replace all NaN/NaT with None before converting to dict
    clean_df = all_jobs.replace({np.nan: None, pd.NaT: None})

    # If still unsure, apply map to force it (optional fallback):
    jobs_json = clean_df.to_dict(orient='records')

    # Save to JSON with datetime handling
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(jobs_json, f, ensure_ascii=False, indent=2, default=str)



    
    logger.info(f"Saved {len(all_jobs)} jobs to:")
    logger.info(f"  - CSV: {csv_output}")
    logger.info(f"  - Excel: {excel_output}")
    logger.info(f"  - JSON: {json_output}")
    
    # Analyze the results
    # Count jobs by site
    if 'site' in all_jobs.columns:
        site_counts = all_jobs['site'].value_counts()
        logger.info(f"Jobs by site:\n{site_counts}")
    
    # Count companies
    company_col = 'company' if 'company' in all_jobs.columns else 'COMPANY' 
    if company_col in all_jobs.columns:
        company_counts = all_jobs[company_col].value_counts().head(10)
        logger.info(f"Top 10 companies:\n{company_counts}")
    
    # Log stats by keyword
    keyword_counts = all_jobs['search_keyword'].value_counts()
    logger.info(f"Jobs by keyword:\n{keyword_counts}")
    
    # Check for remote jobs
    remote_col = 'is_remote' if 'is_remote' in all_jobs.columns else None
    if remote_col and remote_col in all_jobs.columns:
        remote_jobs = all_jobs[all_jobs[remote_col] == True].shape[0]
        logger.info(f"Remote jobs: {remote_jobs} ({remote_jobs/len(all_jobs)*100:.1f}%)")
else:
    logger.warning("No jobs were found across all keywords")

# Print final summary
logger.info("\n===== SCRAPING COMPLETED =====")
logger.info(f"Total jobs found: {len(all_jobs)}")
logger.info(f"Duration: {duration}")
logger.info(f"Output files:")
logger.info(f"  - CSV: {csv_output}")
logger.info(f"  - Excel: {excel_output}")
logger.info(f"Log file: {log_file}")
logger.info("=============================")

# print(f"\n⏱️ Total duration: {duration}")
# print(f"📊 Total jobs: {len(all_jobs)}")
# print(f"📁 CSV file: {csv_output}")
# print(f"📁 Excel file: {excel_output}")
# print(f"📁 JSON file: {json_output}")
# print(f"📁 Log file: {log_file}")


