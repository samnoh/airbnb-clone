import del from 'del';
import gulp from 'gulp';
import sass from 'gulp-sass';
import nodeSass from 'node-sass';
import postCss from 'gulp-postcss';
import autoprefixer from 'autoprefixer';
import tailwindcss from 'tailwindcss';
import csso from 'gulp-csso'; // minifiy CSS

const routes = {
    css: {
        src: 'assets/scss/main.scss',
        dest: 'static/css'
    }
};

const clean = () => del([routes.css.dest]);

const sassCompiler = () => {
    sass.compiler = nodeSass;
    const { src, dest } = routes.css;

    return gulp
        .src(src)
        .pipe(sass().on('error', sass.logError))
        .pipe(postCss([tailwindcss, autoprefixer]))
        .pipe(csso())
        .pipe(gulp.dest(dest));
};

export const css = gulp.series([clean, sassCompiler]);
