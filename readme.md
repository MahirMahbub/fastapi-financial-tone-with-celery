# Code:

### Q) Where is the codes?
inside **\backend** folder
**app**
**db**
**db_merge_scripts**
**db_migrations**

### Q) Where is the .env?
inside **\backend** folder

# Run The Project in Docker:
### Q) What need to install?
Python 3.8.5
https://www.python.org/downloads/release/python-385/
install if for all users
https://www.youtube.com/watch?v=zYdHr-LxsJ0

Docker Desktop Community 3.0.4
Docker 20.10.2

### Q) What's the command to start the application locally?
inside **\backend** folder
(docker command) `docker-compose up`
Check **docker-compose.yml** file

### Add Model data from https://huggingface.co/yiyanghkust/finbert-tone/tree/main to workers/model/fine-tone


### Internet Connection is necessary

### For sample output see sample_result.json

[comment]: <> (# Application Page:)

[comment]: <> (### Hosted at Docker)

[comment]: <> ([http://localhost:7003/docs]&#40;http://localhost:7003/docs&#41;)


[comment]: <> (### Dev)


[comment]: <> (pip install -r requirements.txt)

[comment]: <> (pip list)



[comment]: <> (docker-compose build)

[comment]: <> (docker-compose up)

[comment]: <> (docker-compose up -d)
 
[comment]: <> (for debug run)

[comment]: <> (python debug.py)


[comment]: <> (Remove everything from docker)

[comment]: <> (https://stackoverflow.com/questions/44785585/how-to-delete-all-local-docker-images)

[comment]: <> (docker system prune -a --volumes)


[comment]: <> (DB credentials:)

[comment]: <> (    add new server)

[comment]: <> (    host name: db_campaign)

[comment]: <> (    port: 54320)

[comment]: <> (    db: postgres)

[comment]: <> (    user: admin)

[comment]: <> (    password: secret)

[comment]: <> (API: )

[comment]: <> (http://localhost:7003/docs)


[comment]: <> (DB:)

[comment]: <> (pool_size and max_overflow https://stackoverflow.com/a/9999411)


[comment]: <> (Update Db and insert master data:)

[comment]: <> (python run_db.py auto)

[comment]: <> (python run_db.py data)

[comment]: <> (### The parsing of data and  loading of data to the database will happen while starting the fastapi server when "data_loader" table will have "true" status for "Movie Data Loading")

[comment]: <> (For manual upload of data with parsing run in docker terminal:)

[comment]: <> (python parse.py )

[comment]: <> (NB: ** manual parsing is not included optional "phrase 4", "phrase 4" only runs at startup.)

[comment]: <> (When the database is ready with the parsed data, "data_loader" table will have "false" status for "Movie Data Loading" so that the data parsing & loading never happens again.)

[comment]: <> (### Phrase 4 will run while starting the fastapi server when "data_loader" table will have "true" status for "Movie Rating Loading")

[comment]: <> (change the db value for enable/disable phrase 4. )

[comment]: <> (did not exposed an api for "data_loader" table's status change, because of maintaining exact api deliverables by the assignment requirements.)

[comment]: <> (total number of movies found in third party csv that has been provided: 475)

[comment]: <> (# API endpoints)

[comment]: <> (http://localhost:7003/movies?count={}&page={})

[comment]: <> (http://localhost:7003/movie/{})

[comment]: <> (For Source Code for Data Parsing and Data Upload to database, see:)

[comment]: <> (app/custom_classes/*)

[comment]: <> (Used Chain of Responsibility, Singletone, Repository.)

[comment]: <> (For API details please see: https://github.com/MahirMahbub/Wiki_Movies/blob/master/API%20Doc.pdf)


