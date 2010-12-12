$(function() {
    $( "[name=lang]" ).val( "{{ lang }}" ).change();
    $( "#word" ).val({{ word|tojson|safe }}).keypress();
});
