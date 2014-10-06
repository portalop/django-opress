
function CustomFileBrowser(field_name, url, type, win) {
    
    var cmsURL = '/admin/filebrowser/browse/?pop=2';
    cmsURL = cmsURL + '&type=' + type;
    
    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 980,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: 'yes',
        scrollbars: 'yes',
        inline: 'no',  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: 'no'
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    });
    return false;
}

tinyMCE.init({
    
    // see http://www.tinymce.com/wiki.php/Configuration
    
    // Init
    mode : "specific_textareas",
    editor_selector : "mceEditor",
    theme: 'advanced',
    skin: 'grappelli',
    
    // General
    accessibility_warnings: false,
    browsers: 'gecko,msie,safari,opera',
    dialog_type: 'modal',
    editor_deselector: 'mceNoEditor',
    keep_styles: false,
    language: 'es',
    object_resizing: false,
    plugins: 'advimage,advlink,fullscreen,paste,table,media,searchreplace,grappelli,template,youtube,gallerycon,inlinepopups',
    jquery_url: '/hispaniae/static/grappelli/jquery/jquery-1.9.1.min.js',
    content_css: '/hispaniae/static/grappelli/tinymce/jscripts/tiny_mce/plugins/gallerycon/css/tiny-mce-extra.css',
    // directionality : "rtl",
    
    // Callbacks
    file_browser_callback: 'CustomFileBrowser',


  gallerycon_settings :
  {
    urls :
    {
      galleries : '/hispaniae/admin/opress/galleries?format=json&jsoncallback=?',
      images : '/hispaniae/admin/opress/images/{gallery_id}?format=json&jsoncallback=?',
      image : '/hispaniae/admin/opress/image/{image_id}?format=json&jsoncallback=?',
      img_src: '/hispaniae/admin/opress/image_src/{image_id}/{size_id}?format=json&jsoncallback=?'
    },
    sizes :
    [
      {
        id : 'event_thumb',
        name : 'Tiny thumbnail'
      },
      {
        id : 'thumbnail',
        name : 'Thumbnail'
      },
      {
        id : 'display',
        name : 'Display size'
      },
      {
        id : 'square',
        name : 'Square thumbnail'
      },
    ],
    default_size : 'display',
    default_alignment : 'left'
//    link :
//    {
//      rel : 'lightbox-{gallery_id}', // can_have {image_id}, {gallery_id} and {size_id} placeholders
//      class : '', // can_have {image_id}, {gallery_id} and {size_id} placeholders
//      size : 'display' // Either size or href should be set
    //  href : 'http://somelink.that_can_have{image_id}and{gallery_id}and{size_id}placeholders'
//    }
  },


    // Cleanup/Output
    element_format: 'xhtml',
    fix_list_elements: true,
    forced_root_block: 'p',
    // style formsts overrides theme_advanced_styles
    // see http://www.tinymce.com/wiki.php/Configuration:style_formats
    style_formats: [
        {title: 'Paragraph Small', block : 'p', classes: 'p_small'},
        {title: 'Paragraph ImageCaption', block : 'p', classes: 'p_caption'},
        {title: 'Clearfix', block : 'p', classes: 'clearfix'},
        {title: 'Code', block : 'p', classes: 'code'}
    ],
    verify_html: true,

    // URL
    relative_urls: false,
    remove_script_host: true,

    // Layout
    width: 758,
    height: 300,
    indentation: '10px',
    
    // Theme Advanced
    theme_advanced_toolbar_location: 'top',
    theme_advanced_toolbar_align: 'left',
    theme_advanced_statusbar_location: 'bottom',
    theme_advanced_buttons1: 'formatselect,styleselect,|,bold,italic,underline,|,bullist,numlist,blockquote,|,justifyleft,justifycenter,justifyright,justifyfull,|,undo,redo,|,link,unlink,|,gallerycon,|,fullscreen,|,grappelli_adv',
    theme_advanced_buttons2: 'search,|,pasteword,youtube,charmap,|,code,|,table,cleanup,grappelli_documentstructure',
    theme_advanced_buttons3: '',
    theme_advanced_path: false,
    theme_advanced_blockformats: 'p,h1,h2,h3,h4,pre',
    theme_advanced_resizing: true,
    theme_advanced_resize_horizontal: false,
    theme_advanced_resizing_use_cookie: true,
    
    // Templates
    // see http://www.tinymce.com/wiki.php/Plugin:template
    // please note that you need to add the URLs (src) to your url-patterns
    // with django.views.generic.simple.direct_to_template
   // template_templates : [
   //     {
   //         title : '2 Columns',
   //         src : '/path/to/your/template/',
   //         description : '2 Columns.'
   //     },
   //     {
   //         title : '4 Columns',
   //         src : '/path/to/your/template/',
   //         description : '4 Columns.'
   //     }
   // ],

    // Image Plugin
    // see http://www.tinymce.com/wiki.php/Plugin:advimage
    theme_advanced_styles: 'Image Left=img_left;Image Right=img_right;Image Block=img_block',
    advimage_update_dimensions_onchange: true,
    
    // Link Settings
    // see http://www.tinymce.com/wiki.php/Plugin:advlink
    advlink_styles: 'Internal Link=internal;External Link=external',

    // Media Plugin
    // see http://www.tinymce.com/wiki.php/Plugin:media
    media_strict: true,
    
    // Grappelli Settings
    grappelli_adv_hidden: false,
    grappelli_show_documentstructure: false
    
    // Elements
    // valid_elements: '@[id|class|style|title|dir<ltr?rtl|lang|xml::lang|onclick|ondblclick|'
    // + 'onmousedown|onmouseup|onmouseover|onmousemove|onmouseout|onkeypress|'
    // + 'onkeydown|onkeyup],a[rel|rev|charset|hreflang|tabindex|accesskey|type|'
    // + 'name|href|target|title|class|onfocus|onblur],strong/b,em/i,strike,u,'
    // + '#p,-ol[type|compact],-ul[type|compact],-li,br,img[longdesc|usemap|'
    // + 'src|border|alt=|title|hspace|vspace|width|height|align],-sub,-sup,'
    // + '-blockquote,-table[border=0|cellspacing|cellpadding|width|frame|rules|'
    // + 'height|align|summary|bgcolor|background|bordercolor],-tr[rowspan|width|'
    // + 'height|align|valign|bgcolor|background|bordercolor],tbody,thead,tfoot,'
    // + '#td[colspan|rowspan|width|height|align|valign|bgcolor|background|bordercolor'
    // + '|scope],#th[colspan|rowspan|width|height|align|valign|scope],caption,-div,'
    // + '-span,-code,-pre,address,-h1,-h2,-h3,-h4,-h5,-h6,hr[size|noshade],-font[face'
    // + '|size|color],dd,dl,dt,cite,abbr,acronym,del[datetime|cite],ins[datetime|cite],'
    // + 'object[classid|width|height|codebase|*],param[name|value|_value],embed[type|width'
    // + '|height|src|*],script[src|type],map[name],area[shape|coords|href|alt|target],bdo,'
    // + 'button,col[align|char|charoff|span|valign|width],colgroup[align|char|charoff|span|'
    // + 'valign|width],dfn,fieldset,form[action|accept|accept-charset|enctype|method],'
    // + 'input[accept|alt|checked|disabled|maxlength|name|readonly|size|src|type|value],'
    // + 'kbd,label[for],legend,noscript,optgroup[label|disabled],option[disabled|label|selected|value],'
    // + 'q[cite],samp,select[disabled|multiple|name|size],small,'
    // + 'textarea[cols|rows|disabled|name|readonly],tt,var,big',
    // extended_valid_elements : 'embed[width|height|name|flashvars|src|bgcolor|align|play|'
    // + 'loop|quality|allowscriptaccess|type|pluginspage]'
    
});

