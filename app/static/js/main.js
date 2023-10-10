/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */

/* global CodeMirror, onLoad, getLocalStorageItem, setLocalStorageItem, canUseLocalStorage */

var DEFAULT_CPP_STD = 'cpp17';
var DEFAULT_REV = '1.0';

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
  var elCode = document.getElementById('stdin');
  elCode.style.fontSize = value;
  var elStdOut = document.getElementById('stdout');
  elStdOut.style.fontSize = value;
  var elStdErr = document.getElementById('stderr');
  elStdErr.style.fontSize = value;
}

$('#fontSizer').multipleSelect({
  placeholder: 'A+',
  selectAll: false,
  single: true,
  onClick: function(opt) {

    changeFontSize(opt.value);

    $('#fontSizer').multipleSelect('setSelects', opt);

    setLocalStorageItem('fontSize', opt.value);
  },
});
// check if the current url contains '/lnk' which means that we opened a link. In that case do not load the values from
// local storage.
function isLink() {
  return (window.location.href.indexOf('/lnk') > -1) || (window.location.href.indexOf('/s') > -1);
}

// If this is a link add a keydown listener to the cppEditor and remove the link, if the code is changed.
if (isLink()) {
  cppEditor.on('keydown', function(instance, event) { // eslint-disable-line no-unused-vars
    if (isLink()) {
      history.pushState(null, null, '/');
    }

  });
}

