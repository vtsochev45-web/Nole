<?php
/**
 * Archive template – used for category, tag, date and author archives.
 *
 * @package uk-farm-blog
 */

get_header();
?>

<div id="content">

    <header class="archive-header">
        <?php
        the_archive_title( '<h1 class="archive-title">', '</h1>' );
        the_archive_description( '<p class="archive-description">', '</p>' );
        ?>
    </header>

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
            <p><?php esc_html_e( 'No posts found in this section yet.', 'uk-farm-blog' ); ?></p>
        </div>

    <?php endif; ?>

</div>

<?php get_footer(); ?>
