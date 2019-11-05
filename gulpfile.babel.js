import gulp from 'gulp';
import sass from 'gulp-sass';
import autoprefixer from 'autoprefixer';
import postCss from 'gulp-postcss';
import csso from 'gulp-csso';
import nodeSass from 'node-sass';
import tailwindcss from 'tailwindcss';

sass.compiler = nodeSass;

const css = () =>
    gulp
        .src('assets/scss/main.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(postCss([tailwindcss, autoprefixer]))
        .pipe(csso()) // minifiy CSS
        .pipe(gulp.dest('static/css'));

export default css;
