<?php
/**
 * Front-page template – mirrors the original site homepage.
 * Shows a hero banner with the latest post excerpt, then a grid of all
 * registered categories so visitors can jump straight to a topic.
 *
 * @package uk-farm-blog
 */

get_header();

// Fetch the single most-recent post for the hero banner.
$latest = new WP_Query( array(
    'posts_per_page' => 1,
    'post_status'    => 'publish',
) );
?>

<div id="content">

    <?php if ( $latest->have_posts() ) : $latest->the_post(); ?>
    <div class="hero-banner">
        <h2>📰 <?php esc_html_e( "Today's Farm Brief", 'uk-farm-blog' ); ?></h2>
        <h1><?php the_title(); ?></h1>
        <div><?php the_excerpt(); ?></div>
        <a href="<?php the_permalink(); ?>" class="btn">
            <?php esc_html_e( 'Read Full Brief →', 'uk-farm-blog' ); ?>
        </a>
    </div>
    <?php wp_reset_postdata(); endif; ?>

    <h2 class="sections-heading">📂 <?php esc_html_e( 'Browse Sections', 'uk-farm-blog' ); ?></h2>

    <div class="sections-grid">
        <?php
        $categories = get_categories( array(
            'orderby'    => 'name',
            'order'      => 'ASC',
            'hide_empty' => false,
        ) );

        if ( $categories ) :
            foreach ( $categories as $cat ) :
                $icon = ukfb_category_icon( $cat->slug );
        ?>
            <div class="section-card">
                <h3><?php echo esc_html( $icon . ' ' . $cat->name ); ?></h3>
                <?php if ( $cat->description ) : ?>
                    <p><?php echo esc_html( $cat->description ); ?></p>
                <?php endif; ?>
                <a href="<?php echo esc_url( get_category_link( $cat->term_id ) ); ?>" class="card-btn">
                    <?php esc_html_e( 'Explore →', 'uk-farm-blog' ); ?>
                </a>
            </div>
        <?php
            endforeach;
        else :
        ?>
            <p><?php esc_html_e( 'No categories found yet.', 'uk-farm-blog' ); ?></p>
        <?php endif; ?>
    </div>

</div>

<?php get_footer(); ?>

<?php
/**
 * Return an emoji icon for well-known category slugs.
 *
 * @param string $slug Category slug.
 * @return string Emoji or empty string.
 */
function ukfb_category_icon( $slug ) {
    $icons = array(
        'daily-brief'  => '🗞',
        'weather'      => '🌦',
        'grants'       => '💰',
        'markets'      => '📈',
        'equipment'    => '🚜',
        'livestock'    => '🐄',
        'crops'        => '🌾',
        'seasonal'     => '📅',
        'tools'        => '🧰',
        'community'    => '👥',
        'research'     => '🔬',
    );
    return isset( $icons[ $slug ] ) ? $icons[ $slug ] : '📌';
}
