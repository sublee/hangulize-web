$(function() {
    $( "[name=lang]" ).val({{ lang|tojson|safe }});
    $( "#word" ).val({{ word|tojson|safe }}).keypress();
});
