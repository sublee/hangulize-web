import sys
import os
libpath = os.path.abspath('lib')
for dirname in os.listdir(libpath):
    sys.path.insert(0, os.path.join(libpath, dirname))
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from hangulize import hangulize


app = Flask(__name__)


def get_locales():
    import hangulize.langs
    for loc in hangulize.langs.__all__:
        __import__('hangulize.langs.%s' % loc)
        yield (loc, getattr(getattr(hangulize.langs, loc), loc))

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def index():
    word = request.args.get('word', '')
    locale = request.args.get('locale', 'it')
    if word:
        return jsonify(result=hangulize(unicode(word), locale=locale))
    else:
        context = dict(word=word, locale=locale, locales=get_locales())
        return render_template('index.html', **context)


if __name__ == '__main__':
    run_wsgi_app(app)

