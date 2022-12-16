# Errander APP

Celem aplikacji jest zarządzanie grupami, użytkownikami, zleceniami oraz przypisywanie ich do odpowiednich użytkowników.

Baza danych używana w aplikacji to PostgreSQL, narzędzie do testowania Selenium, podejście TDD.

Kiedy użytkownik odwiedzi stronę główną nie będąc zalogowanym zostanie przekierowany na stronę rejestracji ( /signup ) z odnośnikiem do logowania ( /login ). Stworzenie konta powoduje wysłanie maila z linkiem aktywującym konto na podany podczas rejestracji adres przez NAZWA MODULU TODO. Po potwierdzeniu rejestracji poprzez email użytkownik może zalogować się w aplikacji.

Po zalgowaniu pojawi się strona główna na której będą wyświetlone wszystkie zlecenia i grupy do których użytkownik jest przypisany. Pojawi się także odnośnik w toolbarze do strony głównej, Errands ( /errands ), Groups ( /groups ) i My profile ( /profile TODO ).

Są 3 typy użytkowników, user, manager i admin.
Admin ma pełne uprawnienia do edycji uprawnień użytkowników, zleceń i grup poprzez panel administratora.
Manager może tworzyć/edytować/usuwać zlecenia, grupy, oraz przypisywać userów do  eventów do których sam jest przypisany.
User ma możliwość przeglądania i zatwiedzenia/odrzucenia zlecenia.

Każde zlecenie ma możliwość przypisania lokalizacji przez mapy Google, dodanie lokalizacji GPS bądź opis słowny.

Zlecenia są wyświetlane w kalendarzu na podstronie Errands ( /Errands )
