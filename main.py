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
from google.appengine.ext.webapp.util import run_wsgi_app
from flask import *
from flaskext.babel import Babel, gettext
from hangulize import hangulize, get_lang, Language, InvalidCodeError


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


def best_mimetype(request, html=True, json=True, plist=True):
    mimetypes = []
    if html:
        mimetypes.append('text/html')
    if json:
        mimetypes.append('application/json')
        if request.is_xhr:
            return mimetypes.pop()
    if plist:
        mimetypes.append('application/x-plist')
        mimetypes.append('application/plist+xml')
    return request.accept_mimetypes.best_match(mimetypes) or ''


def dump(data, mimetype):
    if 'json' in mimetype:
        return jsonify(**data)
    elif 'plist' in mimetype:
        try:
            import plistlib
            return plistlib.writePlistToString(data)
        except ImportError:
            pass
    raise TypeError('%s is not supported to dump' % mimetype)


def lang_dict(lang):
    if not isinstance(lang, Language):
        lang = get_lang(lang)
    lang_dict = dict(code=lang.code, name=lang.__class__.__name__)
    for prop in 'iso639_1', 'iso639_2', 'iso639_3':
        iso639 = getattr(lang, prop)
        if iso639:
            lang_dict[prop.replace('_', '-')] = iso639
    return lang_dict


@app.route('/')
def index():
    """The index page."""
    word = request.args.get('word', '')
    lang = request.args.get('lang', 'it')
    context = dict(word=word, lang=lang,
                   langs=get_langs(), locale=get_locale())
    mimetype = best_mimetype(request)

    def get_context(word, lang):
        try:
            result = hangulize(unicode(word), lang)
            return dict(success=True,
                        result=result, word=word, lang=lang_dict(lang))
        except (InvalidCodeError, ImportError):
            reason = '\'%s\' is not supported language or ' \
                     'invalid ISO639-3 code' % lang
        except Exception, e:
            reason = str(e)
        return dict(success=False, reason=reason)

    if word and lang:
        try:
            return dump(get_context(word, lang), mimetype)
        except TypeError:
            pass
        return render_template('result.html', **context)
    else:
        return render_template('index.html', **context)


@app.route('/langs')
def langs():
    import hangulize.langs
    langs = hangulize.langs.get_list()
    data = dict(success=True, langs=map(lang_dict, langs), length=len(langs))
    mimetype = best_mimetype(request, html=False)
    return dump(data, mimetype)


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
