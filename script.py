import subprocess

def migrate():
    subprocess.run(['python', 'manage.py', 'makemigrations'])
    subprocess.run(['python', 'manage.py', 'migrate'])

# python manage.py migrate --fake grademod

def fakeMigrate():
    subprocess.run(['python', 'manage.py', 'migrate', '--fake', 'grademod'])

def start():
    subprocess.run(['python', 'manage.py', 'runserver'])

def main():
    userInput = input("What do you want to do? (migrate/fake/start): ")
    while userInput != "exit":
        if userInput == "migrate":
            migrate()
        elif userInput == "start":
            start()
        elif userInput == "fake":
            fakeMigrate()
        elif userInput != "exit":
            print("Invalid input")
        userInput = input("What do you want to do? (migrate/fake/start): ")

if __name__ == '__main__':
    main()