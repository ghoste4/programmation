import sys
import psycopg2
from PyQt5.QtWidgets import *
from datetime import date,timedelta
import uuid

# Configuration de la base de données
DB_CONFIG = {
    'host': '10.11.11.22',
    'dbname': 'l3info_52',
    'user': 'l3info_52',
    'password': 'L3INFO_52',
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReadMe")
        self.setGeometry(100, 100, 1500, 1000)

        # Configuration principale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setStyleSheet("background-color:#DECBB7 ;")
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez un titre, auteur, ou éditeur...")
        self.search_input.setStyleSheet("""
            background-color: #8F857D;
            color: white;
            border-radius: 5px;
            padding: 5px;""")
        self.search_button = QPushButton("Rechercher")
        self.search_button.setStyleSheet("""
            background-color: #8F857D;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;""")
        self.search_button.clicked.connect(self.search_books)
        search_layout.addWidget(QLabel("Recherche :"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Tableau des résultats
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ISBN", "Titre", "Auteur", "Année", "Éditeur"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setColumnWidth(0, 100)  
        self.tableWidget.setColumnWidth(1, 550)  
        self.tableWidget.setColumnWidth(2, 200)  
        self.tableWidget.setColumnWidth(3, 50) 
        self.tableWidget.setColumnWidth(4, 300)  
        self.tableWidget.setStyleSheet("""
            QHeaderView::section {
                background-color: #433633; 
                color: white;font-weight: bold;      
                border: 1px solid black;}""")
    
        # Boutons d'action
        button_layout = QHBoxLayout()
        self.borrow_button = QPushButton("Emprunter")
        self.borrow_button.clicked.connect(self.borrow_book)
        self.borrow_button.setStyleSheet("""
            background-color: #433633;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;""")
        self.reserve_button = QPushButton("Réserver")
        self.reserve_button.clicked.connect(self.reserve_book)
        self.reserve_button.setStyleSheet("""
            background-color: #433633;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;""")
        self.review_button = QPushButton("Voir les avis")
        self.review_button.clicked.connect(self.view_reviews)
        self.review_button.setStyleSheet("""
            background-color: #433633;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;""")
        self.users_button = QPushButton("Utilisateurs")
        self.users_button.clicked.connect(self.view_users)
        self.users_button.setStyleSheet("""
            background-color: #433633;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;""")

        button_layout.addWidget(self.borrow_button)
        button_layout.addWidget(self.reserve_button)
        button_layout.addWidget(self.review_button)
        button_layout.addWidget(self.users_button)

        # Ajout des widgets au layout principal
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.tableWidget)
        self.layout.addLayout(button_layout)

    def search_books(self):
        # Récupérer le mot-clé de recherche
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Recherche", "Veuillez entrer un mot-clé pour la recherche.")
            return

        column = None
        if keyword.startswith("T:"):
            column = "title"
            keyword = keyword[2:].strip()
        elif keyword.startswith("A:"):
            column = "author"
            keyword = keyword[2:].strip()
        elif keyword.startswith("E:"):
            column = "publisher"
            keyword = keyword[2:].strip()

        exact_match = keyword.endswith("*")
        if exact_match:
            keyword = keyword[:-1] + "%"
    
        # Connexion à la base de données PostgreSQL
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
    
            # Ajouter la colonne "Disponibilité" à la requête SQL
            if column:
                query = f"""
                SELECT b.isbn, b.title, b.author, b.year, b.publisher,
                       br.return_date AS borrowed_until,
                       r.status AS reservation_status
                FROM books b
                LEFT JOIN borrowing br ON b.isbn = br.isbn AND br.return_date > CURRENT_DATE
                LEFT JOIN reservations r ON b.isbn = r.isbn AND r.status = 'reserved'
                WHERE {column} LIKE %s;
                """
                cursor.execute(query, (keyword,))
            else:
                query = """
                SELECT b.isbn, b.title, b.author, b.year, b.publisher,
                       br.return_date AS borrowed_until,
                       r.status AS reservation_status
                FROM books b
                LEFT JOIN borrowing br ON b.isbn = br.isbn AND br.return_date > CURRENT_DATE
                LEFT JOIN reservations r ON b.isbn = r.isbn AND r.status = 'reserved'
                WHERE b.title LIKE %s OR b.author LIKE %s OR b.publisher LIKE %s;
                """
                cursor.execute(query, (keyword, keyword, keyword))
    
            results = cursor.fetchall()

    
            if not results:
                QMessageBox.information(self, "Recherche", f"Aucun résultat trouvé pour '{keyword}'.")
                self.tableWidget.setRowCount(0)
            else:
                self.tableWidget.setRowCount(len(results))
                self.tableWidget.setColumnCount(6)  # Inclut la colonne "Disponibilité"
                self.tableWidget.setHorizontalHeaderLabels(
                    ["ISBN", "Titre", "Auteur", "Année", "Éditeur", "Disponibilité"]
                )

                for row_idx, row_data in enumerate(results):
                    isbn, title, author, year, publisher, borrowed_until, reservation_status = row_data

                    # Déterminer l'état de disponibilité
                    if borrowed_until:
                        availability = "Emprunté"
                    elif reservation_status == "reserved":
                        availability = "Réservé"
                    else:
                        availability = "Disponible"

                    # Ajouter les données dans le tableau
                    self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(str(isbn)))
                    self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(str(title)))
                    self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(str(author)))
                    self.tableWidget.setItem(row_idx, 3, QTableWidgetItem(str(year)))
                    self.tableWidget.setItem(row_idx, 4, QTableWidgetItem(str(publisher)))
                    self.tableWidget.setItem(row_idx, 5, QTableWidgetItem(availability))

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {e}")
    
    def borrow_book(self):
        # Vérifier si un livre est sélectionné
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Emprunt", "Veuillez sélectionner un livre à emprunter.")
            return

        isbn = self.tableWidget.item(selected_row, 0).text()  # Récupérer l'ISBN du livre sélectionné

        try:
            # Connexion à la base de données PostgreSQL
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Vérifier si le livre est déjà emprunté
            query_check = """
            SELECT * FROM borrowing WHERE isbn = %s AND return_date > CURRENT_DATE;
            """
            cursor.execute(query_check, (isbn,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Emprunt", "Ce livre est déjà emprunté.")
                return

            # Récupérer les utilisateurs disponibles
            cursor.execute("SELECT user_id, location FROM users;")
            users = cursor.fetchall()
            if not users:
                QMessageBox.warning(self, "Emprunt", "Aucun utilisateur disponible.")
                return

            # Créer une boîte de dialogue pour sélectionner un utilisateur
            user_dialog = QDialog(self)
            user_dialog.setWindowTitle("Sélectionner un utilisateur")
            user_dialog.setGeometry(200, 200, 400, 300)

            layout = QVBoxLayout()

            user_table = QTableWidget()
            user_table.setColumnCount(2)
            user_table.setHorizontalHeaderLabels(["ID Utilisateur", "Localisation"])
            user_table.setRowCount(len(users))

            for row_idx, (user_id, location) in enumerate(users):
                user_table.setItem(row_idx, 0, QTableWidgetItem(user_id))
                user_table.setItem(row_idx, 1, QTableWidgetItem(location))

            layout.addWidget(user_table)

            select_button = QPushButton("Sélectionner")
            layout.addWidget(select_button)
            user_dialog.setLayout(layout)

            # Fonction pour finaliser l'emprunt après sélection
            def select_user():
                selected_user_row = user_table.currentRow()
                if selected_user_row == -1:
                    QMessageBox.warning(user_dialog, "Erreur", "Veuillez sélectionner un utilisateur.")
                    return

                selected_user_id = user_table.item(selected_user_row, 0).text()
                user_dialog.accept()  # Fermer la boîte de dialogue
                self.finalize_borrowing(conn, isbn, selected_user_id)

            select_button.clicked.connect(select_user)
            user_dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'emprunt : {e}")

    def finalize_borrowing(self, conn, isbn, user_id):
        try:
            cursor = conn.cursor()

            # Ajouter l'emprunt dans la table
            query_insert = """
            INSERT INTO borrowing (brw_id, user_id, isbn, brw_date, return_date)
            VALUES (%s, %s, %s, %s, %s);
            """
            borrow_id = str(uuid.uuid4())  # ID unique pour l'emprunt
            borrow_date = date.today().isoformat()  # Date d'emprunt
            return_date = (date.today() + timedelta(days=30)).isoformat()  # Retour dans 30 jours

            cursor.execute(query_insert, (borrow_id, user_id, isbn, borrow_date, return_date))
            conn.commit()

            QMessageBox.information(self, "Emprunt", "Le livre a été emprunté avec succès.")
            cursor.close()
            conn.close()

            # Mettre à jour la table après l'emprunt
            self.search_books()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'emprunt : {e}")


    def reserve_book(self):
        # Vérifier si un livre est sélectionné
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Réservation", "Veuillez sélectionner un livre à réserver.")
            return

        isbn = self.tableWidget.item(selected_row, 0).text()  # Récupérer l'ISBN du livre sélectionné

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Récupérer les utilisateurs
            cursor.execute("SELECT user_id, location FROM users;")
            users = cursor.fetchall()
            if not users:
                QMessageBox.warning(self, "Réservation", "Aucun utilisateur disponible.")
                return

            # Créer une boîte de dialogue pour sélectionner un utilisateur
            user_dialog = QDialog(self)
            user_dialog.setWindowTitle("Sélectionner un utilisateur")
            user_dialog.setGeometry(200, 200, 400, 300)

            layout = QVBoxLayout()

            user_table = QTableWidget()
            user_table.setColumnCount(2)
            user_table.setHorizontalHeaderLabels(["ID Utilisateur", "Localisation"])
            user_table.setRowCount(len(users))

            for row_idx, (user_id, location) in enumerate(users):
                user_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
                user_table.setItem(row_idx, 1, QTableWidgetItem(location))

            layout.addWidget(user_table)

            select_button = QPushButton("Sélectionner")
            layout.addWidget(select_button)
            user_dialog.setLayout(layout)

            def select_user():
                selected_user_row = user_table.currentRow()
                if selected_user_row == -1:
                    QMessageBox.warning(user_dialog, "Erreur", "Veuillez sélectionner un utilisateur.")
                    return

                selected_user_id = user_table.item(selected_user_row, 0).text()
                user_dialog.accept()  # Fermer la boîte de dialogue
                self.finalize_reservation(conn, isbn, selected_user_id)

            select_button.clicked.connect(select_user)
            user_dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des utilisateurs : {e}")

    def finalize_reservation(self, conn, isbn, user_id):
        try:
            cursor = conn.cursor()

            # Vérifier si le livre est déjà réservé
            query_check = """
            SELECT status FROM reservations WHERE isbn = %s AND status = 'reserved';
            """
            cursor.execute(query_check, (isbn,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Réservation", "Ce livre est déjà réservé.")
                return

            # Ajouter la réservation dans la table
            query_insert = """
            INSERT INTO reservations (rsv_id, user_id, isbn, rsv_date, status)
            VALUES (%s, %s, %s, %s, %s);
            """
            reservation_id = str(uuid.uuid4())
            reservation_date = date.today().isoformat()
            status = "reserved"

            cursor.execute(query_insert, (reservation_id, user_id, isbn, reservation_date, status))
            conn.commit()

            QMessageBox.information(self, "Réservation", "Le livre a été réservé avec succès.")
            cursor.close()
            conn.close()

            # Mettre à jour la table après la réservation
            self.search_books()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la réservation : {e}")


    def view_reviews(self):
        # Vérifier si un livre est sélectionné
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avis", "Veuillez sélectionner un livre pour voir les avis.")
            return

        # Récupérer l'ISBN du livre sélectionné
        isbn = self.tableWidget.item(selected_row, 0).text()

        try:
            # Connexion à la base de données PostgreSQL
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Requête pour obtenir les avis triés par note décroissante
            query = """
            SELECT user_id, rate
            FROM rate
            WHERE isbn = %s
            ORDER BY rate DESC;
            """
            cursor.execute(query, (isbn,))
            results = cursor.fetchall()

            if not results:
                QMessageBox.information(self, "Avis", "Aucun avis disponible pour ce livre.")
            else:
                # Créer une fenêtre de dialogue pour afficher les avis
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Avis pour ISBN {isbn}")
                dialog.setGeometry(200, 200, 400, 300)

                layout = QVBoxLayout()

                review_table = QTableWidget()
                review_table.setColumnCount(2)
                review_table.setHorizontalHeaderLabels(["Utilisateur", "Note"])
                review_table.setRowCount(len(results))

                for row_idx, row_data in enumerate(results):
                    for col_idx, col_data in enumerate(row_data):
                        review_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

                review_table.horizontalHeader().setStretchLastSection(True)

                layout.addWidget(review_table)
                dialog.setLayout(layout)
                dialog.exec_()

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des avis : {e}")

    def view_users(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Requête pour obtenir les utilisateurs
            query = """
            SELECT user_id, location
            FROM users;
            """
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                QMessageBox.information(self, "Utilisateurs", "Aucun utilisateur trouvé.")
            else:
                # Créer une fenêtre de dialogue pour afficher les utilisateurs
                dialog = QDialog(self)
                dialog.setWindowTitle("Liste des utilisateurs")
                dialog.setGeometry(200, 200, 400, 300)

                layout = QVBoxLayout()

                user_table = QTableWidget()
                user_table.setColumnCount(2)
                user_table.setHorizontalHeaderLabels(["ID Utilisateur", "Localisation"])
                user_table.setRowCount(len(results))

                for row_idx, row_data in enumerate(results):
                    for col_idx, col_data in enumerate(row_data):
                        user_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

                user_table.horizontalHeader().setStretchLastSection(True)

                layout.addWidget(user_table)
                dialog.setLayout(layout)
                dialog.exec_()

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des utilisateurs : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



