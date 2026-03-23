from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QApplication,
    QSizePolicy,
    QGraphicsOpacityEffect,
)
from PyQt5.QtGui import QFont, QPixmap, QPainter, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from db import connect_db, initialize_database
from course_management_window import CourseManagementWindow
from styles_css.styles import (
    input_style_login_window,
    main_window_left_side,
    main_window_left_side_rounded_label,
    main_window_right_side_login,
    main_window_exit_button,
    apply_shadow,
)
from login_window import LoginWindow
import sys


class MainWindow(QWidget):
    def __init__(self, role="student"):
        super().__init__()
        self.role = role
        self.setWindowTitle("E-learning Πλατφόρμα ")
        self.setGeometry(500, 100, 1300, 920)
        self.setWindowState(Qt.WindowMaximized)

        self.background_image = QPixmap("icons/background-main-window.png")
        if self.background_image.isNull():
            print("Προσοχή: Η εικόνα icons/background-main-window.png δεν βρέθηκε!")

        self.init_ui()

    # Συνάρτηση για να ζωγραφίζει το background image στο παράθυρο και να τεντώνει την εικόνα σε όλο το παράθυρο
    def paintEvent(self, event):
        painter = QPainter(self)
        # Σχεδίαση της ήδη φορτωμένης εικόνας
        if not self.background_image.isNull():
            # Χρησιμοποιούμε το self.background_image αντί να το φορτώνουμε από το δίσκο
            painter.drawPixmap(self.rect(), self.background_image)

        super().paintEvent(event)

    def init_ui(self):

        main_layout = QHBoxLayout()

        # Αριστερή πλευρά - branding panel
        left_frame = QFrame()
        left_frame.setFixedWidth(500)  # Ορίζω το frame να είναι 500 x 800
        # Υψος του frame για να χωράει το εικονίδιο,όσο το αυξάνω είναι σαν να κάνει zoom out το εικονίδιο και να φαίνεται μικρότερο,όσο το μειώνω είναι σαν να κάνει zoom in και να φαίνεται μεγαλύτερο,Παντα ομως πιάνει όλο το ύψος του frame
        left_frame.setFixedHeight(970)
        left_frame.setStyleSheet(main_window_left_side())
        # alpha= είναι η διαφάνεια της σκιάς, όσο μικρότερη είναι τόσο πιο διαφανής είναι η σκιά, όσο μεγαλύτερη είναι τόσο πιο έντονη είναι η σκιά. Το 170 είναι μια καλή τιμή για να φαίνεται η σκιά χωρίς να είναι υπερβολική.
        apply_shadow(left_frame, blur=30, x=0, y=0, alpha=170)

        # --- ΠΡΟΣΘΗΚΗ BACKGROUND ΣΤΟ FRAME ---
        bg_label = QLabel(left_frame)
        icon_pixmap = QPixmap("icons/left_panel_icon_bg.png")
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)

        # Κάνουμε την εικόνα scale ακριβώς στο μέγεθος του frame,τις βάζουμε τις διαστάσεις του frame για να πιάνουν όλο το frame χωρίς κενά
        bg_label.setPixmap(
            icon_pixmap.scaled(
                500, 970, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        )

        # Κάνουμε scale την εικόνα
        scaled_pixmap = icon_pixmap.scaled(
            500, 970, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        bg_label.setPixmap(scaled_pixmap)
        bg_label.setGeometry(0, 0, 500, 970)

        # Δημιουργούμε μια μάσκα με στρογγυλεμένες γωνίες
        # Ορίζουμε το ορθογώνιο και την ακτίνα (30px),αν θες μόνο αριστερά στρογγυλεμένα, χρησιμοποίησε μεγαλύτερο width στο rect της μάσκας.
        path = QPainterPath()
        # To 5 εδώ αλλάζει το ποσο κοβεται η γωνια στις δυο κατω πλευρές του frame, αν το βάλεις 0 θα κοβονται πιο πολύ, αν το βάλεις 10 θα κοβονται λιγότερο.
        path.addRoundedRect(0, 5, 500, 935, 30, 30)
        # 935 είναι το ύψος του frame μείον το 5 που δώσαμε στην αρχή για να μην κοβεται πολύ η γωνία, αν το βάλεις 970 θα κοβονται πολύ οι γωνίες.
        region = QRegion(path.toFillPolygon().toPolygon())
        bg_label.setMask(region)  # Αυτό "κόβει" φυσικά την εικόνα
        # Κόβει και το frame για να μην εξέχει τίποτα
        left_frame.setMask(region)
        # Επιβάλουμε στρογγύλεμα ΚΑΙ στο QLabel ώστε να "κόψει" τις γωνίες της εικόνας που προεξέχουν.
        bg_label.setStyleSheet(main_window_left_side_rounded_label())
        # Εξασφαλίζουμε ότι το label σέβεται το border-radius για το περιεχόμενό του
        bg_label.setAttribute(Qt.WA_StyledBackground, True)

        left_layout = QVBoxLayout(left_frame)  # Σύνδεση layout με το frame
        # Αφαίρεση περιθωρίων για να καλύψει όλο το frame
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        # π.χ.250x250 είναι το αρχικό μεγεθος του icon, αλλά μετά το αλλάζω στο scaled για να φαίνεται καλύτερα στην οθόνη
        icon_pixmap = QPixmap(250, 250)
        icon_pixmap.load("icons/icon-main-window.png")
        # Εδω αλλάζει το πραγματικό μέγεθος του icon
        logo_label.setPixmap(
            icon_pixmap.scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        logo_label.setAlignment(Qt.AlignCenter)
        # Το logo_label περιέχει το εικονίδιο και το τοποθετεί πρώτο-πρώτο στην κορυφή του layout
        left_layout.addWidget(logo_label)

        left_label = QLabel("E-Learning\nΠλατφόρμα")
        left_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        left_label.setStyleSheet("color: white;")
        # Κεντράρει το κείμενο μέσα στο label (δηλαδή η λέξη "Πλατφόρμα" θα είναι ακριβώς κάτω από το κέντρο της λέξης "E-Learning").
        left_label.setAlignment(Qt.AlignCenter)
        # Κεντράρει το label μέσα στο panel.
        # Το logo_label περιέχει το εικονίδιο και το τοποθετεί πρώτο-πρώτο στην κορυφή του layout
        left_layout.addWidget(logo_label)
        # Προσθέτει ένα κενό 10 pixels κάτω από το εικονίδιο για να μην κολλάει το κείμενο πάνω του
        left_layout.addSpacing(10)
        # Τοποθετεί το Label με το κείμενο ("E-Learning Πλατφόρμα") ακριβώς κάτω από το κενό που αφήσαμε πριν
        left_layout.addWidget(left_label)
        # "Πάρε όλο αυτόν τον σκελετό (εικόνα-κενό-κείμενο) και τοποθέτησέ τον μέσα στο γκρίζο/background πλαίσιο που ονομάσαμε left_frame
        left_frame.setLayout(left_layout)

        # Δεξιά πλευρά - login card
        self.login_frame = QFrame()
        self.login_frame.setFixedWidth(480)
        # Αυτό επιτρέπει στο frame να μεγαλώνει όσο προσθέτεις μεγάλα πεδία
        self.login_frame.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.MinimumExpanding
        )
        self.login_frame.setStyleSheet(main_window_right_side_login())
        self.login_frame.setGraphicsEffect(None)
        self.login_layout = QVBoxLayout()
        self.login_layout.setContentsMargins(40, 40, 40, 40)
        self.login_frame.setLayout(self.login_layout)

        # Αντί για load_login_fields, δημιουργώ το Widget που έφτιαξα
        self.login_widget = LoginWindow(parent_window=self)
        self.login_layout.addWidget(self.login_widget)

        main_layout.addWidget(left_frame)
        main_layout.addStretch()
        main_layout.addWidget(self.login_frame)
        # Δίνουμε χώρο στη σκιά να φανεί
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Κουμπί εξόδου
        exit_button = QPushButton("Έξοδος")
        exit_button.setFixedWidth(100)
        exit_button.setStyleSheet(main_window_exit_button())
        exit_button.clicked.connect(QApplication.quit)

        # Layout για το κουμπί κάτω δεξιά
        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addStretch()
        bottom_right_layout.addWidget(exit_button)

        # Τελικό layout
        outer_layout = QVBoxLayout()
        outer_layout.addLayout(main_layout)
        outer_layout.addLayout(bottom_right_layout)

        self.setLayout(outer_layout)

    def authenticate_user(self):
        # ΠΡΟΣΟΧΗ:Τα πεδία email_input και password_input ανήκουν στο login_widget
        email = self.login_widget.email_input.text()
        password = self.login_widget.password_input.text()

        self.login_widget.login_error.hide()
        self.login_widget.login_successful.hide()

        self.login_widget.email_input.setStyleSheet(input_style_login_window())
        self.login_widget.password_input.setStyleSheet(input_style_login_window())

        email = self.login_widget.email_input.text()
        password = self.login_widget.password_input.text()
        valid = True

        # SELECT user_id,role,username:Επιλέγω αυτές τις τρεις στήλες από τον πίνακα users(FROM users)
        conn = connect_db()
        # WHERE email=? AND password=?:Φέρνω μόνο τη γραμμή όπου το email και το password ταιριάζουν με αυτά που θα σου δώσω
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, role FROM users WHERE email=? AND  password=?",
            (email, password),
        )
        # επιστρέφει ένα tuple,μία λίστα με στοιχεία π.χ.user = (1, "Dimitris", "admin"),user_id primary key
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id = user[0]  # π.χ.      1
            username = user[1]  # "Dimitris"
            role = user[2]  # "admin" ή "student"
            self.login_widget.login_successful.setText(
                f"Επιτυχής σύνδεση! Καλωσήρθες, {username}."
            )

            # Δημιουργώ ένα εφέ διαφάνειας για το label
            opacity_effect = QGraphicsOpacityEffect(self.login_widget.login_successful)
            self.login_widget.login_successful.setGraphicsEffect(opacity_effect)

            # Ρυθμίζω το animation
            self.anim = QPropertyAnimation(opacity_effect, b"opacity")
            self.anim.setDuration(800)  # Διάρκεια 0.8 δευτερόλεπτα
            self.anim.setStartValue(0)  # Ξεκινάει από τελείως διαφανές
            self.anim.setEndValue(1)  # Καταλήγει σε πλήρως ορατό
            self.anim.setEasingCurve(QEasingCurve.InOutQuad)  # Ομαλή κίνηση
            self.login_widget.login_successful.show()
            self.anim.start()  # Ξεκινάει το animation
            QTimer.singleShot(
                2000,
                lambda: self.open_course_management_window(
                    user_id=user_id, admin=(role == "admin")
                ),
            )

        else:
            self.login_widget.login_error.setText("Λάθος email ή κωδικός.")
            self.login_widget.login_error.show()
            valid = False

        if not valid:
            return  # Σταματάμε αν υπάρχει σφάλμα

    def open_course_management_window(self, user_id, admin=False):
        self.course_window = CourseManagementWindow(user_id=user_id, admin=admin)
        self.course_window.showMaximized()
        self.close()


if __name__ == "__main__":
    initialize_database()  # Δημιουργεί πίνακες και φάκελο lectures
    app = QApplication(sys.argv)
    win = MainWindow()  # Η επιλογή ρόλου γίνεται μέσα στο MainWindow
    win.showMaximized()
    sys.exit(app.exec_())
