1. uruchomić serwer postgres
2. w konsoli przejść do folderu z projektem
3. wpisać komendę "pip install -r requirements.txt"
4. zmodyfikować plik conf.yml, nadać wartości początkowe stałym wartościom takim jak np. adres bazy danych itp
 (skrzynka adresu email (jeśli będzie to gmail) do wysyłania raportów musi mieć zezwolenie na dostęp mniej bezpiecznych aplikacji)
5. wpisać komendę "screen -S api" utworzy ona nowe okno shella
6. wpisać komendę "python main.py" - spowoduje to uruchomienie serwera
7. wcisnąć klawisze ctr+a,d - spowoduje to powrót do pierwotnego okna
8. utworzyć nowe okno za pomocą komendy "screen -S report"
9. wpisać komendę "python report.py" - spowoduje to uruchomienia skryptu do raportowania
10. powrót do pierwotnego okna
11. komenda "screen -ls" pozwoli podejrzeć wszystkie okna wraz z ich numerami ID
12. aby powrócić do konkretnego okna należy wpisać komendę "screen -r <ID>"
13. należy zaimportować plik KartyMenu.postman_collection.json do postmana, tam jest udokumentowane całe API
