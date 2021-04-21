## deploy on your machine with python and postgres.

`app.py` is a python programme with  a command line interface allowing the user to launch the download of resources
 in companies house API and insert them automatically in a postresql database.  

#### configuration:

##### the interpreter
- clone the repository to a local folder. 
- `cd` into it.
- create a new virtual environment with **python 3.6+**.
- install the requirements.  

##### the database

- you need to have postgres installed of course, and you need to have created a target
  database where the tables will be created and data inserted. 
- make sure that the `configs/database.ini` file is filled with the following:  
> host=[choose host - you probably want to just use `localhost`]  
database=[choose db name]   
user=[choose user name]    
password=[choose password]   

- make sure that you choose the `DB_SCHEMA` in `configs/pg_constants.py`. The schema will be created if it doesn't exist 
and the connection object will be set to the schema.
  
- add the key companies house gave you in the `api_key` file. 

- should companies house have granted you more than the 500 query per 5 min (say, 1000), edit this number in the `utils/
  extract/api_functions.py` constant `CALLS`.
  
- run the programme from within the environment:

```textmate
(venv) prompt$ python3 <path/to/prgoramme> <path/to/file_with_ids> <optional flags>
(venv) prompt$ python3 app.py file.txt --psc
```

##### flags

###### for the input data 
- The url_id for the following flags is the uniquely identifiable company_code. Example: **OC362072**  
`--psc`: for person of significant interest.   
`--ol`: for officers list.   
`--cp`: for company profile.  
`--fh`: for filing history.  
`--ch`: for company charges.  


- The url_id for the following flag is companies house officer_id. Example: **RY_RJjPR0uGi0pOJuJi7dyCCTzo**  
`--al`: for appointment list.
  

##### errors

- the file extensions for the file containing the urls can be either `txt` or `csv`. Relatively messy files can be parsed, 
 ideally write an url_id per line. No need to end the line with a comma. 
 
- if you try to form URI for the appointments resource using a company code or vice versa, an officer_id for a company 
resource, the programme will throw an error at you.

- flags which use the same type of url_id can be cumulative, conversely they collide and an error will be thrown.  
legal: `python3 pipeline.py <url_file_containing_company_codes.csv> --psc --ol --cp`  
illegal: `python3 pipeline.py <url_file_containing_company_codes.csv> --al --cp`
  
##### goodies

There a few nice features in the programme:

- you can rerun the pipeline with the same company or officer ids without risk of uploading 
the same data several times as data matching that id in the root table is first deleted on cascade.
  
- names and country names are normalised, so it's possible to easily dedupe using group by statements.
  
- nationality is originally present in the data as string "uk, Italian". The pipeline splits, normalises
and stacks the nationalities in a separate table. 
  
- address columns are further cleaned: postal code, locality, legal_authority and place_registered. This should
help to dedupe addresses. 