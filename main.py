import sys
import os
libpath = os.path.abspath('lib')
for dirname in os.listdir(libpath):
    sys.path.insert(0, os.path.join(libpath, dirname))
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from hangulize import hangulize, langs


app = Flask(__name__)
locales = langs.__all__


@app.route('/')
def index():
    word = request.args.get('word', '')
    locale = request.args.get('locale', 'it')
    context = dict(word=word, locale=locale, locales=locales)
    if word:
        context['hangulized'] = hangulize(unicode(word), locale=locale)
        return render_template('result.html', **context)
    else:
        return render_template('input.html', **context)


if __name__ == '__main__':
    run_wsgi_app(app)

