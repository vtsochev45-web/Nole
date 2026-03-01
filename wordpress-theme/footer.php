<footer id="site-footer">
    <?php if ( is_active_sidebar( 'footer-1' ) || is_active_sidebar( 'footer-2' ) || is_active_sidebar( 'footer-3' ) ) : ?>
        <div class="footer-widgets">
            <?php dynamic_sidebar( 'footer-1' ); ?>
            <?php dynamic_sidebar( 'footer-2' ); ?>
            <?php dynamic_sidebar( 'footer-3' ); ?>
        </div>
    <?php endif; ?>

    <?php
    if ( has_nav_menu( 'footer' ) ) {
        wp_nav_menu( array(
            'theme_location' => 'footer',
            'menu_id'        => 'footer-menu',
            'container'      => 'nav',
            'container_id'   => 'footer-navigation',
            'depth'          => 1,
        ) );
    }
    ?>

    <p class="site-info">
        🚜 <?php bloginfo( 'name' ); ?> &mdash;
        <?php
        printf(
            /* translators: %s: WordPress link */
            esc_html__( 'Proudly powered by %s', 'uk-farm-blog' ),
            '<a href="https://wordpress.org/">WordPress</a>'
        );
        ?>
    </p>
</footer>

<?php wp_footer(); ?>
</body>
</html>
