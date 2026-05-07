# uneversity-program-for-training

mirik:
python -m vemv vemv 
source venv/Scripts/activate

pip install -r requirements.txt
cd src

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperusers
python manage.py runserver

git branch -M [name]

git add .
git commit -m " info "
git push

git pull origin main



# Commands #
1. pwd =                            tells us where we are
2. ls =                             shows what is in this folder.
3. ls -l =                          shows a list of folders in a convenient way.
4. clear =                          clean terminal.
5. ctrl + l =                       clears the terminal
6. mkdir =                          command line to create this folder
7. cd folder-name =                 enter the folder.
8. cd .. =                          this is back, i.e. back
9. rmdir =                          this deletes the folder.
10. touch file-name =               command line to create a file;
11. echo" something " > file-name = created this file and adds information into it.
12. cat file-name =                 to view the information inside this file.
13. nano file-name =                editor to change file.
14. ctrl+x => y => ctrl+m =         saves changes to this file and exits the editor.
15. rm -rf =                        this deletes the folder and its contents, including files.
16. mv =                            this renames or moves files and folders.
17. cp =                            copies this file or folder.

