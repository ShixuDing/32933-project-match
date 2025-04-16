# Update on Apr 17 2AM

# 1. The entire backend architecture has been redeveloped, from a traditonal flask into a FastAPI + MySQL, tested with Postman

## 2. Tech Stack
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic v2
- Postman

## 3. Project index:
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

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\crud

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2025/4/17     1:29                __pycache__
-a---           2025/4/17     1:29           1658 user.py

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\crud\__pycache__

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     1:29           2601 user.cpython-313.pyc

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\models

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2025/4/17     1:33                __pycache__
-a---           2025/4/17     1:32            709 project.py
-a---           2025/4/17     0:55             97 student.py
-a---           2025/4/17     1:31            601 supervisor.py
-a---           2025/4/17     0:56            507 user_base.py

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\models\__pycache__

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     1:33           1327 project.cpython-313.pyc
-a---           2025/4/17     0:55            488 student.cpython-313.pyc
-a---           2025/4/17     1:31           1378 supervisor.cpython-313.pyc
-a---           2025/4/17     0:56           1310 user_base.cpython-313.pyc

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\routers

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2025/4/17     0:11                __pycache__
-a---           2025/4/16    21:38            362 user.py

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\routers\__pycache__

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     0:11            748 user.cpython-313.pyc

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\schemas

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2025/4/17     0:14                __pycache__
-a---           2025/4/16    22:26            677 user.py

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\schemas\__pycache__

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     0:14           1533 user.cpython-313.pyc

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\tests

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     1:44         474148 register result found in MySQL.png
-a---           2025/4/17     1:43         218211 register success in postman.png

    Directory: C:\Users\a7846\Desktop\32933\32933-project-match\backend\__pycache__

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           2025/4/17     0:54            802 database.cpython-313.pyc
-a---           2025/4/16    22:28            560 main.cpython-313.pyc
-a---           2025/4/16    16:29           6514 user.cpython-313.pyc


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

