/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */

/* global CodeMirror, storageAllowed, onLoad */

var DEFAULT_CPP_STD = 'cpp17';
// load cookies
onLoad();

var cppEditor = CodeMirror.fromTextArea(document.getElementById('cpp-code'), {
  lineNumbers: true,
  matchBrackets: true,
  styleActiveLine: true,
  mode: 'text/x-c++src'
});

cppEditor.focus();
var insightsOptions = [DEFAULT_CPP_STD];
var code = cppEditor.getValue();

function setStandard(std) {
  var selected = $('#insightsOptions').multipleSelect('getSelects', 'value');

  var filtered = selected.filter(function(value, index, arr) { // eslint-disable-line no-unused-vars
    return !value.startsWith('cpp');
  });

  filtered.push(std);

  $('#insightsOptions').multipleSelect('setSelects', filtered);
}

$('#insightsOptions').multipleSelect({
  placeholder: 'C++ Insights Options',
  selectAll: false,
  onClick: function(opt) {
    if (opt.value.startsWith('cpp')) {
      setStandard(opt.value);
    }
  },
  onOptgroupClick: function(group) {
    if ('C++ Standard' == group.label) {
      setStandard(DEFAULT_CPP_STD);
    }
  },
});

function changeFontSize(value) {
  var el = document.getElementById('code2');
  el.style.fontSize = value;
  var el = document.getElementById('stdout');
  el.style.fontSize = value;
  var el = document.getElementById('stderr');
  el.style.fontSize = value;
}

$('#fontSizer').multipleSelect({
  placeholder: 'A+',
  selectAll: false,
  single: true,
  onClick: function(opt) {

    changeFontSize(opt.value);

    $('#fontSizer').multipleSelect('setSelects', opt);

    if (window.localStorage && storageAllowed()) {
      window.localStorage.setItem('fontSize', JSON.stringify(opt.value));
    }
  },
});
// check if the current url contains '/lnk' which means that we opened a link. In that case do not load the values from
// local storage.
function isLink() {
  return (window.location.href.indexOf('/lnk') > -1);
}

// If this is a link add a keydown listener to the cppEditor and remove the link, if the code is changed.
if (isLink()) {
  cppEditor.on('keydown', function(instance, event) { // eslint-disable-line no-unused-vars
    if (isLink()) {
      history.pushState(null, null, '/');
    }

  });
}

if (window.localStorage && storageAllowed() && !isLink()) {
  if (!cppEditor.getValue()) {
    insightsOptions = window.localStorage.getItem('insightsOptions');

    if (insightsOptions) {
      insightsOptions = JSON.parse(insightsOptions);
    }

    code = window.localStorage.getItem('code');
    if (code) {
      code = JSON.parse(code);
    }
  }
}

if (!code) {
  insightsOptions = [DEFAULT_CPP_STD];
  code =
    '#include <cstdio>\n\nint main()\n{\n    const char arr[10]{2,4,6,8};\n\n    for(const char& c : arr)\n    {\n      printf("c=%c\\n", c);\n    }\n}';

}

//try {
if (!isLink()) {
  $('#insightsOptions').multipleSelect('setSelects', insightsOptions);
}

var DEFAULT_FONT_SIZE = 'initial';

if (window.localStorage && storageAllowed()) {
  var fontSize = window.localStorage.getItem('fontSize');
  if (fontSize) {
    DEFAULT_FONT_SIZE = JSON.parse(fontSize);
  }
}

$('#fontSizer').multipleSelect('setSelects', [DEFAULT_FONT_SIZE]);
changeFontSize(DEFAULT_FONT_SIZE);

displayContents(code);
//} catch (e) {
// hm
//}

