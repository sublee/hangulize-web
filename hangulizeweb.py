# -*- coding: utf-8 -*-
"""
    hangulizeweb
    ~~~~~~~~~~~~

    The Flask application to use Hangulize.

"""
from __future__ import with_statement
from datetime import datetime
import json
import random
import urllib

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flaskext.babel import Babel, gettext
from google.appengine.api import urlfetch
from pytz import timezone, utc

from hangulize import get_lang
from hangulize.models import Language


__all__ = ['app']


LOCALES = ['ko', 'en']
JSONP_PARAM = 'jsonp'


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ko'
babel = Babel(app)


api = 'https://api.hangulize.org/v2'


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


specs = {}


def fetch_specs():
    if specs:
        return specs

    r = urlfetch.fetch(api + '/specs', headers={'Accept': 'application/json'})
    specs.update({s['lang']['id']: s for s in json.loads(r.content)['specs']})
    return specs


def get_langs():
    """Returns the allowed languages in :mod:`hangulize`."""
    def iter():
        for lang, spec in fetch_specs().items():
            attr = {'ko': 'korean', 'en': 'english'}[get_locale()]
            name = spec['lang'][attr]
            yield lang, name
    def compare(x, y):
        return cmp(x[1], y[1])
    return sorted(iter(), cmp=compare)


def get_example(lang=None):
    lang = lang or random.choice(list(get_langs()))[0]

    specs = fetch_specs()
    spec = specs[lang]
    example = random.choice(spec['test'])

    return lang, example['word']


def best_mimetype(html=True, json=True, plist=True):
    mimetypes = []
    if json:
        mimetypes.append('application/json')
        if request.is_xhr or request.args.get(JSONP_PARAM):
            return mimetypes.pop()
    if plist:
        mimetypes.append('application/x-plist')
        mimetypes.append('application/plist+xml')
    if html:
        mimetypes.append('text/html')
    return request.accept_mimetypes.best_match(mimetypes) or ''


def dump(data, mimetype=None):
    mimetype = mimetype or best_mimetype()
    if 'json' in mimetype:
        json = jsonify(**data)
        jsonp = request.args.get(JSONP_PARAM)
        if jsonp:
            json.data = '%s(%s)' % (jsonp, json.data)
        return json
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
    lang_dict = dict(code=lang.code, name=lang.__class__.__name__,
                     label=gettext(lang.code))
    for prop in 'iso639_1', 'iso639_2', 'iso639_3':
        iso639 = getattr(lang, prop)
        if iso639:
            lang_dict[prop.replace('_', '-')] = iso639
    return lang_dict


def hangulize(word, lang):
    s_word = urllib.quote(word.encode('utf-8'))
    s_lang = urllib.quote(lang)

    r = urlfetch.fetch(api + '/hangulized/%s/%s' % (s_lang, s_word),
                       headers={'Accept': 'text/plain'})

    return r.content


def get_result(lang, word):
    try:
        result = hangulize(unicode(word), lang)
        return dict(success=True,
                    result=result, word=word, lang=lang_dict(lang))
    except (ValueError, ImportError):
        reason = '\'%s\' is not supported language or ' \
                 'invalid ISO639-3 code' % lang
    except Exception, e:
        reason = str(e)
    return dict(success=False, reason=reason)


@app.route('/')
def index():
    """The index page."""
    lang = request.args.get('lang')
    word = request.args.get('word')
    kor_tz = timezone('Asia/Seoul')
    kor_dt = datetime.utcnow().replace(tzinfo=utc).astimezone(kor_tz)
    if (kor_dt.month, kor_dt.day) == (10, 9):
        logo_name = 'logo-hangul.png'
    else:
        logo_name = 'logo.png'
    context = dict(langs=get_langs(), locale=get_locale(), logo_name=logo_name)
    if lang and word:
        data = get_result(lang, word)
        try:
            return dump(data)
        except TypeError:
            context.update(**data)
            return render_template('result.html', **context)
    return render_template('index.html', **context)


@app.route('/langs')
def langs():
    """The language list."""
    import hangulize.langs
    langs = hangulize.langs.get_list()
    data = dict(success=True, langs=map(lang_dict, langs), length=len(langs))
    mimetype = best_mimetype(html=False)
    return dump(data, mimetype)


@app.route('/example')
def example():
    lang, word = get_example(request.args.get('lang'))
    return dump(get_result(lang, word))


@app.route('/shuffle.js')
def shuffle():
    """Sends a JavaScript code which fills a random language and word to the
    form of the index page.
    """
    lang, word = get_example(request.args.get('lang'))
    context = dict(lang=lang, word=word)
    return render_template('shuffle.js', **context)


@app.route('/favicon.ico')
def favicon():
    """Sends the favicon file."""
    return app.send_static_file('favicon.ico')
