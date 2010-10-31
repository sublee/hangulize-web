import sys
import os
libpath = os.path.abspath('lib')
for dirname in os.listdir(libpath):
    sys.path.insert(0, os.path.join(libpath, dirname))
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from hangulize import hangulize


app = Flask(__name__)


def get_langs():
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
    context = dict(word=word, locale=locale, langs=get_langs())
    if word and locale:
        result = hangulize(unicode(word))
        if request.is_xhr:
            return jsonify(result=result, locale=locale)
        else:
            context.update(result=result);
            return render_template('result.html', **context)
    else:
        return render_template('index.html', **context)


if __name__ == '__main__':
    run_wsgi_app(app)

