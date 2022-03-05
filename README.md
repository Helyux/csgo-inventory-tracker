      ___ ___  __ _  ___                        
     / __/ __|/ _` |/ _ \                       
    | (__\__ | (_| | (_) |                      
     \___|___/\__, |\___/   _                   
    (_)_ ____ |___/__ _ __ | |_ ___  _ __ _   _ 
    | | '_ \ \ / / _ | '_ \| __/ _ \| '__| | | |
    | | | | \ V |  __| | | | || (_) | |  | |_| |
    |_|_| |_|\_/ \___|_|_|_|\__\___/|_|   \__, |
    | |_ _ __ __ _  ___| | _____ _ __     |___/ 
    | __| '__/ _` |/ __| |/ / _ | '__|          
    | |_| | | (_| | (__|   |  __| |             
     \__|_|  \__,_|\___|_|\_\___|_|             

## Prerequisites :airplane:
- Have a MySQL Server

## Installation :zap:
1. `git clone https://github.com/Helyux/csgo-inventory-tracker`
2. `pipenv install`
3. `pipenv run python main.py`

## SQL Configuration :wrench:
1. Login as root\
`mysql -u root -p`
<br/>

3. Create a SQL User\
`CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';`
<br/>

4. Setup a SQL Database\
`CREATE DATABASE IF NOT EXISTS databasename;`
<br/>

5. Grant all rights for the created user to the created database\
`GRANT ALL PRIVILEGES ON databasename.* TO 'username'@'localhost';`
<br/>

6. Flush privileges\
`FLUSH PRIVILEGES;`

## Configuration  :clipboard:
1. Make a copy of template.toml named prod.toml in the base directory
2. Fill in the variables in prod.toml