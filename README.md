launches a REST service on a uWSGI/NGINX server to add records to a mongodb (included in docker-compose.yml)

Since I need to take my weight, blood pressure, and blood sugar on a regular basis I thought it'd be fun to store all that data in a database and do normal database-y things with it.

datbase = 'healthStats
collections = ['sugar', 'weight', 'pressure']

TODO:
- better query
- config file for various settings
- return SVG generated from date range query
- accompanying webUI front end (what for entering data, queries, and showing SVG results)
