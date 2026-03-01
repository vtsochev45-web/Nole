# UK Farm Blog – WordPress Theme

A custom WordPress theme that converts the **UK Farm Blog** Jekyll site into a
fully functional WordPress theme, preserving the original design (gradients,
card grid, navigation) and site structure.

## Theme Files

| File | Purpose |
|------|---------|
| `style.css` | Theme metadata + all CSS styles |
| `functions.php` | Theme setup, menus, widget areas, excerpt filters |
| `header.php` | Site header (gradient banner + sticky nav) |
| `footer.php` | Site footer with optional widget columns |
| `front-page.php` | Homepage: hero banner + category grid |
| `index.php` | Blog post list (fallback template) |
| `single.php` | Single post view |
| `page.php` | Static page view |
| `archive.php` | Category / tag / date archives |

## Installation

1. Copy the `wordpress-theme/` folder to `wp-content/themes/` on your WordPress
   server and rename it to `uk-farm-blog`.
2. In **Appearance → Themes** activate **UK Farm Blog**.
3. Go to **Appearance → Menus**, create a menu and assign it to **Primary Menu**.
   Add items for each category (Daily Brief, Weather, Grants, etc.).
4. *(Optional)* In **Appearance → Widgets** add widgets to the three footer columns.

## Importing Content

Use `wordpress-export.xml` (also included in `wordpress-migration.zip`) to
import all existing posts and pages:

1. **Tools → Import → WordPress → Run Importer**
2. Upload `wordpress-export.xml` and click **Upload file and import**.
3. Assign posts to an existing user and click **Submit**.

After import, WordPress will automatically create categories matching the
imported posts so the homepage category grid will be populated.
