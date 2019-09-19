var jshelper;

new QWebChannel(qt.webChannelTransport, function (channel) {
    jshelper = channel.objects.jshelper;
});

var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/yaml");
editor.setUseSoftTabs(true);
editor.setTabSize(4);
editor.session.on('change', function(delta) {
    alert('Bob');
    jshelper._returnText(editor.getValue(), function(val) {} );
});