# --- Standard Library Imports ---
import os
import sys

# --- PyQt5 Imports ---
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
    QStackedWidget, QScrollArea, QFrame, QWidget
)

# --- Local Application Imports ---
from ...i18n.translator import get_translation
from ..main_window import get_app_icon_object


class TourStepWidget(QWidget):
    """
    A custom widget representing a single step or page in the feature guide.
    It neatly formats a title and its corresponding content.
    """
    def __init__(self, title_text, content_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0; padding-bottom: 15px;")
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("background-color: transparent;")

        content_label = QLabel(content_text)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        content_label.setTextFormat(Qt.RichText)
        content_label.setOpenExternalLinks(True) # Allow opening links in the content
        content_label.setStyleSheet("font-size: 11pt; color: #C8C8C8; line-height: 1.8;")
        scroll_area.setWidget(content_label)
        layout.addWidget(scroll_area, 1)


class HelpGuideDialog (QDialog ):
    """A multi-page dialog for displaying the feature guide."""
    def __init__ (self ,steps_data ,parent_app ,parent =None ):
        super ().__init__ (parent )
        self .current_step =0 
        self .steps_data =steps_data 
        self .parent_app =parent_app 

        app_icon =get_app_icon_object ()
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self .setModal (True )
        self .setFixedSize (650 ,600 )


        current_theme_style =""
        if hasattr (self .parent_app ,'current_theme')and self .parent_app .current_theme =="dark":
            if hasattr (self .parent_app ,'get_dark_theme'):
                current_theme_style =self .parent_app .get_dark_theme ()


        self .setStyleSheet (current_theme_style if current_theme_style else """
            QDialog { background-color: #2E2E2E; border: 1px solid #5A5A5A; }
            QLabel { color: #E0E0E0; }
            QPushButton { background-color: #555; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 8px 15px; border-radius: 4px; min-height: 25px; font-size: 11pt; }
            QPushButton:hover { background-color: #656565; }
            QPushButton:pressed { background-color: #4A4A4A; }
        """)
        self ._init_ui ()
        if self .parent_app :
            self .move (self .parent_app .geometry ().center ()-self .rect ().center ())

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 


    def _init_ui (self ):
        main_layout =QVBoxLayout (self )
        main_layout .setContentsMargins (0 ,0 ,0 ,0 )
        main_layout .setSpacing (0 )

        self .stacked_widget =QStackedWidget ()
        main_layout .addWidget (self .stacked_widget ,1 )

        self .tour_steps_widgets =[]
        for title ,content in self .steps_data :
            step_widget =TourStepWidget (title ,content )
            self .tour_steps_widgets .append (step_widget )
            self .stacked_widget .addWidget (step_widget )

        self .setWindowTitle (self ._tr ("help_guide_dialog_title","Kemono Downloader - Feature Guide"))

        buttons_layout =QHBoxLayout ()
        buttons_layout .setContentsMargins (15 ,10 ,15 ,15 )
        buttons_layout .setSpacing (10 )

        self .back_button =QPushButton (self ._tr ("tour_dialog_back_button","Back"))
        self .back_button .clicked .connect (self ._previous_step )
        self .back_button .setEnabled (False )

        if getattr (sys ,'frozen',False )and hasattr (sys ,'_MEIPASS'):
            assets_base_dir =sys ._MEIPASS 
        else :
            # Go up three levels from this file's directory (src/ui/dialogs) to the project root
            assets_base_dir =os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

        github_icon_path =os .path .join (assets_base_dir ,"assets","github.png")
        instagram_icon_path =os .path .join (assets_base_dir ,"assets","instagram.png")
        discord_icon_path =os .path .join (assets_base_dir ,"assets","discord.png")

        self .github_button =QPushButton (QIcon (github_icon_path ),"")
        self .instagram_button =QPushButton (QIcon (instagram_icon_path ),"")
        self .Discord_button =QPushButton (QIcon (discord_icon_path ),"")

        icon_size =QSize (24 ,24 )
        self .github_button .setIconSize (icon_size )
        self .instagram_button .setIconSize (icon_size )
        self .Discord_button .setIconSize (icon_size )

        self .next_button =QPushButton (self ._tr ("tour_dialog_next_button","Next"))
        self .next_button .clicked .connect (self ._next_step_action )
        self .next_button .setDefault (True )
        self .github_button .clicked .connect (self ._open_github_link )
        self .instagram_button .clicked .connect (self ._open_instagram_link )
        self .Discord_button .clicked .connect (self ._open_Discord_link )
        self .github_button .setToolTip (self ._tr ("help_guide_github_tooltip","Visit project's GitHub page (Opens in browser)"))
        self .instagram_button .setToolTip (self ._tr ("help_guide_instagram_tooltip","Visit our Instagram page (Opens in browser)"))
        self .Discord_button .setToolTip (self ._tr ("help_guide_discord_tooltip","Visit our Discord community (Opens in browser)"))


        social_layout =QHBoxLayout ()
        social_layout .setSpacing (10 )
        social_layout .addWidget (self .github_button )
        social_layout .addWidget (self .instagram_button )
        social_layout .addWidget (self .Discord_button )

        while buttons_layout .count ():
            item =buttons_layout .takeAt (0 )
            if item .widget ():
                item .widget ().setParent (None )
            elif item .layout ():
                pass 
        buttons_layout .addLayout (social_layout )
        buttons_layout .addStretch (1 )
        buttons_layout .addWidget (self .back_button )
        buttons_layout .addWidget (self .next_button )
        main_layout .addLayout (buttons_layout )
        self ._update_button_states ()

    def _next_step_action (self ):
        if self .current_step <len (self .tour_steps_widgets )-1 :
            self .current_step +=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        else :
            self .accept ()
        self ._update_button_states ()

    def _previous_step (self ):
        if self .current_step >0 :
            self .current_step -=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        self ._update_button_states ()

    def _update_button_states (self ):
        if self .current_step ==len (self .tour_steps_widgets )-1 :
            self .next_button .setText (self ._tr ("tour_dialog_finish_button","Finish"))
        else :
            self .next_button .setText (self ._tr ("tour_dialog_next_button","Next"))
        self .back_button .setEnabled (self .current_step >0 )

    def _open_github_link (self ):
        QDesktopServices .openUrl (QUrl ("https://github.com/Yuvi9587"))

    def _open_instagram_link (self ):
        QDesktopServices .openUrl (QUrl ("https://www.instagram.com/uvi.arts/"))

    def _open_Discord_link (self ):
        QDesktopServices .openUrl (QUrl ("https://discord.gg/BqP64XTdJN"))