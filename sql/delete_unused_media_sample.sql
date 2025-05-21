DELETE FROM wp_posts
WHERE post_type = 'attachment'
AND guid LIKE '%wp-content/uploads/2023/08/beispiel.jpg';