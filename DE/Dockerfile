FROM apache/airflow:2.10.0-python3.10

USER root

# Set Airflow to use LocalExecutor
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Cài đặt Google Chrome và ChromeDriver
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

# Create virtualenv for Qdrant as airflow user
RUN python3 -m venv /opt/airflow/venvs && \
    /opt/airflow/venvs/bin/pip install --upgrade pip && \
    /opt/airflow/venvs/bin/pip install \
    "sqlalchemy>=2.0" \
    qdrant-client \
    googletrans \
    llama-index-embeddings-huggingface \
    llama-index-embeddings-huggingface-api \
    "qdrant-client[fastembed]" \
    fastembed-gpu \
    pandas \
    boto3 \
    llama-index-embeddings-huggingface \
    dotenv

# Copy and install Python requirements (for airflow)
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
