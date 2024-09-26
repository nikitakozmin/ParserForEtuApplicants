# ParserForEtuApplicants
Терминальное приложение, которое, обрабатывая сайт ETU с конкурсными списками, создаёт текстовый файл с максимальными проходными баллами на текущий момент для бюджетного отделения (распределяет абитуриентов по направлениям). Использует браузер Chrome.

## Для запуска должен быть установлен интерпретатор Python3, а также  Selenium 4.16.0 и Webdriver_manager 4.0.0
```
pip install selenium==4.16.0
```
```
pip install webdriver_manager==4.0.0
```
## Пути развития проекта:
- Изменить обработку страниц с абитуриентами под текущую ссылку (включить в декораторе исспользование вложенной функции)
- Полностью скачать весь сайт со всеми дочерними ссылками, чтобы иметь возможность запускать проект локально
- Добавить сборку через докер и тестирование 
- Добавить логирование
- Добавить использование мультипоточности
