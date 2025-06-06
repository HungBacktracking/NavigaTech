# Scrapy settings for coursera project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "coursera"

SPIDER_MODULES = ["coursera.spiders"]
NEWSPIDER_MODULE = "coursera.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 4

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
    # 'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
   # "coursera.middlewares.CourseraSpiderMiddleware": 543,
# }

# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy_splash.SplashCookiesMiddleware': 723,
    # 'scrapy_splash.SplashMiddleware': 725,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'coursera.middlewares.RateLimitDetectionMiddleware': 300,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',
    'scrapy_fake_useragent.providers.FakerProvider',
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',
]
FAKEUSERAGENT_FALLBACK = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "coursera.pipelines.GeminiNormalizationPipeline": 300,
    # "coursera.pipelines.CourseraPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 36000
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 522, 524, 404, 408, 429]
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# SPLASH_URLS = [
#     "http://localhost:8050",
#     "http://localhost:8051",
#     "http://localhost:8052",
#     "http://localhost:8053",
# ]
# SPLASH_URL = "http://localhost:8050"

# SPLASH_SLOT_POLICY = scrapy_splash.SlotPolicy.PER_DOMAIN

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"


RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]


ROTATING_PROXY_LIST = [
    '159.69.57.20:8880',
    '141.94.196.80:8989',
    '62.133.60.126:24558',
    '45.140.143.77:18080',
    '200.174.198.86:8888'
]

ROTATING_PROXY_BAN_CODES = [
    500, 502, 503, 504, 522, 524, 408, 429, 403
]

FEEDS = {
    # key: đường dẫn/tên file hoặc URI (có thể kèm protocol như file://, s3://, v.v.)
    # value: cấu hình detalied cho từng output
    "coursera.json": {
        "format": "json",         # định dạng (csv, json, jsonlines, xml, v.v.)
        "encoding": "utf-8",      # (tuỳ chọn) mã hoá
        "store_empty": True,     # (tuỳ chọn) có lưu file nếu không có item nào không
        "indent": 4,              # (tuỳ chọn) số khoảng trắng để xuống dòng (chỉ áp dụng với JSON)
        "fields": None,           # (tuỳ chọn) chỉ xuất các field nào, giữ nguyên thứ tự, hoặc None để xuất tất cả theo item definition
        "overwrite": True,        # (tuỳ chọn) nếu file đã tồn tại, có ghi đè không
    },
}
