$(function() {

// Elements
var word = $( "#word" ),
    lang = $( "[name=lang]" ),
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
            var reqWord = word.val();
            word.addClass( "loading" );
            $.get( "", form.serialize(), function( data ) {
                if ( data.success && reqWord === hangulize.prevWord ) {
                    result.text( data.result );
                    resultWrapper.animate({ marginTop: 0 }, delay );
                    hangulize.mode = EXPAND;
                    word.removeClass( "loading" );
                    if ( history.replaceState ) {
                        var enc = encodeURIComponent,
                            qs = "?";
                        qs += "lang=" + enc( lang.val() );
                        qs += "&word=" + enc( word.val() );
                        history.replaceState( null, "", qs );
                    }
                }
            }, "json" );
        }, delay );
    },
    shuffle = function() {
        var script = $( "<script></script>" );
        script.attr( "src", "/shuffle.js?lang=" + lang.val() );
        script.appendTo( document.body );
    };

// Apply
word.keypress( hangulize ).keyup( hangulize ).keydown( hangulize );
lang.change(function() {
    delete hangulize.prevWord;
    hangulize.call( this );
});
$( ".shuffle a" ).click(function() {
    shuffle();
    return false;
});

// Default Focus
word.focus();

});
