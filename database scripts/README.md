
## How to recreate the _Minimal+DB_ app database 
The scripts in this folder create the `my_local_db` PostgreSQL database with 2 schemas:
`minimaluser` and `namer`.

Use the scripts 
- `1-create-database.sql`
- `2-fill-database-minimalser.sql`
- `3-fill-database-namer.sql`

one after the other, using psql or pgAdmin query tool.

**NOTE**: make sure to select the 'my_local_db' database between step 1 and 2, so that the 
schemas will be created in the correct database :)

The `namer` schema contains some SVG templates which are used to create custom tiles, and a set 
of nouns which are used to create custom nicknames.