# Update on Apr 17 

## 1. Project remake
The entire backend architecture has been redeveloped, from a traditonal flask into a FastAPI + MySQL, tested with Postman

## 2. Tech Stack
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic v2
- Postman

## 3. Project index:
```bash
PS C:\Users\a7846\Desktop\32933\32933-project-match\backend> ls -R

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2025/4/17     0:54                __pycache__
d----           2025/4/17     0:12                crud
d----           2025/4/17     0:12                models
d----           2025/4/17     0:11                routers
d----           2025/4/17     0:14                schemas
d----           2025/4/16    21:19                services
d----           2025/4/17     1:44                tests
d----           2025/4/16    21:19                utils
-a---           2025/4/16    21:18              0 config.py
-a---           2025/4/17     0:54            472 database.py
-a---           2025/4/16    22:28            298 main.py
-a---           2025/4/17     1:39              0 readme.md
-a---           2025/4/16    21:18              0 requirements.txt

```
## 4. Today's milestone: Register function is finished:
    User need to provide first name, last name, email and password to register
    Email has regex to make sure it is a UTS format email
    User would be automatically gave a user group identifier to identify if they are students or supervisors by juding if their email contains a 'student' after '@'
    If there are repeat names, they would get a new email by add a '-number', like a.b-1@uts.edu.au
    User would be assigned with a id as primary key

## 5.  testing steps and interface guide:
    use uvicorn main:app --reload to launch the server

    Set method to POST in postman, add a raw body and a header application/json
    Successfully registered
    ![Postman Register Successfully](tests/register%20success%20in%20postman.png)

    Data successfully write in MySQL:
    ![Workbench Query](tests/register%20result%20found%20in%20MySQL.png)

