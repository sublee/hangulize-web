from __future__ import with_statement
import sys
import os
libpath = os.path.abspath('lib')
for dirname in (x for x in os.listdir(libpath) if x != 'hangulize'):
    sys.path.insert(0, os.path.join(libpath, dirname))
sys.path.insert(0, os.path.join(libpath, 'hangulize'))
sys.path.insert(0, libpath)
import re
import random
import plistlib
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from flaskext.babel import Babel, gettext
from hangulize import hangulize, get_lang, InvalidCodeError


LOCALES = ['ko', 'en']


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ko'
babel = Babel(app)


@babel.localeselector
def get_locale():
    """Returns a best matched language. It finds a language from the GET
    arguments, the cookie values, and the HTTP ``Accept-Language`` header.
    """
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
    """Sets a language to the cookie values."""
    locale = request.form["locale"]
    response = redirect(url_for("index"))
    response.set_cookie("locale", locale, 60 * 60 * 24 * 14)
    return response


def get_langs():
    """Returns the allowed languages in :mod:`hangulize`."""
    import hangulize.langs
    def iter():
        for code in hangulize.langs.get_list():
            yield code, gettext(code)
    def compare(x, y):
        return cmp(x[1], y[1])
    return sorted(iter(), cmp=compare)


@app.route('/favicon.ico')
def favicon():
    """Sends the favicon file."""
    return app.send_static_file('favicon.ico')


@app.route('/')
def index():
    """The index page."""
    word = request.args.get('word', '')
    lang = request.args.get('lang', 'it')
    context = dict(word=word, lang=lang,
                   langs=get_langs(), locale=get_locale())

    provided_mimetypes = 'application/json', 'application/x-plist', \
                         'application/plist+xml', 'text/html'
    mimetype = request.accept_mimetypes.best_match(provided_mimetypes) or ''

    def get_context(word, lang):
        try:
            result = hangulize(unicode(word), lang)
            language = get_lang(lang)
            lang_dict = dict(code=language.code,
                             name=language.__class__.__name__)
            for prop in 'iso639_1', 'iso639_2', 'iso639_3':
                iso639 = getattr(language, prop)
                if iso639:
                    lang_dict[prop.replace('_', '-')] = iso639
            return dict(success=True, result=result, word=word, lang=lang_dict)
        except (InvalidCodeError, ImportError):
            reason = '\'%s\' is not supported language or ' \
                     'invalid ISO639-3 code' % lang
        except Exception, e:
            reason = str(e)
        return dict(success=False, reason=reason)

    if word and lang:
        if 'json' in mimetype or request.is_xhr:
            return jsonify(**get_context(word, lang))
        elif 'plist' in mimetype:
            return plistlib.writePlistToString(get_context(word, lang))
        else:
            context.update(**get_context(word, lang));
            return render_template('result.html', **context)
    else:
        return render_template('index.html', **context)


@app.route('/readme')
def readme():
    from markdown import markdown
    module_path = __import__(hangulize.__module__).__file__
    readme_path = os.path.join(os.path.split(os.path.split(module_path)[0])[0],
                               'README.md')
    with open(readme_path) as readme_file:
        readme_text = ''.join(readme_file.readlines())
        readme = markdown(readme_text.decode('utf-8'))
    return render_template('readme.html', readme=readme)


@app.route('/shuffle.js')
def shuffle():
    """Sends a JavaScript code which fills a random language and word to the
    form of the index page.
    """
    lang = request.args.get('lang') or random.choice(list(get_langs()))[0]
    modname = lang.replace('.', '_')
    test = getattr(__import__('tests.%s' % modname), modname)
    case = [x for x in dir(test) \
              if x.endswith('TestCase') and not x.startswith('Hangulize')][0]
    test = getattr(test, case)
    word = random.choice(test.get_examples().keys())
    context = dict(lang=lang, word=word)
    return render_template('shuffle.js', **context)


if __name__ == '__main__':
    run_wsgi_app(app)
