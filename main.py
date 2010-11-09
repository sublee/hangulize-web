from __future__ import with_statement
import sys
import os
libpath = os.path.abspath('lib')
for dirname in os.listdir(libpath):
    sys.path.insert(0, os.path.join(libpath, dirname))
sys.path.insert(0, libpath)
import re
import random
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
    try:
        return request.args["locale"]
    except KeyError:
        pass
    try:
        return request.cookies["locale"]
    except KeyError:
        return request.accept_languages.best_match(LOCALES)


@app.route("/locale", methods=["post"])
def set_locale():
    locale = request.form["locale"]
    response = redirect(url_for("index"))
    response.set_cookie("locale", locale, 60 * 60 * 24 * 14)
    return response


def all_langs():
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
    mimetypes = ['text/html', 'application/json']
    mimetype = request.accept_mimetypes.best_match(mimetypes)
    word = request.args.get('word', '')
    lang = request.args.get('lang', 'it')
    context = dict(word=word, lang=lang, langs=all_langs(),
                   locale=get_locale())
    if word and lang:
        result = hangulize(unicode(word), lang)
        if mimetype == mimetypes[1]:
            return jsonify(result=result, lang=lang)
        else:
            context.update(result=result);
            return render_template('result.html', **context)
    else:
        return render_template('index.html', **context)


@app.route('/shuffle.js')
def shuffle():
    lang = random.choice(list(all_langs()))[0]
    test_path = os.path.join(libpath, 'hangulize', 'tests', lang + '.py')
    assertion_pattern = re.compile("assert u'(?P<want>.+)' == " \
                                   "self\.hangulize\(u'(?P<word>.+)'\)")
    with open(test_path) as f:
        test_code = ''.join(f.readlines())
        assertion = random.choice(list(assertion_pattern.finditer(test_code)))
    context = dict(lang=lang, word=assertion.group('word'))
    return render_template('shuffle.js', **context)


if __name__ == '__main__':
    run_wsgi_app(app)
