import sqlite3
import json
from datetime import datetime
from calendar import monthrange
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRectangleFlatIconButton

from database_setup import create_database





"""
Opis:
    Aplikacja mobilna „Fit calendar” czyli kalendarz ćwiczeń, umożliwia 
    użytkownikom planowanie i organizowanie swoich treningów. Zbudowana 
    została w opraciu o framework Kivy.

Autor:
    Szymon Ciemny s21355

"""

class PlanCard(MDCard):
    title = StringProperty()

    def __init__(self, **kwargs):
        super(PlanCard, self).__init__(**kwargs)
        self.on_start = kwargs.get('on_start')

    def start_plan(self):
        if self.on_start:
            self.on_start(self.title)

class ExerciseCard(MDCard):
    name = StringProperty()
    def add_exercise_to_plan(self, exercise_name):
        try:
            # Utworzenie połączenia z bazą danych
            connection = sqlite3.connect('fitness.db')
            conn = connection.cursor()

            try:
                # Pobranie ID ostatnio dodanego planu treningowego
                conn.execute("SELECT id from workouts order by id DESC limit 1")
                plan_id = conn.fetchone()[0]
                # Wstawienie nowego ćwiczenia do tabeli exercise
                conn.execute("INSERT INTO exercise (name) VALUES (?)", (exercise_name,))
                connection.commit()

                # Pobranie ID nowo dodanego ćwiczenia
                conn.execute("SELECT last_insert_rowid()")
                cwiczenie_id = conn.fetchone()[0]

                # Powiązanie ćwiczenia z planem treningowym w tabeli exercise_in_workouts
                conn.execute("INSERT INTO exersise_in_workouts (cwiczenie_id, plan_id) VALUES (?, ?)",
                             (cwiczenie_id, plan_id))
                connection.commit()

            finally:
                # Zamknięcie połączenia z bazą danych
                connection.close()

        except sqlite3.Error as error:
            # Obsługa błędów bazy danych
            print("An error occurred:", str(error))
        except Exception as error:
            # Obsługa ogólnego błędu
            print("An error occurred:", str(error))

class StartedCard(MDCard):
    title = StringProperty()
    exercise_name = StringProperty('')

class HomePage(Screen):
    def on_pre_enter(self):
        self.refresh_screen()

    # Funkcja pobierająca plany i wyświetlająca je
    def refresh_screen(self):
        self.ids.timeline.clear_widgets()

        connection = sqlite3.connect('fitness.db')
        conn = connection.cursor()

        conn.execute("SELECT title FROM workouts")
        titles = conn.fetchall()

        for title in titles:
            self.ids.timeline.add_widget(PlanCard(title=title[0], on_start=lambda title=title[0]: self.start_plan(title)))

    #
    def start_plan(self, title):
        self.manager.current = 'started_page'
        self.manager.get_screen('started_page').load_exercises(title)


class StartedPage(Screen):
    startedex = ObjectProperty(None)


    def load_exercises(self, plan_title):
        self.title = plan_title
        self.make_screen()

    # Funkcja pobierająca ćwiczenia z planu i wyświetlająca je
    def make_screen(self):
        self.ids.startedex.clear_widgets()

        connection = sqlite3.connect('fitness.db')
        conn = connection.cursor()

        # Pobranie ID ostatnio dodanego planu treningowego
        conn.execute("SELECT exercise.name FROM exercise JOIN exersise_in_workouts ON exercise.id = exersise_in_workouts.cwiczenie_id JOIN workouts ON exersise_in_workouts.plan_id = workouts.id WHERE workouts.title = ?", (self.title,))
        exersise_in_workouts = conn.fetchall()
        for name in exersise_in_workouts:
            self.ids.startedex.add_widget(StartedCard(exercise_name=name[0]))


class NewPlanScreen(Screen):

    def on_enter(self):
        self.list_exercises()

    #  Wyswietlenie wszystkich ćwiczeń w cards
    def list_exercises(self):
        with open('assets/exercises.json') as f_obj:
            data = json.load(f_obj)
            for item in data:
                exercise = ExerciseCard(md_bg_color='#6E6E71')
                exercise.name = item["name"]
                self.ids.exercises.add_widget(exercise)


    def add_plan_title(self):
        try:
            # Pobranie tytułu planu
            plan_title = self.ids.plan_title.text

            # Sprawdzenie, czy tytuł planu jest niepusty
            if not plan_title:
                raise ValueError("Plan title cannot be empty.")

            # Utworzenie połączenia z bazą danych
            connection = sqlite3.connect('fitness.db')
            conn = connection.cursor()

            try:
                # Wstawienie nowego planu treningowego do tabeli workouts
                conn.execute("INSERT INTO workouts (title) VALUES (?)", (plan_title,))
                connection.commit()


            finally:
                # Zamknięcie połączenia z bazą danych
                connection.close()

        except (ValueError, sqlite3.Error) as error:
            # Obsługa błędów związanych z wartościami pustymi oraz błędów bazy danych
            print("An error occurred:", str(error))
        except Exception as error:
            # Obsługa ogólnego błędu
            print("An error occurred:", str(error))
class CalendarScreen(Screen):

    # Definicja właściwości na potrzeby automatycznej aktualziacji
    current_month = NumericProperty(0)
    current_year = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CalendarScreen, self).__init__(**kwargs)
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.days_layout = self.ids.days_layout
        self.update_calendar()

    # Funkcja do aktualizacji kalendarza
    def update_calendar(self):
        _, num_days = monthrange(self.current_year, self.current_month)
        days_layout = self.ids.days_layout
        days_layout.clear_widgets()

        for day in range(1, num_days + 1):
            day_label = MDRectangleFlatIconButton(text=str(day), md_bg_color='white', text_color='black',
                                                  line_color=(0, 0, 0, 0), valign='center', halign='center')
            days_layout.add_widget(day_label)

    # Przycisk do następnego miesiąca
    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()

    # Przycisk do poprzedniego miesiąca
    def previous_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()


class MainApp(MDApp):

    # Definicja kolorów
    background_light = get_color_from_hex('#6E6E71')  # Kolor tła ciemny
    background_dark = get_color_from_hex('#2E2E2F')  # Kolor tła szary ciemny
    text_white = get_color_from_hex('#F1F6F9')  # Kolor tekstu biały
    text_black = get_color_from_hex('#020202')  # Kolor tekstu czarny
    button_red = get_color_from_hex('#E66060')  # Kolor tekstu czarny
    button_green = get_color_from_hex('#47B044')  # Kolor tekstu czarny


    def build(self):
        #  Wczytanie pliku KV
        Builder.load_file('home_page.kv')
        sm = self.create_screen_manager()
        return sm

    def create_screen_manager(self):

        # Definicja stron, ktáre będą wyświetlane.
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomePage(name='home_page'))
        sm.add_widget(CalendarScreen(name='calendar_screen'))
        sm.add_widget(NewPlanScreen(name='new_plan_screen'))
        sm.add_widget(StartedPage(name='started_page'))
        return sm

    def switch_screen(self, screen_name):
        self.root.current = screen_name


if __name__ == "__main__":
    create_database()
    MainApp().run()

