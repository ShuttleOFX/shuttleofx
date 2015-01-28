'use strict';

module.exports = function (grunt) {

  // Load grunt tasks automatically, when needed
  require('jit-grunt')(grunt, {
    express: 'grunt-express-server',
    useminPrepare: 'grunt-usemin'
  });

  require('time-grunt')(grunt);

  grunt.initConfig({

    pkg: grunt.file.readJSON('package.json'),
    project: {
      static: 'static_tmp',
      static_dist: 'static_dist',
      static_tmp: 'static'
    },


    express: {
      options: {
        port: process.env.PORT || 9000
      },
    },
    open: {
      server: {
        url: 'http://localhost:<%= express.options.port %>'
      }
    },


    watch: {
      
      script: {
        files: [
          '<%=  project.static %>/scripts/*.js',
          '<%=  project.static %>/scripts/**/*.js',

        ],
        tasks: ['newer:jshint:all', 'concat:scripts']
      },

      less: {
        files: [
          '<%= project.static %>/styles/**/*.less',
          '<%= project.static %>/styles/*.less'],

        tasks: ['less', 'autoprefixer']
      },

      gruntfile: {
        files: ['Gruntfile.js']
      },

      livereload: {
        files: [
          '<%= project.static_tmp %>/styles/**/*.css',
          '<%= project.static_tmp %>/styles/*.css',
          '<%= project.static_tmp %>/styles/vendor/*.css',


          '/templates/*.html',

          '<%= project.static_tmp %>/scripts/**/*.js',
          '<%= project.static_tmp %>/scripts/*.js',

          '<%= project.static %>/images/{,*//*}*.{png,jpg,jpeg,gif,webp,svg}',
          '<%= project.static %>/images/**/{,*//*}*.{png,jpg,jpeg,gif,webp,svg}'

        ],
        options: {
          livereload: true
        }
      },

    },

    concat :{
      scripts : {
        src: [
          '<%=  project.static %>/scripts/*.js',
        ],
        dest: '<%= project.static_tmp %>/scripts/combined-scripts.js'
      },
      styles : {
        src: [
          '<%=  project.static_tmp %>/styles/main.css'
        ],
        dest: '<%= project.static_tmp %>/styles/main.css'
      }
    },


    // Make sure code styles are up to par and there are no obvious mistakes
    jshint: {
      options: {
        jshintrc: '<%= project.static %>/.jshintrc',
        reporter: require('jshint-stylish'),
        force : true
      },
      
      all: [
        '<%= project.static %>/scripts/**/*.js',
        '<%= project.static %>/scripts/*.js',
      ]
    },

    // Empties folders to start fresh
    clean: {
      static_dist: {
        files: [{
          dot: true,
          src: [
            '<%= project.static_dist %>/*',
            '!<%= project.static_dist %>/.git*',
            '!<%= project.static_dist %>/Procfile'
          ]
        }]
      },
      server: '<%= project.static_tmp %>'
    },

    // Add vendor prefixed styles
    autoprefixer: {
      options: {
        browsers: ['last 1 version']
      },
      static_dist: {
        files: [{
          expand: true,
          cwd: '<%= project.static_tmp %>/styles/',
          src: '{,*/}*.css',
          dest: '<%= project.static_tmp %>/styles/'
        }]
      }
    },

    // Reads HTML for usemin blocks to enable smart builds that automatically
    // concat, minify and revision files. Creates configurations in memory so
    // additional tasks can operate on them
    useminPrepare: {
      html: ['templates/index.html'],
      options: {
        dest: 'templates/'
      }
    },

    // Performs rewrites based on rev and the useminPrepare configuration
    usemin: {
      html: ['templates/{,*/}*.html'],
      css: ['<%= project.static_dist %>/styles/{,*/}*.css'],
      js: ['<%= project.static_dist %>/scripts/{,*/}*.js'],
      options: {
        assetsDirs: [
          '<%= project.static_dist %>'
        ],
        // This is so we update image references in our ng-templates
        patterns: {
          js: [
            [/(assets\/images\/.*?\.(?:gif|jpeg|jpg|png|webp|svg))/gm, 'Update the JS to reference our revved images']
          ]
        }
      }
    },

    // Copies remaining files to places other tasks can use
    copy: {
      static_dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= project.static_tmp %>/',
          dest: '<%= project.static_dist %>/',
          src: [
            '*.{ico,png,txt}',
            'images/{,*/}*.{webp}',
            'images/*.jpg',
            'images/*.png',
            'images/*.gif',
            'images/**/*.jpg',
            'images/**/*.png',
            'images/**/*.svg',

            'fonts/**/*',
            'styles/*.css',
            'styles/vendor/*.css',
            'styles/vendor/*.map',

            'scripts/*.js',
            'scripts/vendor/*.js',


          ]
        }, {
          expand: true,
          cwd: '<%= project.static_tmp %>/images/',
          dest: '<%= project.static_dist %>/images/',
          src: ['generated/*']
        }]
      },
      

      static_tmp: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= project.static %>/',
          dest: '<%= project.static_tmp %>/',
          src: [
            'images/{,*/}*.{webp}',
            'images/*.jpg',
            'images/*.png',
            'images/*.gif',
            'images/**/*.jpg',
            'images/**/*.png',
            'images/**/*.svg',

            'fonts/**/*',
            'styles/vendor/*.css',
            'styles/vendor/*.map',
            
            'scripts/vendor/*.js',
            'scripts/*.js'




          ]
        }]
      }

    },

    // Run some tasks in parallel to speed up the build process
    concurrent: {
      server: [
        'less',
        'concat:scripts'

      ],
      test: [
        'less',
        'concat:scripts'

      ],
      static_dist: [
        'less',
        'concat:scripts'

      ]
    },


    // Compiles Less to CSS
    less: {
      options: {
        paths: [
          '<%= project.static %>/styles/'
        ]
      },
      server: {
        files: {
          '<%= project.static_tmp %>/styles/main.css' : '<%= project.static %>/styles/main.less'
        }
      },
    },
  });

  // Used for delaying livereload until after server has restarted
  grunt.registerTask('wait', function () {
    grunt.log.ok('Waiting for server reload...');

    var done = this.async();

    setTimeout(function () {
      grunt.log.writeln('Done waiting!');
      done();
    }, 1500);
  });

  grunt.registerTask('express-keepalive', 'Keep grunt running', function() {
    this.async();
  });

  grunt.registerTask('serve', function (target) {
    if (target === 'static_dist') {
      return grunt.task.run(['build', 'env:all', 'env:prod', 'wait', 'open']);
    }

    grunt.task.run([
      'clean:server',
      'concurrent:server',
      'autoprefixer',
      'copy:static_tmp',
      'wait',
      'open',
      'watch'
    ]);
  });

  grunt.registerTask('server', function () {
    grunt.log.warn('The `server` task has been deprecated. Use `grunt serve` to start a server.');
    grunt.task.run(['serve']);
  });


  grunt.registerTask('build', [
    'clean:static_dist',
    'concurrent:static_dist',
    'useminPrepare',
    'autoprefixer',
    'copy:static_dist',
    // 'cssmin',
    'usemin'
  ]);

  grunt.registerTask('default', [
    'newer:jshint',
    'test',
    'build'
  ]);
};
