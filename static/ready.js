// Elements
var word = $( "#word" ),
    form = word.parent(),
    resultWrapper = $( "#result" ),
    result = resultWrapper.find( "span:eq(0)" );

// Style
var blindHeight = resultWrapper.css( "margin-top" ),
    delay = 250;

// Events
var FOLD = true,
    EXPAND = false,
    hangulize = function() {
        if ( word.val() === hangulize.prevWord ) {
            // Do nothing when the word is not changed
            return;
        }
        hangulize.prevWord = word.val();

        if ( hangulize.mode === EXPAND ) {
            // Fold while inputting
            resultWrapper.stop().animate({ marginTop: blindHeight }, delay );
        }
        hangulize.mode = FOLD;
        clearTimeout( hangulize.timer );
        word.removeClass( "loading" );

        if ( !hangulize.prevWord ) {
            return;
        }
        hangulize.timer = setTimeout(function() {
            var lang = $( "[name=lang]" );
            var reqLang = lang.val();
            var reqWord = word.val();

            word.addClass( "loading" );

            gtag('event', reqLang, {
                'event_category': 'Hangulize',
                'event_label': reqWord
            });

            $.get( "", form.serialize(), function( data ) {
                if ( data.success && reqWord === hangulize.prevWord ) {
                    result.text( data.result );
                    resultWrapper.animate({ marginTop: 0 }, delay );
                    hangulize.mode = EXPAND;
                    word.removeClass( "loading" );
                    if ( history.replaceState ) {
                        var enc = encodeURIComponent,
                            qs = "?";
                        qs += "lang=" + enc( reqLang );
                        qs += "&word=" + enc( reqWord );
                        history.replaceState( null, "", qs );
                    }
                }
            }, "json" );
        }, delay );
    },
    shuffle = function() {
        var script = $( "<script></script>" ),
            lang = $( "[name=lang]" );
        script.attr( "src", "/shuffle.js?lang=" + lang.val() );
        script.appendTo( document.body );
    },
    improveSelector = function( select, cols ) {
        select = $( select );
        select.hide();

        var selectedLang = $( "<div class='selected-lang'></div>" ),
            langs = $( "<table class='langs'><tr></tr></table>" ),
            options = select.children(),
            width = 100 / cols,
            rows = Math.ceil( options.length / cols );

        for ( var i = 0; i < cols; i++ ) {
            var td = $( "<td></td>" );
            td.width( width + "%" );
            for ( var j = 0; j < rows; j++ ) {
                var opt = options.eq( i * rows + j ),
                    lang = $( "<a href='#'></a>" );
                opt.data( "mirror", lang );
                lang.text( opt.text() ).data( "lang", opt.val() );
                if ( opt.attr( "selected" ) ) {
                    lang.addClass( "selected" );
                }
                lang.click(function() {
                    var lang = $( this );
                    select.val( lang.data( "lang" ) ).change();
                    langs.hide();
                    return false;
                });
                lang.appendTo( td );
            }
            j++;
            langs.find( "tr" ).append( td );
        }

        select.change(function() {
            var select = $( this ),
                opt = select.find( ":selected" );
            langs.find( ".selected" ).removeClass( "selected" );
            opt.data( "mirror" ).addClass( "selected" );
            selectedLang.find( "a" ).text( opt.text() );
        });

        selectedLang.html( "<a class='lang' href='#langs'></a>" );
        selectedLang.find( "a" ).text( select.find( ":selected" ).text() )
        selectedLang.click(function() {
            langs.show();
            return false;
        });
        selectedLang.insertAfter( select ).after( langs );
    };

// Apply
word.keypress( hangulize ).keyup( hangulize ).keydown( hangulize );
improveSelector( $( "[name=lang]" ).change(function() {
    delete hangulize.prevWord;
    hangulize.call( this );
}), 3 );
$( ".shuffle a" ).click(function() {
    shuffle();
    return false;
});
$( $.browser.msie ? document.body : window ).click(function( e ) {
    $( ".langs" ).each(function() {
        var langs = $( this ),
            p = langs.position(),
            horizontal = e.pageX >= p.left && e.pageX <= p.left + langs.width(),
            vertical = e.pageY >= p.top && e.pageY <= p.top + langs.height();
        if ( !(horizontal && vertical) ) {
            langs.hide();
        }
    });
});

// Default Focus
