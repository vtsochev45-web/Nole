<?php
/**
 * UK Farm Blog – Theme Functions
 *
 * @package uk-farm-blog
 */

// Exit if accessed directly.
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Theme setup: register menus, add theme support.
 */
function ukfb_setup() {
    // Make theme available for translation.
    load_theme_textdomain( 'uk-farm-blog', get_template_directory() . '/languages' );

    // Add support for automatic feed links.
    add_theme_support( 'automatic-feed-links' );

    // Let WordPress manage the document title.
    add_theme_support( 'title-tag' );

    // Enable Post Thumbnails.
    add_theme_support( 'post-thumbnails' );

    // Support for HTML5 markup.
    add_theme_support( 'html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ) );

    // Register primary navigation menu.
    register_nav_menus( array(
        'primary' => esc_html__( 'Primary Menu', 'uk-farm-blog' ),
        'footer'  => esc_html__( 'Footer Menu',  'uk-farm-blog' ),
    ) );
}
add_action( 'after_setup_theme', 'ukfb_setup' );

/**
 * Enqueue theme stylesheet.
 */
function ukfb_enqueue_scripts() {
    wp_enqueue_style(
        'uk-farm-blog-style',
        get_stylesheet_uri(),
        array(),
        wp_get_theme()->get( 'Version' )
    );
}
add_action( 'wp_enqueue_scripts', 'ukfb_enqueue_scripts' );

/**
 * Register widget areas.
 */
function ukfb_widgets_init() {
    register_sidebar( array(
        'name'          => esc_html__( 'Footer Column 1', 'uk-farm-blog' ),
        'id'            => 'footer-1',
        'description'   => esc_html__( 'First footer widget area.', 'uk-farm-blog' ),
        'before_widget' => '<div class="footer-col">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4>',
        'after_title'   => '</h4>',
    ) );

    register_sidebar( array(
        'name'          => esc_html__( 'Footer Column 2', 'uk-farm-blog' ),
        'id'            => 'footer-2',
        'description'   => esc_html__( 'Second footer widget area.', 'uk-farm-blog' ),
        'before_widget' => '<div class="footer-col">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4>',
        'after_title'   => '</h4>',
    ) );

    register_sidebar( array(
        'name'          => esc_html__( 'Footer Column 3', 'uk-farm-blog' ),
        'id'            => 'footer-3',
        'description'   => esc_html__( 'Third footer widget area.', 'uk-farm-blog' ),
        'before_widget' => '<div class="footer-col">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4>',
        'after_title'   => '</h4>',
    ) );
}
add_action( 'widgets_init', 'ukfb_widgets_init' );

/**
 * Customise the excerpt length.
 */
function ukfb_excerpt_length( $length ) {
    return 40;
}
add_filter( 'excerpt_length', 'ukfb_excerpt_length', 999 );

/**
 * Replace the default excerpt suffix with a nicer ellipsis.
 */
function ukfb_excerpt_more( $more ) {
    return '&hellip;';
}
add_filter( 'excerpt_more', 'ukfb_excerpt_more' );