var mac = CodeMirror.keyMap.default == CodeMirror.keyMap.macDefault;
CodeMirror.keyMap.default[(mac ? 'Cmd' : 'Ctrl') + '-Space'] = 'autocomplete';
var cppOutEditor = CodeMirror.fromTextArea(document.getElementById(
  'cpp-code-out'), { // eslint-disable-line no-unused-vars
  lineNumbers: true,
  matchBrackets: true,
  styleActiveLine: true,
  readOnly: true,
  mode: 'text/x-c++src'
});
var stdErrEditor = CodeMirror.fromTextArea(document.getElementById(
  'stderr-out'), { // eslint-disable-line no-unused-vars
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

function getInsightsOptions() {
  return $('#insightsOptions').multipleSelect('getSelects', 'value');
}

function getCppStd() {
  var filtered = getInsightsOptions().filter(function(value, index, arr) { // eslint-disable-line no-unused-vars
    return value.startsWith('cpp');
  });

  return filtered[0];
}

function OnRunKeyDown(e) {
  if (!((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey)) return;
  Transform();
}

function OnRunClicked(e) {
  e.preventDefault();
  Transform();
  cppEditor.focus();
}

function OnWaitForResultKeyDown(e) {
  if (!((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey)) return;
  stdErrEditor.setValue('A request is already in the air...');
}

function OnWaitForResultRunClicked(e) {
  e.preventDefault();
  stdErrEditor.setValue('A request is already in the air...');
}

function RunListenersSetup(addKeyDown, removeRunBtn, addRunBtn) {
  window.onkeyup = addKeyDown;

  var runButton = document.querySelector('.button-run');
  if (runButton) {
    runButton.title = 'Run C++ Insights (' + (mac ? 'Cmd-Return' : 'Ctrl-Enter') + ')';
    runButton.removeEventListener('click', removeRunBtn);
    runButton.addEventListener('click', addRunBtn);
  }
  cppEditor.focus();
}

function SetRunListeners() {
  RunListenersSetup(OnRunKeyDown, OnWaitForResultRunClicked, OnRunClicked);
}

// set them initially
SetRunListeners();

function SetWaitForResultListeners() {
  RunListenersSetup(OnWaitForResultKeyDown, OnRunClicked, OnWaitForResultRunClicked);
}

function CopyClick() { // eslint-disable-line no-unused-vars
  var textToCopy = document.getElementById('lnkurl');

  textToCopy.select();

  document.execCommand('copy');
}

// at least FireFox has a problem with just btoa with UTF-8 characters
function b64UTFEncode(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, v) {
    return String.fromCharCode(parseInt(v, 16));
  }));
}

function updateLinkToCompilerExplorer() {
  var cppstdparam = '-std=' + getCppStd().replace('cpp', 'c++');
  var clientstate = {
    sessions: [{
      id: 1,
      language: 'c++',
      source: cppEditor.getValue(),
      compilers: [{
        id: 'gsnapshot',
        options: cppstdparam
      }]
    }]
  };

  var link = location.protocol + '//godbolt.org/clientstate/' + b64UTFEncode(JSON.stringify(clientstate));
  var ceButton = document.getElementById('button-ce');
  ceButton.href = link;
}

document.querySelector('#button-ce').addEventListener('mousedown', function() {
  updateLinkToCompilerExplorer();
});

document.querySelector('.button-create-link').addEventListener('click', function(event) {
  event.preventDefault();
  event.stopPropagation();
  var cppStd = getCppStd();
  var insightsOptions = getInsightsOptions();
  var text = getURLBase() + '/lnk?code=' + b64UTFEncode(cppEditor.getValue()) + '&insightsOptions=' +
    insightsOptions + '&std=' + cppStd +
    '&rev=1.0';

  var lnkElement = document.getElementById('lnkurl');
  lnkElement.value = text;

  var element = document.getElementById('copyDropdown');
  element.classList.toggle('show');
});

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

// without trailing '/'
function getURLBase() {
  return location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '');
}

// Send a transformation request to the server
function Transform() { // eslint-disable-line no-unused-vars

  var request = new XMLHttpRequest();

  if (window.localStorage && storageAllowed()) {
    window.localStorage.setItem('code', JSON.stringify(cppEditor.getValue()));
    window.localStorage.setItem('insightsOptions', JSON.stringify(getInsightsOptions()));
  }

  request.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var response = JSON.parse(this.responseText);
      cppOutEditor.setValue(response.stdout);
      stdErrEditor.setValue(response.stderr);
      SetRunListeners();
    } else if (this.readyState == 4 && this.status != 200) {
      stdErrEditor.setValue('Sorry, your request failed');
      SetRunListeners();
    }
  };

  stdErrEditor.setValue('Waiting for response...');

  var url = getURLBase() + '/api/v1/transform';

  request.open('POST', url, true);
  request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

  var data = {};

  data.insightsOptions = getInsightsOptions();
  data.code = cppEditor.getValue();

  SetWaitForResultListeners();
  request.send(JSON.stringify(data));
}
