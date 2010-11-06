$(function() {
    $( "[name=locale]" ).val({{ locale|tojson|safe }});
    $( "#word" ).val({{ word|tojson|safe }}).keypress();
});
