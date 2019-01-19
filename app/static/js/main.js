/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */

/* global form, CodeMirror */

var cppEditor = CodeMirror.fromTextArea(document.getElementById('cpp-code'), {
  lineNumbers: true,
  matchBrackets: true,
  styleActiveLine: true,
  mode: 'text/x-c++src'
});

if (window.sessionStorage) {
  cppEditor.focus();
  var pos = window.sessionStorage.getItem('position');
  if (pos) {
    try {
      cppEditor.setCursor(JSON.parse(pos));
    } catch (e) {
      // continue, error does not matter here
    }
  }
}

if (window.localStorage) {
  if (!cppEditor.getValue()) {

    var code = window.localStorage.getItem('code');

    if (!code) {
      code =
        "#include <cstdio>\n#include <vector>\n\nint main()\n{\n    const char arr[10]{2,4,6,8};\n\n    for(const char& c : arr)\n    {\n      printf(\"c=%c\\n\", c);\n    }\n}";
    } else {
      code = JSON.parse(code);
    }

    try {
      console.log("restore");
      displayContents(code);
    } catch (e) {
      // hm
      console.log('failed');
    }
  }
}

var mac = CodeMirror.keyMap.default == CodeMirror.keyMap.macDefault;
CodeMirror.keyMap.default[(mac ? 'Cmd' : 'Ctrl') + '-Space'] = 'autocomplete';
var cppOutEditor = CodeMirror.fromTextArea(document.getElementById('cpp-code-out'), { // eslint-disable-line no-unused-vars
  lineNumbers: true,
  matchBrackets: true,
  styleActiveLine: true,
  readOnly: true,
  mode: 'text/x-c++src'
});
var stdErrEditor = CodeMirror.fromTextArea(document.getElementById('stderr-out'), { // eslint-disable-line no-unused-vars
  lineNumbers: false,
  readOnly: true,
  mode: 'shell'
});

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
  cppEditor.setValue(contents);
}

document.querySelector('.button-upload')
  .addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('file-input').click();
  });

document.getElementById('file-input')
  .addEventListener('change', readSingleFile);

document.querySelector('.button-download').addEventListener('click', function(event) {
  event.preventDefault();
  download('cppinsights.txt', cppEditor.getValue());
});

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

/*
function toggleConsole() {
  var element = document.getElementById('stderr-div').style;
  if ('none' == element.display) {
    element.display = 'initial';
  } else {
    element.display = 'none';
  }
}
*/

form.addEventListener('keydown', function(e) {
  if (!((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey)) return;
  submit();
});

function submit() {
  if (window.sessionStorage) {
    window.sessionStorage.setItem('position', JSON.stringify(cppEditor.getCursor()));
  }

  if (window.localStorage) {
    window.localStorage.setItem('code', JSON.stringify(cppEditor.getValue()));
  }

  form.submit();
}

function CopyClick() { // eslint-disable-line no-unused-vars
  var textToCopy = document.getElementById('lnkurl');

  textToCopy.select();

  document.execCommand('copy');
}

document.querySelector('.button-create-link').addEventListener('click', function(event) {
  event.preventDefault();
  event.stopPropagation();
  var hostname = window.location.hostname;
  var text = 'https://' + hostname + '/lnk?code=' + btoa(cppEditor.getValue()) + '&rev=1.0';

  var lnkElement = document.getElementById('lnkurl');
  lnkElement.value = text;

  var element = document.getElementById('copyDropdown');
  element.classList.toggle('show');
});

var runButton = document.querySelector('.button-run');
if (runButton) {
  runButton.title = 'Run C++ Insights (' + (mac ? 'Cmd-Return' : 'Ctrl-Enter') + ')';
  runButton.addEventListener('click', function(event) {
    event.preventDefault();
    submit();
  });
}

window.onclick = function(event) {
  if (!event.target.matches('.dropbtn') && !event.target.matches('.cpybtn') && !event.target.matches('#lnkurl')) {

    var dropdowns = document.getElementsByClassName('copyDownDownContent');
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
};
