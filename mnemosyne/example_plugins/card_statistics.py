#
# card_statistics.py <bonoshi@gmail.com>
#

import math
import time
from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin


class ShowCardStatsFilter(Filter):

    used_for = "after_load"
    cardAbbre = None
    ID = -1

    def run(self, text, card, fact_key, **render_args):
        if ShowCardStatsFilter.ID == card.id:
            return text
        ShowCardStatsFilter.ID = card.id

        ShowCardStatsFilter.globalRun(self, card)

        return text

    def globalRun(mySelf, card):
        parent = mySelf.main_widget()

        #Next repetition
        interval = mySelf.scheduler().grade_answer(card, 1, True)
        dayGrade1 = str(int(math.ceil(interval / 86400.0)))
        interval = mySelf.scheduler().grade_answer(card, 2, True)
        dayGrade2 = str(int(math.ceil(interval / 86400.0)))
        interval = mySelf.scheduler().grade_answer(card, 3, True)
        dayGrade3 = str(int(math.ceil(interval / 86400.0)))
        interval = mySelf.scheduler().grade_answer(card, 4, True)
        dayGrade4 = str(int(math.ceil(interval / 86400.0)))
        interval = mySelf.scheduler().grade_answer(card, 5, True)
        dayGrade5 = str(int(math.ceil(interval / 86400.0)))

        now = time.time()
        interval_days = (card.last_rep - now) / 86400.0
        interval_days = int(math.floor(-interval_days))

        abbreCardText = "G:" + str(card.grade) + \
                        "|E:" + ("%1.2f" % card.easiness) + \
                        "|Ln:" + str(card.acq_reps) + \
                        "|Re:" + str(card.ret_reps) + \
                        "|Lp:" + str(card.lapses) + \
                        "|LR:" + str(interval_days) + \
                        "|NR:" + dayGrade1 + \
                        "/" + dayGrade2 + \
                        "/" + dayGrade3 + \
                        "/" + dayGrade4 + \
                        "/" + dayGrade5

        if not ShowCardStatsFilter.cardAbbre:
            ShowCardStatsFilter.cardAbbre = QtWidgets.QLabel("", parent.status_bar)
            parent.status_bar.addWidget(ShowCardStatsFilter.cardAbbre)
            ShowCardStatsFilter.cardAbbre.setText(abbreCardText)
        else:
            ShowCardStatsFilter.cardAbbre.setText(abbreCardText)

    globalRun = staticmethod(globalRun)

class CardStatistics(Plugin):
    
    name = "Card Statistics"
    version = "1.0"
    description = "Show card statistics on the left of the status bar. (v" + version + ")\n\n" + \
                  "All abbreviations of the current card are listed as follows:\n\n" + \
                  "G: GRADE\n" + \
                  "E: EASINESS\n" + \
                  "Ln: LEARNING repetitions\n" + \
                  "Re: REVIEW repetitions\n" + \
                  "Lp: LAPSES\n" + \
                  "AT: AVERAGE THINKING time (secs)\n" + \
                  "TT: TOTAL THINKING time (secs)\n" + \
                  "LR: LAST REPETITION (days ago)\n" + \
                  "NR: Expected NEXT REPETITION (days after) when graded 1/2/3/4/5. The actual repetition is subject to randomness and will be around the expected one.\n"
    components = [ShowCardStatsFilter]
    supported_API_level = 2
    firstFilter = False

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        ShowCardStatsFilter.cardAbbre = None

    def activate(self):
        Plugin.activate(self)
        card = self.review_controller().card
        if card:
            ShowCardStatsFilter.globalRun(self, card)

        self.render_chain("default").\
            register_filter_at_front(ShowCardStatsFilter)
        # Other chain you might want to add to is e.g. "card_browser".

    def deactivate(self):
        Plugin.deactivate(self)
        parent = self.main_widget()
        parent.status_bar.removeWidget(ShowCardStatsFilter.cardAbbre)
        ShowCardStatsFilter.cardAbbre = None
        self.render_chain("default").\
            unregister_filter(ShowCardStatsFilter)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(CardStatistics)

