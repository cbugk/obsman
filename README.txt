%%%%%%%%%%% START

PLEASE, do not change file/folder names in this folder. Main folder's name
can be edited, however.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

After installing "docker" and "docker-compose", run command within this folder

For initial/update creation of image:
	docker-compose up -d --build

After image is created can start almost instantly by:
	docker-compose up -d

It should take couple of minutes before building the image (compiles python
from source).
Thereafter you can use docker commands to "stop", "start", "kill"
projects container.

Default username and password are in ./node-red-config/settings.js file:

user: aukr
pass: AUKRpassword

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

For Node-RED security details see: http://www.steves-internet-guide.com/securing-node-red-ssl/

basically use bcrypt hashes of passwords in settings.js file (within ./node-red-config)
You can install "node-red-admin" program on your host and run:
	node-red-admin hash-pw
Provide a password and copy/paste its output into setting.js file.
Note that: each passwords need to be rehashed (even if they are the same)
because, bcrypt produces different hashes each-time.

Or you can use another online/offline bcrypt hasher solution if you desire.

For TLS place your .pem files in ./node-red-config/nodecerts with names:
	node-cert.pem
	node-crs.pem
	node-key.pem

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Projects uses Node-RED for frontend and python3.7 for backend.
There is a single Node-RED container with python 3.7 installed from source
(as of now nodered/node-red-docker image has python3.5, f-strings are not
supported in that version).

Read docker-compose.yml and Dockerfile for further details.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Informative-links folder is only for referencing certian topics' research on
the internet. For the maintainer, they might be trivial or helpful; still
better to have those txt files around.

%%%%%%%%%%% END
