# Errander APP

Celem aplikacji jest zarządzanie grupami, użytkownikami, zleceniami oraz przypisywanie ich do odpowiednich użytkowników.

Baza danych używana w aplikacji to PostgreSQL, narzędzie do testow jednostkowych i integracyjnych wbudowane narzedzia Django.

Kiedy użytkownik odwiedzi stronę główną nie będąc zalogowanym zostanie przekierowany na stronę logowania ( /login ). Jedynie konta w grupie manager mają możliwość wysyłania zaproszeń do założenia konta w aplikacji. Zaproszenie zawiera link aktywujący konto wysłane na podany podczas rejestracji adres. Po potwierdzeniu rejestracji poprzez email użytkownik może zalogować się w aplikacji. Jeżeli token ma więcej niz jeden dzien i uzytkownik nie zostal aktywowany pg_cron sprawdzajac powyzsze warunki raz na 24h usunie uzytkownika z tabeli.

Domyślny model User z django.contrib.auth.models został zamieniony na customowy rezydujący w accounts/models.py aby dodać m.in. timestampy dla tokenów. Innym istotnym powodem było ograniczenie zapytań do bazy danych, przy takim podejściu zostaje wysłane tylko jedno zapytanie przy pobraniu obiektu użytkownika, gdzie przy użyciu relacji one-to-one oraz sygnałow wymagało by dodatkowego zapytania pobierając dane użytkownika nie znajdujące się w domyślnym modelu User.

Po zalgowaniu pojawi się strona główna na której będą wyświetlone wszystkie zlecenia i grupy do których użytkownik jest przypisany. Pojawi się także odnośnik w toolbarze do strony głównej, Errands ( /errands ), Groups ( /groups ) i My profile ( /profile ).

Są 3 typy użytkowników, user, manager i admin.
Admin ma pełne uprawnienia do edycji uprawnień użytkowników, zleceń i grup poprzez panel administratora.
Manager może tworzć/edytować/usuwać zlecenia, grupy, oraz przypisywać userów do eventów do których sam jest przypisany. Ma takze uprawnienia do wysylania zaproszen do aplikacji, projekt nie bedzie posiadac strony rejestracji dla niezalogowanych użytkownikow nie będących managerami.
User ma możliwość przeglądania, zatwiedzenia/odrzucenia zlecenia i zmiany jego statusu.

Każde zlecenie ma możliwość przypisania klienta oraz lokalizacji przez mapy Google, dodanie lokalizacji GPS bądź opis słowny.

Zlecenia są wyświetlane w kalendarzu na podstronie Errands ( /errands )

Modele:
User
Errand
Client

Technology stack:

Python wersja 3.10.6
Django wersja 4.1.2
django-simple-history 3.2.0
django-permissionedforms 0.1

TODO
custom errors
rewrite tests f.e. with pytest-djang
