<?php
/**
 * Single post template.
 *
 * @package uk-farm-blog
 */

get_header();
?>

<div id="content">
    <?php while ( have_posts() ) : the_post(); ?>

    <article id="post-<?php the_ID(); ?>" <?php post_class( 'content-page' ); ?>>

        <h1 class="entry-title"><?php the_title(); ?></h1>

        <p class="entry-meta">
            📅 <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>">
                <?php echo esc_html( get_the_date() ); ?>
            </time>
            <?php if ( get_the_category_list( ', ' ) ) : ?>
                &nbsp;|&nbsp; 🗂 <?php the_category( ', ' ); ?>
            <?php endif; ?>
            <?php
            $tags = get_the_tag_list( ' | 🏷 ', ', ' );
            if ( $tags ) {
                echo wp_kses_post( $tags );
            }
            ?>
        </p>

        <div class="entry-content">
            <?php
            the_content(
                sprintf(
                    '<span class="screen-reader-text">%1$s</span>',
                    /* translators: %s: Name of current post */
                    sprintf( esc_html__( 'Continue reading %s', 'uk-farm-blog' ), get_the_title() )
                )
            );

            wp_link_pages( array(
                'before'      => '<div class="page-links">' . esc_html__( 'Pages:', 'uk-farm-blog' ),
                'after'       => '</div>',
            ) );
            ?>
        </div>

    </article>

    <nav class="post-navigation">
        <?php
        $prev = get_previous_post();
        if ( $prev ) {
            echo '<a href="' . esc_url( get_permalink( $prev ) ) . '">← ' . esc_html( get_the_title( $prev ) ) . '</a>';
        }
        $next = get_next_post();
        if ( $next ) {
            echo '<a href="' . esc_url( get_permalink( $next ) ) . '">' . esc_html( get_the_title( $next ) ) . ' →</a>';
        }
        ?>
    </nav>

    <?php endwhile; ?>
</div>

<?php get_footer(); ?>
