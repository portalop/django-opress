var parameters = {
    'fields': ['titulo', 'imagen', 'enlace', 'contenido', 'flickr_user', 'flickr_album', 'timeline'],
    'types':[
	    {'value': '', 'show': []},
	    {'value': 'html', 'show': ['titulo', 'contenido']},
        {'value': 'image', 'show': ['titulo', 'imagen', 'enlace']},
	    {'value': 'card', 'show': ['titulo', 'imagen', 'contenido']},
	    {'value': 'timeline', 'show': ['titulo', 'timeline']},
	    {'value': 'flickr', 'show': ['titulo', 'flickr_user', 'flickr_album']},
    ]
};

function hide_fields(select) {
    for (i=0; i<parameters.fields.length; i++)
        $(select).closest('.grp-module').children('.grp-row.' + parameters.fields[i]).hide();
    var value = $(select).val();
    for (i=0; i<parameters.types.length; i++)
        if (parameters.types[i].value==value) {
            var show = parameters.types[i].show;
            var parent_module = $(select).closest('.grp-module');
            for (j=0; j<show.length; j++)
                parent_module.children('.grp-row.' + show[j]).show();
        }
}

$(function () {
    $('.select_block').each(function() {
        hide_fields(this);
    })
})