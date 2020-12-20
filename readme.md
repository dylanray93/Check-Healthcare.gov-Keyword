# Healthcare.gov Keyword Check Airflow Test

### This ETL process pulls down a list of all Healthcare.gov webpages, checks that the downloaded data meets expected criteria, then checks whether a keyword is present in the webpages.

ETL Steps:
1. Ping Healthcare.gov, download webpage names as json file, convert to dataframe, save to Docker container.
2. Open saved file, check against pre-configured expectations file. This step fails if the expectations do not pass the great_expectations requirements.
3. Open saved file, search for keyword. This step fails if the keyword **is found** in one of the webpage names.
