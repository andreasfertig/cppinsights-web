require('jsdom-global')()

var app = require('../app/static/js/cookie.js');

// insert an additional cookie at front to test parsing multiple cookies
function createCookie(name, value) {
  var days = 365;
  var date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  var expires = '; expires=' + date.toGMTString();

  document.cookie = name + '=' + value + expires + '; path=/';
}

var assert = require('assert');
describe('Cookie', function() {
  createCookie('dummy', 'nothing');
  // banner gets inserted during window load
  app.onLoad();

  it('innerHTML contains cookie-law node', function() {
    assert.notEqual(document.getElementById('cookie-law'), null);
  });

  it('storageAllowed returns false at startup', function() {
    assert.equal(app.storageAllowed(), false);
  });

  it('User declines cookie -> cookieAccept(false)', function() {
    // user clicks decline
    app.cookieAccept(false);

    assert.equal(app.storageAllowed(), false);
    assert.equal(document.getElementById('cookie-law'), null);
  });

  it('User accepts cookie -> cookieAccept(true)', function() {
    // simulate reload
    this.jsdom = require('jsdom-global')()
    app.onLoad();

    // user clicks accept
    app.cookieAccept(true);

    assert.equal(app.storageAllowed(), true);
    assert.equal(document.getElementById('cookie-law'), null);
  });

  it('ensure no cookie banner is shown', function() {
    // simulate reload
    var cookie = document.cookie; // keep existing cookies
    this.jsdom = require('jsdom-global')() // reset the DOM
    document.cookie = cookie; // restore existing cookies
    app.onLoad(); // reload

    assert.equal(document.getElementById('cookie-law'), null);
  });

});
