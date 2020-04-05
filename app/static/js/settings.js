/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */

/* global getLocalStorageItem, setLocalStorageItem, storageAllowed, createComplianceCookie */

function toggleButton(divId, show) { // eslint-disable-line no-unused-vars
  var value = 'initial';

  if (!show) {
    value = 'none';

  }

  setLocalStorageItem(divId, value);
}

function applyTheme(dark) {
  if (dark) {
    document.body.setAttribute('data-theme', 'dark');
  } else {
    document.body.removeAttribute('data-theme');
  }
}

function toggleTheme(dark) {
  applyTheme(dark);

  setLocalStorageItem('dark-theme', dark);
}

function adjustTheme() {
  applyTheme(getLocalStorageItem('dark-theme', false));
}

var settingsConfiguration = [
  // name, get-function, set-function, requires cookies
  ['Accept cookies', storageAllowed, createComplianceCookie, false],
  ['Show community events', function() {
    return 'initial' === getLocalStorageItem('banner', 'initial');
  }, function(b) {
    toggleButton('banner', b);
  }, true],
  ['Minimize console', function() {
    return getLocalStorageItem('stderr-div', false);
  }, function(b) {
    setLocalStorageItem('stderr-div', !b);
  }, true],
  ['Use dark theme', function() {
    return getLocalStorageItem('dark-theme', false);
  }, toggleTheme, true],
];

// settings
function SettingsHandler() {
  var settingsList = document.getElementById('settings');
  if (null == settingsList) {
    // settings page not loaded
    return;
  }

  while (settingsList.firstChild) {
    settingsList.removeChild(settingsList.firstChild);
  }

  function createSetting(item, index) {
    var li = document.createElement('li');

    var input = document.createElement('input');
    input.setAttribute('type', 'checkbox');
    var label = document.createElement('label');
    var text = document.createTextNode(item[0]);
    label.appendChild(text);

    input.checked = item[1]();

    // disable cookie related items, if cookies are not allowed
    if ((item[3] == true) && !storageAllowed()) {
      input.disabled = true;
    }

    li.appendChild(input);
    li.appendChild(label);

    input.addEventListener('change', (event) => {
      item[2](event.target.checked);

      if (0 == index) { // assuming that cookies are at pos 0
        // reload the entire list to prevent changes to cookie related items
        SettingsHandler();
      }
    });

    settingsList.appendChild(li);
  }

  settingsConfiguration.forEach(createSetting);

}

SettingsHandler();

// set to dark if enabled
adjustTheme();