if (canUseLocalStorage() && !isLink()) {
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

var DEFAULT_FONT_SIZE = getLocalStorageItem('fontSize', 'initial');

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

function toggleButton(divId) { // eslint-disable-line no-unused-vars
  var element = document.getElementById(divId).style;

  if ('none' == element.display) {
    element.display = 'initial';

  } else {
    element.display = 'none';

  }

  setLocalStorageItem(divId, element.display);
}

function setElementDisplay(divId, value) {
  var element = document.getElementById(divId).style;

  element.display = value;
}

setElementDisplay('banner', getLocalStorageItem('banner', 'initial'));
showHideConsole(getLocalStorageItem('stderr-div', 'initial'));

/* -- resizing columns and rows -- */

function changeGridConsoleRowHeight(newHeight) {
  var allm = document.getElementById('allmain');
  var navHeight = document.getElementById('nav').clientHeight + 'px';

  allm.style.gridTemplateRows = navHeight + ' ' + 'auto' + ' 10px ' + newHeight;
}

var dragging = false;
var draggingMode = '';
var consoleClosed = false;

function showHideConsole(show) {
  var elem = document.getElementById('stderr-div');
  var err = document.getElementById('errstd');
  var oldHeight = err.clientHeight;

  var allm = document.getElementById('allmain');

  var element = elem.style;
  var minimized = document.getElementById('console-btn');

  if (show) {
    element.display = 'initial';

    allm.style.removeProperty('grid-template-rows');

    minimized.classList.remove('minimized');
    // refresh codemirror, otherwise the editor contains the old value
    stdErrEditor.refresh();

  } else {
    var height = elem.clientHeight;

    element.display = 'none';
    var errStyleHeight = 'calc(' + oldHeight + 'px - ' + height + 'px)';
    changeGridConsoleRowHeight(errStyleHeight);

    minimized.classList.add('minimized');
  }

  consoleClosed = (element.display == 'none');
}

function toggleConsole() { // eslint-disable-line no-unused-vars
  var element = document.getElementById('stderr-div').style;

  showHideConsole('none' == element.display);

  setLocalStorageItem('stderr-div', !consoleClosed);
}

function dragstart(e, mode) {
  e.preventDefault();
  dragging = true;
  draggingMode = mode;
}

function dragmove(e) {
  if (dragging) {
    var percentage = 0;
    var mainPercentage = 0;

    if ('v' == draggingMode) {
      percentage = (e.pageX / window.innerWidth) * 100;
      if (percentage > 5 && percentage < 98) {
        mainPercentage = 100 - percentage;
        var allm = document.getElementById('allmain');

        allm.style.gridTemplateColumns = 'calc(' + percentage + '% - 5px) 10px calc(' + mainPercentage + '% - 5px)';
      }
    } else if ('h' == draggingMode) {
      if (consoleClosed) {
        return;
      }

      percentage = (e.pageY / window.innerHeight) * 100;

      if (percentage > 5 && percentage < 94) {
        mainPercentage = 100 - percentage;
        changeGridConsoleRowHeight(mainPercentage + '%');
      }
    }

  }
}

function dragend() {
  dragging = false;
}

if (window.addEventListener) {
  document.getElementById('vdragbar').addEventListener('mousedown', function(e) {
    dragstart(e, 'v');
  });
  document.getElementById('vdragbar').addEventListener('touchstart', function(e) {
    dragstart(e, 'v');
  });
  document.getElementById('hdragbar').addEventListener('mousedown', function(e) {
    dragstart(e, 'h');
  });
  document.getElementById('hdragbar').addEventListener('touchstart', function(e) {
    dragstart(e, 'h');
  });
  window.addEventListener('mousemove', function(e) {
    dragmove(e);
  });
  window.addEventListener('touchmove', function(e) {
    dragmove(e);
  });
  window.addEventListener('mouseup', dragend);
  window.addEventListener('touchend', dragend);
}

/* -- resizing columns and rows -- */

function getInsightsOptions() {
  return $('#insightsOptions').multipleSelect('getSelects', 'value');
}

function getCppStd() {
  var filtered = getInsightsOptions().filter(function(value, index, arr) { // eslint-disable-line no-unused-vars
    return value.startsWith('cpp');
  });

  return filtered[0];
}

function getUseLibStdCpp() {
  var filtered = getInsightsOptions().filter(function(value, index, arr) { // eslint-disable-line no-unused-vars
    return value.startsWith('use-libcpp');
  });

  if(0 == filtered.length) {
    return null;
  }

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

function SetupRequestShortLinkListener() {
  var requestShortLinkButton = document.querySelector('#rqslbtn');
  if (requestShortLinkButton) {
    requestShortLinkButton.title = 'Request short link';
    requestShortLinkButton.addEventListener('click', RequestShortLink);
  }
}

SetupRequestShortLinkListener();

function RemoveRequestShortLinkListener() {
  var requestShortLinkButton = document.querySelector('#rqslbtn');
  if (requestShortLinkButton) {
    requestShortLinkButton.removeEventListener('click', RequestShortLink);
  }
}

function SetWaitForResultListeners() {
  RunListenersSetup(OnWaitForResultKeyDown, OnRunClicked, OnWaitForResultRunClicked);
}

function CopyClick() { // eslint-disable-line no-unused-vars
  var textToCopy = document.getElementById('lnkurl');

  textToCopy.select();

  document.execCommand('copy');
}

function RequestShortLinkClick() { // eslint-disable-line no-unused-vars
  RequestShortLink();
}

// at least FireFox has a problem with just btoa with UTF-8 characters
function b64UTFEncode(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, v) {
    return String.fromCharCode(parseInt(v, 16));
  }));
}

function updateLinkToCompilerExplorer() {
  var cppstdparam = '-std=' + getCppStd().replace('cpp', 'c++');

  var libCpp = getUseLibStdCpp();
  if(null != libCpp) {
    cppstdparam += ' -stdlib=libc++';
  }

  var clientstate = {
    sessions: [{
      id: 1,
      language: 'c++',
      source: cppEditor.getValue(),
      compilers: [{
        id: 'clang_trunk',
        options: cppstdparam
      }]
    }]
  };

  var link = location.protocol + '//compiler-explorer.com/clientstate/' + b64UTFEncode(JSON.stringify(clientstate));
  var ceButton = document.getElementById('button-ce');
  ceButton.href = link;
}

document.querySelector('#button-ce').addEventListener('mousedown', function() {
  updateLinkToCompilerExplorer();
});

