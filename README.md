# Playlist

Музыкальный плеер для практической работы № 1 «Связные списки».
Окно написано на Tkinter, звук воспроизводится через pygame. Треки
хранятся в кольцевом двусвязном списке.

## Первый запуск на Windows

1. Установите [Python 3.11 для Windows](https://www.python.org/downloads/release/python-3119/#files). Для обычного 64-битного ПК выберите **Windows installer (64-bit)**. Оставьте включёнными **Tcl/Tk and IDLE** и **Python Launcher**. Python 3.11 подходит и для плеера, и для проверки через Pylint 2.17.7.
2. Если проект ещё не скачан, установите [Git for Windows](https://git-scm.com/install/windows). Откройте **PowerShell** через меню «Пуск» и выполните команды ниже. Git создаст папку `Playlist` внутри «Документов».

```powershell
Set-Location ([Environment]::GetFolderPath('MyDocuments'))
git clone https://github.com/Sofia-Petukhova/Playlist.git
cd Playlist
```

Если проект уже скачан, откройте в Проводнике папку, где лежит `player.py`, введите `powershell` в адресную строку и нажмите Enter.

3. Подготовьте окружение проекта и установите библиотеку для воспроизведения. Выполняйте команды по одной из папки с `player.py`.

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Первая команда должна вывести `Python 3.11.x`. Если команда `py` не найдена, откройте новый PowerShell после установки Python и проверьте, что установлен **Python Launcher**. Если рабочая `.venv` уже есть, сразу переходите к запуску.

4. Запустите плеер. Этой же команды достаточно при следующих запусках из папки проекта.

```powershell
.\.venv\Scripts\python.exe player.py
```

Должно открыться окно «Музыкальный плеер». Нажмите «Добавить файлы», выберите MP3, OGG или WAV с компьютера и нажмите «Играть».

## Управление

При запуске открыт пустой «Мой плейлист». Нажмите «Добавить файлы» и
выберите MP3, OGG или WAV. Двойной щелчок, Enter или кнопка «Играть»
запускают выбранный трек. После последней записи снова играет первая.

Кнопки «Выше» и «Ниже» перемещают выделенную запись. Если убрать
играющий трек, плеер переключится на следующий. Если убрать
единственный трек, воспроизведение остановится.

Кнопка «Создать» добавляет плейлист. Выбрать его можно в выпадающем
списке. Плейлисты хранятся в памяти до закрытия окна.
Удаление записей и плейлистов сохраняет исходные аудиофайлы на диске.

## Тесты курса на Windows

Скачайте [только файл `test_linked_list.py` из репозитория курса](https://gitverse.ru/forjadores/AlgosAndDataStructures/content/master/practice/practice_1/test_linked_list.py) и сохраните его в папку «Загрузки» под этим именем. Команды ниже копируют тест во временную папку, чтобы он импортировал `linked_list.py` из проекта, даже если в «Загрузках» лежит одноимённый шаблон курса.

```powershell
$testDir = Join-Path $env:TEMP "Playlist-tests-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $testDir | Out-Null
Copy-Item -LiteralPath "$env:USERPROFILE\Downloads\test_linked_list.py" -Destination $testDir
.\.venv\Scripts\python.exe -m unittest discover -s $testDir -p test_linked_list.py -v
```

При успешной проверке в конце появятся `Ran 14 tests` и `OK`. Закрывать окно плеера для тестов необязательно.

## Проверка стиля через Pylint на Windows

Если `.venv` создана на Python 3.11 по инструкции выше, выполните:

```powershell
.\.venv\Scripts\python.exe -m pip install pylint==2.17.7
.\.venv\Scripts\python.exe -m pylint --rcfile=.pylintrc audio.py linked_list.py player.py playlist.py
```

Если плеер уже работает в `.venv` на Python 3.12, для этой версии Pylint используйте отдельную `.venv-lint` на Python 3.11. Если она уже настроена, достаточно последней команды.

```powershell
py -3.11 -m venv .venv-lint
.\.venv-lint\Scripts\python.exe -m pip install -r requirements.txt pylint==2.17.7
.\.venv-lint\Scripts\python.exe -m pylint --rcfile=.pylintrc audio.py linked_list.py player.py playlist.py
```

## Запуск и Pylint на Linux и macOS

Используйте Python 3.11 с Tkinter. Откройте терминал в папке проекта и выполните:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python player.py
```

Проверка стиля из той же папки:

```sh
.venv/bin/python -m pip install pylint==2.17.7
.venv/bin/python -m pylint --rcfile=.pylintrc audio.py linked_list.py player.py playlist.py
```

Шаблон списка и настройки pylint взяты из
[репозитория курса](https://gitverse.ru/forjadores/AlgosAndDataStructures/content/master/practice/practice_1).
