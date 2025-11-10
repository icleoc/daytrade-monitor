==> Cloning from https://github.com/icleoc/daytrade-monitor
==> Checking out commit 08ec31507f3567a9f3b946c54ba4ff17b3f31129 in branch main
==> Installing Python version 3.13.4...
==> Using Python version 3.13.4 (default)
==> Docs on specifying a Python version: https://render.com/docs/python-version
==> Using Poetry version 2.1.3 (default)
==> Docs on specifying a Poetry version: https://render.com/docs/poetry-version
==> Running build command 'pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir'...
Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.1.1)
Collecting pip
  Downloading pip-25.3-py3-none-any.whl.metadata (4.7 kB)
Downloading pip-25.3-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 4.1 MB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 25.1.1
    Uninstalling pip-25.1.1:
      Successfully uninstalled pip-25.1.1
Successfully installed pip-25.3
Collecting flask==2.3.3 (from -r requirements.txt (line 1))
  Downloading flask-2.3.3-py3-none-any.whl.metadata (3.6 kB)
Collecting pandas==2.3.3 (from -r requirements.txt (line 2))
  Downloading pandas-2.3.3-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (91 kB)
Collecting numpy==2.3.4 (from -r requirements.txt (line 3))
  Downloading numpy-2.3.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (62 kB)
Collecting requests==2.32.5 (from -r requirements.txt (line 4))
  Downloading requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
Collecting python-binance==1.0.15 (from -r requirements.txt (line 5))
  Downloading python_binance-1.0.15-py2.py3-none-any.whl.metadata (11 kB)
Collecting Werkzeug>=2.3.7 (from flask==2.3.3->-r requirements.txt (line 1))
  Downloading werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
Collecting Jinja2>=3.1.2 (from flask==2.3.3->-r requirements.txt (line 1))
  Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting itsdangerous>=2.1.2 (from flask==2.3.3->-r requirements.txt (line 1))
  Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
Collecting click>=8.1.3 (from flask==2.3.3->-r requirements.txt (line 1))
  Downloading click-8.3.0-py3-none-any.whl.metadata (2.6 kB)
Collecting blinker>=1.6.2 (from flask==2.3.3->-r requirements.txt (line 1))
  Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting python-dateutil>=2.8.2 (from pandas==2.3.3->-r requirements.txt (line 2))
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting pytz>=2020.1 (from pandas==2.3.3->-r requirements.txt (line 2))
  Downloading pytz-2025.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting tzdata>=2022.7 (from pandas==2.3.3->-r requirements.txt (line 2))
  Downloading tzdata-2025.2-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting charset_normalizer<4,>=2 (from requests==2.32.5->-r requirements.txt (line 4))
  Downloading charset_normalizer-3.4.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (37 kB)
Collecting idna<4,>=2.5 (from requests==2.32.5->-r requirements.txt (line 4))
  Downloading idna-3.11-py3-none-any.whl.metadata (8.4 kB)
Collecting urllib3<3,>=1.21.1 (from requests==2.32.5->-r requirements.txt (line 4))
  Downloading urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests==2.32.5->-r requirements.txt (line 4))
  Downloading certifi-2025.10.5-py3-none-any.whl.metadata (2.5 kB)
