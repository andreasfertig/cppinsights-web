/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */
var cppEditor = CodeMirror.fromTextArea(document.getElementById("cpp-code"), {
    lineNumbers: true,
    matchBrackets: true,
    styleActiveLine: true,
    mode: "text/x-c++src"
});
var mac = CodeMirror.keyMap.default == CodeMirror.keyMap.macDefault;
CodeMirror.keyMap.default[(mac ? "Cmd" : "Ctrl") + "-Space"] = "autocomplete";
var cppOutEditor = CodeMirror.fromTextArea(document.getElementById("cpp-code-out"), {
    lineNumbers: true,
    matchBrackets: true,
    styleActiveLine: true,
    readOnly: true,
    mode: "text/x-c++src"
});
var stdErrEditor = CodeMirror.fromTextArea(document.getElementById("stderr-out"), {
    lineNumbers: false,
    readOnly: true,
    mode: "shell"
});

function copyText() {
    document.getElementById("cpp-code").value = cppEditor.getValue();
}

function readSingleFile(e) {
    var file = e.target.files[0];
    if (!file) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        displayContents(contents);
    };
    reader.readAsText(file);
}

function displayContents(contents) {
    /*var element = document.getElementById('cpp-code');
    element.textContent = contents;*/
    cppEditor.setValue(contents);
}

document.getElementById('file-input')
    .addEventListener('change', readSingleFile, false);

function dl() {
    download("f.txt", cppEditor.getValue());
}

function download(filename, text) {
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    pom.setAttribute('download', filename);
    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
}

function toggleConsole() {
    var element = document.getElementById('stderr-div').style
    if ('none' == element.display) {
        element.display = 'initial';
    } else {
        element.display = 'none';
    }
}

var form = document.getElementById('form');
//document.body.addEventListener('keydown', function(e) {
form.addEventListener('keydown', function(e) {
	if(!((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey)) return;

	var target = e.target;
	if(target.form) {
		target.form.submit();
	}
});

function CopyClick() {
  var textToCopy = document.getElementById("lnkurl");

  textToCopy.select();

  document.execCommand("copy");
}

function dropDownControl() {
    var hostname = window.location.hostname;
    var text = 'https://' + hostname + '/lnk?code=' + btoa(cppEditor.getValue()) + '&rev=1.0';

    var lnkElement = document.getElementById("lnkurl");
    lnkElement.value = text;

    var element = document.getElementById("copyDropdown");
    element.classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches('.dropbtn') && !event.target.matches('.cpybtn') && !event.target.matches('#lnkurl')) {

    var dropdowns = document.getElementsByClassName("copyDownDownContent");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}
