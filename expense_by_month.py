from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from datetime import datetime
from kivy.uix.image import Image
from kivy.graphics.instructions import Canvas
# from kivy.graphics.instructions import CanvasBase
from kivy.graphics import Color, Rectangle
import PyCanvas


# Creating the scrollview which will go inside our carousel
class ExpenseByMonth(GridLayout):

    def __init__(self, month, data, **kwargs):
        super(ExpenseByMonth, self).__init__(**kwargs)
        self.cols = 1
        data = data
        expenses = data['expenses'][month]
        expense_keys = expenses.keys()
        ordered = sorted(expenses.items(), key = lambda x: x[1]['date'])
        mydate = datetime.strptime(month, '%Y-%m')
        date = mydate.strftime('%B %Y')
        pTotal = 0
        user_budget = data['budget']

        title = Label(text=date, text_size=(None, 1000), size_hint=(1, 0.125), pos_hint={"top": 1, "right": 1},
                      font_size='20 dp', valign='middle')
        SV = ScrollView(size_hint=(1, 0.85), pos_hint={"top": .85,
                                                       "right": 1})  # Set spacing 2 (1,2) to change the vertical spacing between rows
        GL = GridLayout(cols=1, size_hint_y=None, height=self.minimum_height, spacing=(0, 10),
                        row_default_height='40 dp', row_force_default=True)
        GL.bind(minimum_height=GL.setter('height'))

        for i in range(len(ordered)):
            expense = ordered[i][1]
            x = str(expense['category'])
            e = datetime.strptime(str(expense['date']), '%Y%m%d')
            d = e.strftime('%b %d')
            i = 'icons/expenses/' + x + '.png'

            pNum = expense['price']
            pFloat = '%.2f' % pNum
            p = '$ ' + pFloat
            pTotal += pNum

            # widgets
            expenseFloat = FloatLayout(size=self.size)
            expenseFloat.add_widget(Image(source=i, size_hint=(.12, 1), pos_hint={"x": .04, "y": 0}))
            expenseFloat.add_widget(Label(text=x, text_size=self.size, size_hint=(.5, 1),
                                          pos_hint={"x": .125, "y": 1.15}, halign='left'))
            expenseFloat.add_widget(Label(text=d, text_size=self.size, size_hint=(.5, 0.2),
                                          pos_hint={"x": .125, "y": 1.35}, halign='left', font_size='10 dp'))
            expenseFloat.add_widget(Label(text=p, text_size=(self.width, None), size_hint=(.3, 1),
                                          pos_hint={"x": .6, "top": 1.1}, halign='right', font_size='18 dp'))

            GL.add_widget(expenseFloat)

        SV.add_widget(GL)

        strTotal = '%.2f' % pTotal
        over_under = ''
        if user_budget != 0:
            if pTotal < user_budget:
                over_under = str(int(100 - (pTotal / user_budget * 100))) + '% Under Budget'
                # print(over_under + '% Under Budget')
            else:
                over_under = str(int(pTotal / user_budget * 100) - 100) + '% Over Budget'
                # print(over_under + '% Over Budget')

        total_float = PyCanvas.pythoncanvas(data['colorscheme']['utility_color'])


        l1 = Label(text_size=self.size, text="Monthly Total: ", pos_hint={"top": 1.6, "right": 1}, font_size='14',
                   halign='left', padding_x='5 dp')
        l1.bind(size=l1.setter('text_size'))
        l2 = Label(text_size=self.size, pos_hint={"top": 1.55, "right": .96}, font_size='18 dp', halign='right',
                   padding_x='5 dp', id='monthly_total', text="$ " + strTotal)
        l2.bind(size=l2.setter('text_size'))
        l3 = Label(text_size=self.size, color=(0.5, 0.5, 0.5, 1), pos_hint={"top": 1.3, "right": 1}, font_size='12 dp',
                   halign='left', padding_x='5 dp', id='budget_percent', text=over_under)
        l3.bind(size=l3.setter('text_size'))

        total_float.add_widget(l1)
        total_float.add_widget(l2)
        total_float.add_widget(l3)

        # Add All Layouts to Carousel
        self.add_widget(title)
        self.add_widget(SV)
        self.add_widget(total_float)
