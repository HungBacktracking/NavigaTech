FROM apache/airflow:2.7.3-python3.10

COPY requirements.txt /opt/airflow/

USER root

# Cài đặt Google Chrome và ChromeDriver với cách phân phối mới từ Google
RUN apt-get update && \
    apt-get install -y wget unzip curl gnupg && \
    curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Installed Google Chrome version: $CHROME_VERSION" && \
    wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/chromedriver && \
    mv /tmp/chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

USER airflow
# Install Python dependencies from the requirements.txt
COPY wheels/ /wheels/
COPY requirements.txt /requirements.txt
RUN pip install --find-links=/wheels -r /requirements.txt



