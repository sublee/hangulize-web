import sys
import os
libpath = os.path.abspath('lib')
for dirname in os.listdir(libpath):
    sys.path.insert(0, os.path.join(libpath, dirname))
sys.path.insert(0, libpath)
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from flaskext.babel import Babel, gettext
from hangulize import hangulize


LOCALES = ['ko', 'en']


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ko'
babel = Babel(app)


@babel.localeselector
def get_locale():
    """Returns the HTTP accepted language."""
    return request.accept_languages.best_match(LOCALES)


def get_langs():
    """Returns the allowed languages in :mod:`hangulize`."""
    import hangulize.langs
    for loc in hangulize.langs.__all__:
        __import__('hangulize.langs.%s' % loc)
        lang = getattr(getattr(hangulize.langs, loc), loc)
        lang_name = gettext(lang.__name__)
        yield (loc, lang_name)


@app.route('/favicon.ico')
def favicon():
    """Sends the favicon file."""
    return app.send_static_file('favicon.ico')


@app.route('/')
def index():
    """The index page."""
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