// From: https://github.com/mattgodbolt/compiler-explorer/pull/1823/files
function asciiEncodeJsonText(json) {
  return json.replace(/[\u007F-\uFFFF]/g, function(chr) {
    // json unicode escapes must always be 4 characters long, so pad with leading zeros
    return '\\u' + ('0000' + chr.charCodeAt(0).toString(16)).substr(-4);
  });
}

function updateLinkToQuickBench() {
  var quickBenchState = {
    text: cppEditor.getValue()
  };

  var link = 'http:' /*location.protocol*/ + '//quick-bench.com/#' + b64UTFEncode(asciiEncodeJsonText(JSON.stringify(
    quickBenchState)));
  var qbButton = document.getElementById('button-qb');
  qbButton.href = link;
}

document.querySelector('#button-qb').addEventListener('mousedown', function() {
  updateLinkToQuickBench();
});

function getLongLinkBase() {
  var cppStd = getCppStd();
  var insightsOptions = getInsightsOptions();
  var text = 'lnk?code=' + b64UTFEncode(cppEditor.getValue()) + '&insightsOptions=' +
    insightsOptions + '&std=' + cppStd + '&rev=' + DEFAULT_REV;

  return text;
}

document.querySelector('.button-create-link').addEventListener('click', function(event) {
  event.preventDefault();
  event.stopPropagation();
  var text = buildURL('/' + getLongLinkBase());

  var lnkElement = document.getElementById('lnkurl');
  lnkElement.value = text;

  var lnkDescElement = document.getElementById('lnkdesc');
  lnkDescElement.value = '';

  var element = document.getElementById('copyDropdown');
  element.classList.toggle('show');
});

document.querySelector('.button-more').addEventListener('click', function(event) {
  event.preventDefault();
  event.stopPropagation();

  var element = document.getElementById('moreDropdown');
  element.classList.toggle('show');
});

window.onclick = function(event) {
  if (!event.target.matches('.dropbtn') && !event.target.matches('.cpybtn') && !event.target.matches('#lnkurl') &&
    !event.target.matches('#lnkdesc') && !event.target.matches('#rqslbtn')) {

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

function buildURL(url) {
  return getURLBase() + url;
}

// Send a transformation request to the server
function Transform() { // eslint-disable-line no-unused-vars

  var request = new XMLHttpRequest();

  setLocalStorageItem('code', cppEditor.getValue());
  setLocalStorageItem('insightsOptions', getInsightsOptions());

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

  var url = buildURL('/api/v1/transform');

  request.open('POST', url, true);
  request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

  var data = {};

  data.insightsOptions = getInsightsOptions();
  data.code = cppEditor.getValue();

  SetWaitForResultListeners();
  request.send(JSON.stringify(data));
}

// Send a short link request to the server
function RequestShortLink() { // eslint-disable-line no-unused-vars

  var request = new XMLHttpRequest();

  request.onreadystatechange = function() {
    var linkField = document.getElementById('lnkurl');

    if (this.readyState == 4 && this.status == 200) {
      var response = JSON.parse(this.responseText);

      linkField.value = buildURL(response.shortlink);
    } else if (this.readyState == 4 && this.status != 200) {
      linkField.value = 'Sorry, your request failed';
    }

    SetupRequestShortLinkListener();
  };

  var linkField = document.getElementById('lnkurl');
  var linkDescField = document.getElementById('lnkdesc');
  var longLink = getLongLinkBase();

  // trim spaces and empty newlines from begin and end?

  linkField.value = 'Please wait...';

  var url = buildURL('/api/v1/getshortlink');

  request.open('POST', url, true);
  request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

  var data = {};

  data.longurl = longLink;
  data.code = b64UTFEncode(cppEditor.getValue());
  data.desc = b64UTFEncode(linkDescField.value);
  data.rev = DEFAULT_REV;
  data.std = getCppStd();
  data.options = getInsightsOptions();

  RemoveRequestShortLinkListener();

  request.send(JSON.stringify(data));
}
