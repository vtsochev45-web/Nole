<?php
/**
 * The main template – blog post list.
 * WordPress falls back to this file when no more specific template matches.
 *
 * @package uk-farm-blog
 */

get_header();
?>

<div id="content">

    <?php if ( is_home() && ! is_front_page() ) : ?>
        <header class="archive-header">
            <h1 class="archive-title">
                <?php esc_html_e( '📝 Latest Posts', 'uk-farm-blog' ); ?>
            </h1>
        </header>
    <?php endif; ?>

    <?php if ( have_posts() ) : ?>

        <ul class="posts-list">
        <?php while ( have_posts() ) : the_post(); ?>

            <li class="post-card">
                <h2 class="entry-title">
                    <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                </h2>
                <p class="entry-meta">
                    📅 <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>">
                        <?php echo esc_html( get_the_date() ); ?>
                    </time>
                    &nbsp;|&nbsp;
                    🗂 <?php the_category( ', ' ); ?>
                </p>
                <div class="entry-summary">
                    <?php the_excerpt(); ?>
                </div>
                <a href="<?php the_permalink(); ?>" class="read-more">
                    <?php esc_html_e( 'Read More →', 'uk-farm-blog' ); ?>
                </a>
            </li>

        <?php endwhile; ?>
        </ul>

        <div class="pagination">
            <?php
            the_posts_pagination( array(
                'prev_text' => '&laquo; ' . esc_html__( 'Previous', 'uk-farm-blog' ),
                'next_text' => esc_html__( 'Next', 'uk-farm-blog' ) . ' &raquo;',
            ) );
            ?>
        </div>

    <?php else : ?>

        <div class="no-results">
            <h2><?php esc_html_e( 'Nothing Found', 'uk-farm-blog' ); ?></h2>
            <p><?php esc_html_e( 'No posts were found. Check back soon for new farming updates!', 'uk-farm-blog' ); ?></p>
        </div>

    <?php endif; ?>

</div>

<?php get_footer(); ?>