Collecting six (from python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting dateparser (from python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading dateparser-1.2.2-py3-none-any.whl.metadata (29 kB)
Collecting aiohttp (from python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading aiohttp-3.13.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (8.1 kB)
Collecting ujson (from python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading ujson-5.11.0-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (9.4 kB)
Collecting websockets==9.1 (from python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading websockets-9.1.tar.gz (76 kB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->flask==2.3.3->-r requirements.txt (line 1))
  Downloading markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Collecting aiohappyeyeballs>=2.5.0 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading aiohappyeyeballs-2.6.1-py3-none-any.whl.metadata (5.9 kB)
Collecting aiosignal>=1.4.0 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
Collecting attrs>=17.3.0 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading attrs-25.4.0-py3-none-any.whl.metadata (10 kB)
Collecting frozenlist>=1.1.1 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading frozenlist-1.8.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (20 kB)
Collecting multidict<7.0,>=4.5 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading multidict-6.7.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (5.3 kB)
Collecting propcache>=0.2.0 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading propcache-0.4.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (13 kB)
Collecting yarl<2.0,>=1.17.0 (from aiohttp->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading yarl-1.22.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (75 kB)
Collecting regex>=2024.9.11 (from dateparser->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading regex-2025.11.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
Collecting tzlocal>=0.2 (from dateparser->python-binance==1.0.15->-r requirements.txt (line 5))
  Downloading tzlocal-5.3.1-py3-none-any.whl.metadata (7.6 kB)
Downloading flask-2.3.3-py3-none-any.whl (96 kB)
Downloading pandas-2.3.3-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (12.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.3/12.3 MB 40.1 MB/s  0:00:00
Downloading numpy-2.3.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (16.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.6/16.6 MB 142.8 MB/s  0:00:00
Downloading requests-2.32.5-py3-none-any.whl (64 kB)
Downloading python_binance-1.0.15-py2.py3-none-any.whl (63 kB)
Downloading charset_normalizer-3.4.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (153 kB)
Downloading idna-3.11-py3-none-any.whl (71 kB)
Downloading urllib3-2.5.0-py3-none-any.whl (129 kB)
Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
Downloading certifi-2025.10.5-py3-none-any.whl (163 kB)
Downloading click-8.3.0-py3-none-any.whl (107 kB)
Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
Downloading markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Downloading pytz-2025.2-py2.py3-none-any.whl (509 kB)
Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading tzdata-2025.2-py2.py3-none-any.whl (347 kB)
Downloading werkzeug-3.1.3-py3-none-any.whl (224 kB)
Downloading aiohttp-3.13.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 224.2 MB/s  0:00:00
Downloading multidict-6.7.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (254 kB)
Downloading yarl-1.22.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (377 kB)
Downloading aiohappyeyeballs-2.6.1-py3-none-any.whl (15 kB)
Downloading aiosignal-1.4.0-py3-none-any.whl (7.5 kB)
Downloading attrs-25.4.0-py3-none-any.whl (67 kB)
Downloading frozenlist-1.8.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (234 kB)
Downloading propcache-0.4.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (204 kB)
Downloading dateparser-1.2.2-py3-none-any.whl (315 kB)
Downloading regex-2025.11.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (803 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 803.5/803.5 kB 315.3 MB/s  0:00:00
Downloading tzlocal-5.3.1-py3-none-any.whl (18 kB)
Downloading ujson-5.11.0-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (57 kB)
Building wheels for collected packages: websockets
  Building wheel for websockets (pyproject.toml): started
  Building wheel for websockets (pyproject.toml): finished with status 'done'
  Created wheel for websockets: filename=websockets-9.1-cp313-cp313-linux_x86_64.whl size=97398 sha256=baf51a1df26ac9f924e571bab4e064e6433071465eefda96c335b14ed7047eaf
  Stored in directory: /tmp/pip-ephem-wheel-cache-qudgmm2m/wheels/37/cb/9d/607c67d85b0d0cc1e8d1e19235b6e6538eed8d250b7ea45dcc
Successfully built websockets
Installing collected packages: pytz, websockets, urllib3, ujson, tzlocal, tzdata, six, regex, propcache, numpy, multidict, MarkupSafe, itsdangerous, idna, frozenlist, click, charset_normalizer, certifi, blinker, attrs, aiohappyeyeballs, yarl, Werkzeug, requests, python-dateutil, Jinja2, aiosignal, pandas, flask, dateparser, aiohttp, python-binance
Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.3 aiohappyeyeballs-2.6.1 aiohttp-3.13.2 aiosignal-1.4.0 attrs-25.4.0 blinker-1.9.0 certifi-2025.10.5 charset_normalizer-3.4.4 click-8.3.0 dateparser-1.2.2 flask-2.3.3 frozenlist-1.8.0 idna-3.11 itsdangerous-2.2.0 multidict-6.7.0 numpy-2.3.4 pandas-2.3.3 propcache-0.4.1 python-binance-1.0.15 python-dateutil-2.9.0.post0 pytz-2025.2 regex-2025.11.3 requests-2.32.5 six-1.17.0 tzdata-2025.2 tzlocal-5.3.1 ujson-5.11.0 urllib3-2.5.0 websockets-9.1 yarl-1.22.0
==> Uploading build...
==> Uploaded in 10.9s. Compression took 6.0s
==> Build successful 🎉
==> Deploying...
==> Running 'python app.py'
Traceback (most recent call last):
  File "/opt/render/project/src/app.py", line 16, in <module>
    binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 300, in __init__
    self.ping()
    ~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 526, in ping
    return self._get('ping', version=self.PRIVATE_API_VERSION)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 371, in _get
    return self._request_api('get', path, signed, version, **kwargs)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 334, in _request_api
    return self._request(method, uri, signed, **kwargs)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 315, in _request
    return self._handle_response(self.response)
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 324, in _handle_response
    raise BinanceAPIException(response, response.status_code, response.text)
binance.exceptions.BinanceAPIException: APIError(code=0): Service unavailable from a restricted location according to 'b. Eligibility' in https://www.binance.com/en/terms. Please contact customer service if you believe you received this message in error.
==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
==> Running 'python app.py'
Traceback (most recent call last):
  File "/opt/render/project/src/app.py", line 16, in <module>
    binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 300, in __init__
    self.ping()
    ~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 526, in ping
    return self._get('ping', version=self.PRIVATE_API_VERSION)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 371, in _get
    return self._request_api('get', path, signed, version, **kwargs)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 334, in _request_api
    return self._request(method, uri, signed, **kwargs)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 315, in _request
    return self._handle_response(self.response)
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/binance/client.py", line 324, in _handle_response
    raise BinanceAPIException(response, response.status_code, response.text)
binance.exceptions.BinanceAPIException: APIError(code=0): Service unavailable from a restricted location according to 'b. Eligibility' in https://www.binance.com/en/terms. Please contact customer service if you believe you received this message in error.
