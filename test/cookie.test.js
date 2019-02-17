require('jsdom-global')()

var fs = require('fs');
var vm = require('vm');
var path = './app/static/js/cookie.js';

var code = fs.readFileSync(path);
vm.runInThisContext(code);



var assert = require('assert');
describe('Cookie', function() {
    // banner gets inserted during window load
    window.onload();

    it('innerHTML contains cookie-law node', function(){
      assert.notEqual(document.getElementById('cookie-law'), null);
    });
      
    it('storageAllowed returns false at startup', function(){
      assert.equal(storageAllowed(), false);
    });

    it('User declines cookie -> cookieAccept(false)', function(){
      cookieAccept(false);

      assert.equal(storageAllowed(), false);
      assert.notEqual(document.getElementById('cookie-law'), null);
    });

    it('User accepts cookie -> cookieAccept(true)', function(){
      cookieAccept(true);
        
      assert.equal(storageAllowed(), true);
      assert.equal(document.getElementById('cookie-law'), null);
    });
  
});
