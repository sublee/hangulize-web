$(function() {
    $( "[name=lang][value={{ lang }}]" ).attr( "checked", true ).change();
    $( "#word" ).val({{ word|tojson|safe }}).keypress();
});
