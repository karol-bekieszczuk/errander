# Errander APP

Celem aplikacji jest zarządzanie użytkownikami, zleceniami oraz przypisywanie ich do odpowiednich użytkowników.

Baza danych używana w aplikacji to PostgreSQL, narzędzie do testow jednostkowych i integracyjnych to wbudowane narzedzia Django.

Kiedy użytkownik odwiedzi stronę główną nie będąc zalogowanym zostanie przekierowany na stronę logowania ( /login_user ). Jedynie konta z odpowiednimi uprawnieniami mają możliwość wysyłania zaproszeń do założenia konta w aplikacji. Zaproszenie zawiera link aktywujący konto wysłane na podany podczas rejestracji adres. Po potwierdzeniu rejestracji poprzez email użytkownik może zalogować się w aplikacji. Jeżeli token ma więcej niz jeden dzien i uzytkownik nie zostal aktywowany pg_cron sprawdzajac powyzsze warunki raz na 24h usunie uzytkownika.

Domyślny model User z django.contrib.auth.models został zamieniony na customowy rezydujący w accounts/models.py aby dodać m.in. timestampy dla tokenów. Innym istotnym powodem było ograniczenie zapytań do bazy danych, przy takim podejściu zostaje wysłane tylko jedno zapytanie przy pobraniu obiektu użytkownika, gdzie przy użyciu relacji one-to-one oraz sygnałow wymagało by dodatkowego zapytania pobierając dane użytkownika nie znajdujące się w domyślnym modelu User.

Po zalgowaniu pojawi się strona główna na której będą wyświetlone wszystkie zlecenia do których użytkownik jest przypisany. Pojawi się także odnośnik w toolbarze do strony głównej, Errands ( /errands ) i My profile ( /profile ).

User z odpowiednimi uprawnieniami może tworzć/edytować/usuwać zlecenia oraz przypisywać userów do errandow. Ma takze uprawnienia do wysylania zaproszen do aplikacji, projekt nie bedzie posiadac strony rejestracji dla niezalogowanych użytkownikow oraz nie posiadajacymi odpowiednich uprawnien.
User ma możliwość przeglądania errandu i zmiany jego statusu oraz dodanie opisu.

Każde zlecenie ma możliwość przypisania lokalizacji przez mapy Google.

Zlecenia są wyświetlane na stronie głównej aplikacji ( / )

Modele:
User
Errand

Technology stack:

Python wersja 3.10.6
Django wersja 4.1.2
django-simple-history 3.2.0
django-permissionedforms 0.1

TODO
rewrite tests f.e. with pytest-djang
