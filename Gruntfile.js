module.exports = function(grunt) {

  grunt.initConfig({
    svgmin: {
      options: {
        plugins: [{
            removeViewBox: false
          },
          {
            removeEmptyAttrs: false
          },
          {
            removeUselessStrokeAndFill: false
          },
        ]
      },
      dist: {
        files: {
          'dist/app/static/img/clb.svg': 'app/static/img/clb.svg',
          'dist/app/static/img/nav.svg': 'app/static/img/nav.svg',
        }
      }
    },

    cssmin: {
      target: {
        files: [{
            expand: true,
            cwd: 'app/static/css',
            src: ['*.css', '!*.min.css'],
            dest: 'dist/app/static/css',
            ext: '.min.css'
          },
          {
            'dist/app/static/cm/cm.min.css': ['app/static/cm/codemirror.css', 'app/static/cm/show-hint.css']
          },
        ]
      }
    },

    uglify: {
      options: {
        mangle: false
      },
      cmjs: {
        files: {
          'dist/app/static/cm/cm.min.js': ['app/static/cm/codemirror.js', 'app/static/cm/active-line.js',
            'app/static/cm/clike.js', 'app/static/cm/matchbrackets.js', 'app/static/cm/show-hint.js'
          ],
          'dist/app/static/js/main.min.js': ['app/static/js/main.js'],
          'dist/app/static/js/cookie.min.js': ['app/static/js/cookie.js'],
          'dist/app/static/ms/jquery-3.3.1.min.js': ['app/static/ms/jquery-3.3.1.js'],
          'dist/app/static/ms/multiple-select.min.js': ['app/static/ms/multiple-select.js']
        }
      }
    },

    'string-replace': {
      inline: {
        files: [{
            'dist/tmp/': 'app/templates/*.html'
          },
          {
            'dist/tmp/': 'app/static/*.html'
          },
        ],
        options: {
          replacements: [{
              pattern: /<!-- codemirror includes -->([\s\S]*?)<!-- codemirror includes end -->/g,
              replacement: '<link rel="stylesheet" href="/cm/cm.min.css"><script src="/cm/cm.min.js"></script>'
            },
            {
              pattern: /s\.css/ig,
              replacement: 's.min.css'
            },
            {
              pattern: /gh\.css/ig,
              replacement: 'gh.min.css'
            },
            {
              pattern: /main\.js/ig,
              replacement: 'main.min.js'
            },
            {
              pattern: /cookie\.js/ig,
              replacement: 'cookie.min.js'
            },
            {
              pattern: /jquery-3.3.1\.js/ig,
              replacement: 'jquery-3.3.1.min.js'
            },
            {
              pattern: /multiple-select\.js/ig,
              replacement: 'multiple-select.min.js'
            },
          ]
        }
      }
    },

    htmlmin: {
      dist: {
        options: {
          removeComments: true,
          collapseWhitespace: true,
          conservativeCollapse: true
        },
        files: [{
            expand: true,
            cwd: 'dist/tmp/app/templates/',
            src: ['*.html', '*.html'],
            dest: 'dist/app/templates/'
          },

          {
            expand: true,
            cwd: 'dist/tmp/app/static/',
            src: ['*.html', '*.html'],
            dest: 'dist/app/static/'
          },

          {
            expand: true,
            cwd: 'app/static/',
            src: ['*.xml', '*.xml'],
            dest: 'dist/app/static/'
          },
        ]
      },
    },

    copy: {
      main: {
        options: {
          mode: true,
        },
        files: [{
          expand: true,
          filter: 'isFile',
          src: [
            'app/*.py',
            'app/static/favicon.ico',
            'app/static/robots.txt',
          ],
          dest: 'dist/',
        }, ],
      },
    },

    pngmin: {
      compile: {
        options: {
          ext: '.png',
          quality: '80-90',
          force: true
        },
        files: [{
          expand: true,
          src: ['**/*.png'],
          cwd: 'app/static//',
          dest: 'dist/app/static/'
        }]
      }
    },

    eslint: {
      target: ['app/static/js/*.js']
    },
    jsbeautifier: {
      dist: {
        src: ['app/static/js/*.js', 'app/static/*.html', 'app/templates/*.html', 'app/static/css/*.css',
          'test/*.js'
        ],
        options: {
          config: ".jsbeautifyrc",
          mode: "VERIFY_ONLY"
        },
      },

      format: {
        src: ['app/static/js/*.js', 'app/static/*.html', 'app/templates/*.html', 'app/static/css/*.css',
          'test/*.js', 'Gruntfile.js'
        ],
        options: {
          config: ".jsbeautifyrc",
          mode: "VERIFY_AND_WRITE"
        },
      },
    },
    shell: {
      npm_test_mocha: {
        command: 'npm run test',
      }
    }
  });

  grunt.loadNpmTasks('grunt-svgmin');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify-es');
  grunt.loadNpmTasks('grunt-string-replace');
  grunt.loadNpmTasks('grunt-contrib-htmlmin');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-pngmin');
  grunt.loadNpmTasks('grunt-eslint');
  grunt.loadNpmTasks('grunt-jsbeautifier');
  grunt.loadNpmTasks('grunt-shell');

  grunt.registerTask('default', [ /*'jsbeautifier:dist',*/ 'eslint', /*'shell:npm_test_mocha',*/ 'svgmin', 'cssmin',
    'uglify',
    'string-replace', 'htmlmin', 'copy', 'pngmin'
  ]);
  grunt.registerTask('format', ['jsbeautifier:format']);
};
