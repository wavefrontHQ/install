create database docker_test;
GRANT ALL PRIVILEGES 
       ON docker_test.* 
       TO 'docker'@'localhost'
       IDENTIFIED BY 'docker' 
       WITH GRANT OPTION;

