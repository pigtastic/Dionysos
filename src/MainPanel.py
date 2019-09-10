import time
import json
from kivy.core.text import Label
from drinks import drink_list, ingredients
from kivy.properties import StringProperty, ListProperty
from kivy.uix.progressbar import ProgressBar
from functools import partial
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import Image
from kivy.clock import Clock
from database import Database
from HectorConfig import config

from HectorHardware import HectorHardware


class MainPanel(Screen):
    buttonText = ListProperty([StringProperty(),
                               StringProperty(),
                               StringProperty(),
                               StringProperty(),
                               StringProperty(),
                               StringProperty(),
                               StringProperty(),
                               StringProperty()])

    buttonColor = ListProperty([ListProperty(),
                                ListProperty(),
                                ListProperty(),
                                ListProperty(),
                                ListProperty(),
                                ListProperty(),
                                ListProperty(),
                                ListProperty()])

    db = None
    drinkOnScreen = None
    screenPage = None
    maxScreenPage = None

    def __init__(self, **kwargs):
        super(MainPanel, self).__init__(**kwargs)

        self.db = Database("h9k")

        self.db.createIfNotExists()

        self.screenPage = 1

        items = len(drink_list) % 8
        self.maxScreenPage = (len(drink_list) // 8)

        if items > 0:
            self.maxScreenPage += 1

        self.drinkOnScreen = list()
        self.drinkOnScreen = drink_list[:8]

        self.fillButtons(self.drinkOnScreen)
        self.initVent()

    def initVent(self):
        print("Prepare vets.")
        h = HectorHardware(config)


        h.pump_stop()
        for vnum in range(12):
            print("Vent %d closing..." % (vnum,))
            time.sleep(0.2)
            h.valve_close(vnum)

    def isalcoholic(self, drink):
        for ing, _ in drink["recipe"]:
            if ingredients[ing][1]: return True
        return False

    def fillButtons(self, drinks):
        countDrinksOnScreen = len(drinks)
        count = 0
        while count < countDrinksOnScreen:
            self.buttonText[count] = drinks[count]['name']
            if self.buttonText[count].startswith("..."):
                self.buttonColor[count] = [.3, .3, .3, 1]
            elif self.isalcoholic(drinks[count]):
                self.buttonColor[count] = [1, 0, 0, 1]
            else: # non-alcoholic
                self.buttonColor[count] = [0, 1, 0, 1]
            count += 1

        while count < 8:
            self.buttonText[count] = ''
            self.buttonColor[count] = [1, 1, 1, 1]
            count += 1

    def choiceDrink(self, *args):
        self.readPumpConfiguration()
        if len(self.drinkOnScreen) -1 < args[0]:
            print("no drinks found.")
            return

        root = BoxLayout(orientation='vertical')
        root2 = BoxLayout()
        root2.add_widget(Image(source='img/empty-glass.png'))
        root2.add_widget(
            Label(text='Please be sure\n that a glass \nwith min 200 ml \nis placed onto \nthe black fixture.', font_size='30sp'))
        root.add_widget(root2)

        contentOK = Button(text='OK', font_size=60, size_hint_y=0.5)
        root.add_widget(contentOK)

        contentCancel = Button(text='Cancel', font_size=60, size_hint_y=0.5)
        root.add_widget(contentCancel)

        popup = Popup(title='', content=root,
                      auto_dismiss=False)

        def closeme(button):
            popup.dismiss()
            Clock.schedule_once(partial(self.doGiveDrink, args[0]), .01)

        contentOK.bind(on_press=closeme)
        
        def cancelme(button):
            popup.dismiss()

        contentCancel.bind(on_press=cancelme)

        popup.open()

    def doGiveDrink(self, drink, intervaltime):
        root = BoxLayout(orientation='vertical')
        content = Label(text='Take a break -- \nYour \n\n' + self.drinkOnScreen[drink]["name"]+'\n\nwill be mixed.', font_size='40sp')
        root.add_widget(content)
        popup = Popup(title='Life, the Universe, and Everything. There is an answer.', content=root,
                      auto_dismiss=False)

        def makeDrink(parentwindow):
            drinks = self.drinkOnScreen[drink]
            hector = HectorHardware(config)

            

            for ingridient in drinks["recipe"]:
                hector.valve_dose(pumpList[ingridient[0]], ingridient[1])
                time.sleep(.1)
                print("IndexPumpe: ", pumpList[ingridient[0]])
                print("Ingredient: ", ingridient[0])
                print("Output in ml: ", ingridient[1])
                self.db.countUpIngredient(ingridient[0],ingridient[1])

            time.sleep(1)
            self.db.countUpDrink(drinks["name"])
            hector.finger(1)
            hector.ping(3)
            hector.finger(0)
            print(drinks["name"])
            parentwindow.dismiss()

        popup.bind(on_open=makeDrink)

        popup.open()

    def back(self):
        if self.screenPage == 1:
            self.screenPage = self.maxScreenPage
        else:
            self.screenPage -= 1

        self.drinkOnScreen = drink_list[(self.screenPage * 8) - 8:8 * self.screenPage]
        self.fillButtons(self.drinkOnScreen)

    def forward(self):
        if self.screenPage == self.maxScreenPage:
            self.screenPage = 1
        else:
            self.screenPage += 1
        i = (self.screenPage * 8) - 8
        self.drinkOnScreen = drink_list[i:8 * self.screenPage]
        self.fillButtons(self.drinkOnScreen)

    def readPumpConfiguration(self):
        x = json.load(open('servo_config.json'))
        global pumpList
        pumpList = {}
        for key in x:
            chan = x[key]
            pumpList[chan['value']] = chan['channel']

        return pumpList

    pass
