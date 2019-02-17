/* C++ Insights Web, copyright (c) by Andreas Fertig
   Distributed under an MIT license. See /LICENSE */

var cookieName = 'complianceCookie';

function createBanner() {
  var bodytag = document.getElementsByTagName('body')[0];
  var div = document.createElement('div');
  div.setAttribute('id', 'cookie-law');
  div.innerHTML =
    '<span>This website uses cookies. See <a href="/cookie-policy.html" rel="nofollow" title="Privacy &amp; Cookies Policy">cookie policy</a> for more information.</span> <div class="accept-decline"><div class="btn-decline"><a class="decline-cookie-banner" href="javascript:void(0);" onclick="cookieAccept(false);"><span>Decline</span></a></div><div class="btn-accept"><a class="close-cookie-banner" href="javascript:void(0);" onclick="cookieAccept(true);"><span>Accept</span></a></div></div>';

  bodytag.insertBefore(div, bodytag.firstChild);
}

function createCookie(name, value) {
  var days = 365;
  var date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  var expires = '; expires=' + date.toGMTString();

  document.cookie = name + '=' + value + expires + '; path=/';
}

function checkCookie(name) {
  var nameEQ = name + '=';
  var ca = document.cookie.split(';');

  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1, c.length);
    }

    if (c.indexOf(nameEQ) == 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }

  return null;
}

function cookieAccept(b) { // eslint-disable-line no-unused-vars
  createCookie(cookieName, b);

  var element = document.getElementById('cookie-law');
  element.parentNode.removeChild(element);
}

function storageAllowed() { // eslint-disable-line no-unused-vars
  return ('true' == checkCookie(cookieName));
}

window.onload = function() {
  if (!checkCookie(cookieName)) {
    createBanner();
  }
};
