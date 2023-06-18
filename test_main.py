import unittest
import sqlite3
from main import PlanCard, ExerciseCard, HomePage, StartedPage, NewPlanScreen, CalendarScreen


class MainTestCase(unittest.TestCase):

    def setUp(self):
        # Utwórz połączenie z bazą danych w pamięci
        self.connection = sqlite3.connect(':memory:')
        self.connection.execute("PRAGMA foreign_keys = ON")  # Włącz klucze obce
        self.conn = self.connection.cursor()

        # Utwórz tabelę workouts
        self.conn.execute("CREATE TABLE workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)")

        # Utwórz tabelę exercise
        self.conn.execute("CREATE TABLE exercise (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")

        # Utwórz tabelę exersise_in_workouts
        self.conn.execute("CREATE TABLE exersise_in_workouts (cwiczenie_id INTEGER, plan_id INTEGER, "
                          "FOREIGN KEY (cwiczenie_id) REFERENCES exercise (id), "
                          "FOREIGN KEY (plan_id) REFERENCES workouts (id))")

        # Wstaw przykładowe dane do tabeli workouts
        self.conn.execute("INSERT INTO workouts (title) VALUES ('Plan 1')")
        self.conn.execute("INSERT INTO workouts (title) VALUES ('Plan 2')")

        # Wstaw przykładowe dane do tabeli exercise
        self.conn.execute("INSERT INTO exercise (name) VALUES ('3/4 sit-up')")
        self.conn.execute("INSERT INTO exercise (name) VALUES ('3/4 sit-up')")

        # Wstaw przykładowe dane do tabeli exersise_in_workouts
        self.conn.execute("INSERT INTO exersise_in_workouts (cwiczenie_id, plan_id) VALUES (1, 1)")
        self.conn.execute("INSERT INTO exersise_in_workouts (cwiczenie_id, plan_id) VALUES (2, 1)")
        self.connection.commit()

    def tearDown(self):
        # Zamknij połączenie z bazą danych
        self.connection.close()

    def test_start_plan(self):
        plan_card = PlanCard(title='Plan 1')
        plan_card.start_plan()

        # Sprawdź, czy manager przełączył się na ekran 'started_page'
        self.assertEqual(plan_card.manager.current, 'started_page')

        # Sprawdź, czy started_page załadował ćwiczenia z odpowiedniego planu
        started_page = plan_card.manager.get_screen('started_page')
        self.assertEqual(len(started_page.ids.startedex.children), 2)

    def test_add_exercise_to_plan(self):
        exercise_card = ExerciseCard()
        exercise_card.add_exercise_to_plan('3/4 sit-up')

        # Sprawdź, czy ćwiczenie zostało dodane do bazy danych
        self.conn.execute("SELECT name FROM exercise WHERE name = '3/4 sit-up'")
        result = self.conn.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Exercise 3')

    def test_refresh_screen(self):
        home_page = HomePage()

        # Wywołaj metodę refresh_screen()
        home_page.refresh_screen()

        # Sprawdź, czy wszystkie plany zostały wyświetlone
        self.assertEqual(len(home_page.ids.timeline.children), 2)

    def test_load_exercises(self):
        started_page = StartedPage()

        # Wywołaj metodę load_exercises() dla planu 'Plan 1'
        started_page.load_exercises('Plan 1')

        # Sprawdź, czy ćwiczenia zostały poprawnie załadowane
        self.assertEqual(len(started_page.ids.startedex.children), 2)

    def test_add_plan_title(self):
        new_plan_screen = NewPlanScreen()
        new_plan_screen.ids.plan_title.text = 'New Plan'
        new_plan_screen.add_plan_title()

        # Sprawdź, czy nowy plan został dodany do bazy danych
        self.conn.execute("SELECT title FROM workouts WHERE title = 'New Plan'")
        result = self.conn.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'New Plan')

    def test_update_calendar(self):
        calendar_screen = CalendarScreen()
        calendar_screen.current_month = 6
        calendar_screen.current_year = 2023
        calendar_screen.update_calendar()

        # Sprawdź, czy liczba dni w miesiącu została poprawnie zaktualizowana
        num_days = len(calendar_screen.ids.days_layout.children)
        self.assertEqual(num_days, 30)


if __name__ == '__main__':
    unittest.main()
