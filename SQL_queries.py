__author__ = '130315'

# Query to list Countries_names order by position
query = ("SELECT Countries.name, country_ratings.position FROM Countries, country_ratings WHERE Countries.id = country_ratings.id_country ORDER BY country_ratings.position")
SELECT Countries.name, country_ratings.position FROM Countries, country_ratings WHERE Countries.id = country_ratings.id_country ORDER BY country_ratings.position