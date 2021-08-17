#
# cache test by moriya@runserver.jp
#
from pathlib import Path
import datetime
import responder

wd = Path(__file__).parent
api = responder.API(templates_dir=wd/'templates')

# ヘッダに何も指定しない
#
# ie11 ではキャッシュされない
#
# chrome(92.0.4515.131) ではキャッシュされない
#
# => 特に指定がない場合の動作
#
@api.route("/cache_nospec/")
async def normal(req, resp):
    now = datetime.datetime.now()
    resp.html = api.template('cache_nospec.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# Cache-Control ヘッダ: max-age=60
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => max-age を指定した場合の動作
#    ie11 はアドレスバーで URL を入力した場合は、リンククリックと同様
#
#    chrome はアドレスバーで URL を入力した場合は、リロードと同様
#    https://stackoverflow.com/questions/11245767/is-chrome-ignoring-cache-control-max-age
#    https://blog.chromium.org/2017/01/reload-reloaded-faster-and-leaner-page_26.html
#    などか
#
@api.route("/cache_control1/")
async def cache_control1(req, resp):
    now = datetime.datetime.now()
    resp.headers['Cache-Control'] = 'max-age=60'
    resp.html = api.template('cache_control1.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# Cache-Control ヘッダ max-age=60
# ドキュメントの http-equiv Cache-Control の値 no-store
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => Cache-Control は http-equiv では指定できない？
#
@api.route("/cache_control1a/")
async def cache_control1a(req, resp):
    now = datetime.datetime.now()
    resp.headers['Cache-Control'] = 'max-age=60'
    # <meta http-equiv="Cache-Control" content="no-store">
    resp.html = api.template('cache_control1a.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# Cache-Control ヘッダ: max-age=60
# ドキュメントの http-equiv Expires の値: Thu, 01 Dec 1994 16:00:00 GMT
#
# ie11
# リンククリック/アドレスバー: 再リクエストされる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => ie11 では、http-equiv expires は有効
#    chrome は http-equiv expires を無視？
#
@api.route("/cache_control2/")
async def cache_control2(req, resp):
    now = datetime.datetime.now()
    resp.headers['Cache-Control'] = 'max-age=60'
    # <meta http-equiv="Expires" content="Thu, 01 Dec 1994 16:00:00 GMT">
    resp.html = api.template('cache_control2.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# Cache-Control ヘッダ: max-age=60
# ドキュメントの http-equiv Cache-Control 値: max-age=0
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => ie11/chrome とも ドキュメントの http-equiv cache-control は無視？
#
@api.route("/cache_control2a/")
async def cache_control2a(req, resp):
    now = datetime.datetime.now()
    resp.headers['Cache-Control'] = 'max-age=60'
    # <meta http-equiv="Cache-Control" content="max-age=0">
    resp.html = api.template('cache_control2a.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# レスポンスヘッダなし
# ドキュメントの http-equiv Cache-Control 値: max-age=60
#
# ie11
# リンククリック/アドレスバー: 再リクエストされる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: 再リクエストされる
# アドレスバー/リロード: 再リクエストされる
#
# => ie11/chrome とも ドキュメントの http-equiv cache-control は無視？
#
@api.route("/cache_control2b/")
async def cache_control2b(req, resp):
    now = datetime.datetime.now()
    # <meta http-equiv="Cache-Control" content="max-age=60">
    resp.html = api.template('cache_control2b.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# レスポンスヘッダなし
# ドキュメントの http-equiv Expires 値: 60秒後
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: 再リクエストされる
# アドレスバー/リロード: 再リクエストされる
#
# => ie11 はドキュメントの http-equiv が使われる
#    chrome は http-equiv expires を無視？
#
@api.route("/cache_control2c/")
async def cache_control2c(req, resp):
    now = datetime.datetime.now()
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    expires = utcnow + datetime.timedelta(seconds=60)
    # <meta http-equiv="Expires" content="現在時刻+60秒">
    resp.html = api.template('cache_control2c.html', time=now.strftime('%Y/%m/%d %H:%M:%S'), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))

# Expires ヘッダ: Thu, 01 Dec 1994 16:00:00 GMT
# ドキュメントの http-equiv Expires 値: 60秒後
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: 再リクエストされる
# アドレスバー/リロード: 再リクエストされる
#
# => ie11 はドキュメントの http-equiv が優先
#    chrome は http-equiv expires を無視？
#
@api.route("/cache_control2d/")
async def cache_control2d(req, resp):
    now = datetime.datetime.now()
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    expires = utcnow + datetime.timedelta(seconds=60)
    resp.headers['Expires'] = 'Thu, 01 Dec 1994 16:00:00 GMT'
    # <meta http-equiv="Expires" content="現在時刻+60秒">
    resp.html = api.template('cache_control2c.html', time=now.strftime('%Y/%m/%d %H:%M:%S'), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))

# Expires ヘッダ: 60秒後
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => Expires ヘッダは有効(念のため確認)
# 
@api.route("/cache_control2e/")
async def cache_control2e(req, resp):
    now = datetime.datetime.now()
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    expires = utcnow + datetime.timedelta(seconds=60)
    resp.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    resp.html = api.template('cache_control2e.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

# Cache-Control ヘッダ: max-age=60
# Expires ヘッダ: Thu, 01 Dec 1994 16:00:00 GMT
# MDN によると、Cache-Control に max-age 指定があると、Expires は無視される
#
# ie11
# リンククリック/アドレスバー: キャッシュが使われる
# リロード: 再リクエストされる
#
# chrome
# リンククリック: キャッシュが使われる
# アドレスバー/リロード: 再リクエストされる
#
# => MDN の記述どおり
#
@api.route("/cache_control3/")
async def cache_control3(req, resp):
    now = datetime.datetime.now()
    resp.headers['Cache-Control'] = 'max-age=60'
    resp.headers['Expires'] = 'Thu, 01 Dec 1994 16:00:00 GMT'
    resp.html = api.template('cache_control3.html', time=now.strftime('%Y/%m/%d %H:%M:%S'))

if __name__ == "__main__":
    api.run(address='0.0.0.0')

