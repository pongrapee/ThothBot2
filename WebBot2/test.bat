@echo off
set "home=C:\Users\Pongrapee\Desktop\TEMP\spider2\WebBot2"
:loop
call scrapy crawl new_bot
timeout 10
goto :loop