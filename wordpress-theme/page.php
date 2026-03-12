<?php
/**
 * Static page template.
 *
 * @package uk-farm-blog
 */

get_header();
?>

<div id="content">
    <?php while ( have_posts() ) : the_post(); ?>

    <article id="page-<?php the_ID(); ?>" <?php post_class( 'content-page' ); ?>>

        <h1 class="entry-title"><?php the_title(); ?></h1>

        <div class="entry-content">
            <?php
            the_content();

            wp_link_pages( array(
                'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'uk-farm-blog' ),
                'after'  => '</div>',
            ) );
            ?>
        </div>

    </article>

    <?php endwhile; ?>
</div>

<?php get_footer(); ?>
