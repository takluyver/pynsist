"use strict";

function JSManager() {
    return Qt.createQmlObject("import JSManager 1.0; JSManager {}",
                              appWindow, "JSManager");
}

function onLoad(){
    var jsManager = new JSManager();

    // Populate text
    jsManager.text.connect(function(text){
      jsText.text = text;
    });

    jsManager.get_text();
}
