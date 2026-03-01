<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header id="site-header">
    <a class="site-title" href="<?php echo esc_url( home_url( '/' ) ); ?>">
        🌾 <?php bloginfo( 'name' ); ?>
    </a>
    <p class="site-description"><?php bloginfo( 'description' ); ?></p>
</header>

<nav id="site-navigation" aria-label="<?php esc_attr_e( 'Primary menu', 'uk-farm-blog' ); ?>">
    <?php
    wp_nav_menu( array(
        'theme_location' => 'primary',
        'menu_id'        => 'primary-menu',
        'container'      => false,
        'fallback_cb'    => 'ukfb_fallback_menu',
    ) );
    ?>
</nav>

<?php
/**
 * Fallback navigation – displayed when no menu has been assigned to the
 * "Primary Menu" location.  Shows a list of the site's top-level pages.
 */
function ukfb_fallback_menu() {
    echo '<ul id="primary-menu">';
    echo '<li><a href="' . esc_url( home_url( '/' ) ) . '">🏠 ' . esc_html__( 'Home', 'uk-farm-blog' ) . '</a></li>';
    wp_list_pages( array(
        'title_li'    => '',
        'depth'       => 1,
        'sort_column' => 'menu_order',
    ) );
    echo '</ul>';
}
?>
