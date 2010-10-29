$(function() {

// Elements
var word = $( "#word" ),
    locale = $( "[name=locale]" ),
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
                if ( data.result && reqWord === hangulize.prevWord ) {
                    result.text( data.result );
                    resultWrapper.animate({ marginTop: 0 }, delay );
                    hangulize.mode = EXPAND;
                    word.removeClass( "loading" );
                }
            }, "json" );
        }, delay );
    };

// Apply
word.keypress( hangulize ).keyup( hangulize ).keydown( hangulize );
locale.change(function() {
    delete hangulize.prevWord;
    hangulize.call( this );
});

// Default Focus
word.focus();

});
