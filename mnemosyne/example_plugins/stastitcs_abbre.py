#
# stastitcs_abbre.py <bonoshi@gmail.com>
#

import math
from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin

class ShowStatsAbbreFilter(Filter):
    def run(self, text, card, fact_key, **render_args):
        scheduled_count, non_memorised_count, active_count = self.review_controller().counters()
        #quite dirty but the condition is in order to avoid the function
        #'card_count_scheduled_n_days_from_now(n=i)' from slowing the system down 
        if StatisticsAbbre.activeCardNum != active_count:
            StatisticsAbbre.activeCardNum = active_count
            for i in range(1, StatisticsAbbre.showSchedDay+1):
                StatisticsAbbre.schedNum[i-1]=(self.scheduler().card_count_scheduled_n_days_from_now(n=i))
            ShowStatsAbbreHook.globalRun(self)
        return text

class ShowStatsAbbreHook(Hook):

    used_for = "after_repetition"

    def run(self, card):
        ShowStatsAbbreHook.globalRun(self, card)
        StatisticsAbbre.firstHook = True

    def globalRun(mySelf, card=None):
        parent = mySelf.main_widget()
        parent.clear_status_bar()
        StatisticsAbbre.cardPlannedTo = QtWidgets.QLabel("", parent.status_bar)
        StatisticsAbbre.sched = QtWidgets.QLabel("", parent.status_bar)
        StatisticsAbbre.notmem = QtWidgets.QLabel("", parent.status_bar)
        StatisticsAbbre.act = QtWidgets.QLabel("", parent.status_bar)
        StatisticsAbbre.abbreSched = QtWidgets.QLabel("", parent.status_bar)
        parent.add_to_status_bar(StatisticsAbbre.cardPlannedTo)
        parent.add_to_status_bar(StatisticsAbbre.abbreSched)
        parent.add_to_status_bar(StatisticsAbbre.sched)
        parent.add_to_status_bar(StatisticsAbbre.notmem)
        parent.add_to_status_bar(StatisticsAbbre.act)

        if card:
            dayPlaned = int(math.ceil((card.next_rep-card.last_rep)/86400.0))
            cardPlanedToDay = "In:"+str(dayPlaned)
            if dayPlaned >= 1 and dayPlaned <= StatisticsAbbre.showSchedDay:
                StatisticsAbbre.schedNum[dayPlaned-1]+=1
        else:
            cardPlanedToDay = "In:?"
        StatisticsAbbre.cardPlannedTo.setText(cardPlanedToDay)

        scheduled_count, non_memorised_count, active_count = mySelf.review_controller().counters()
        StatisticsAbbre.sched.setText("Sched:"+str(scheduled_count))
        StatisticsAbbre.notmem.setText("Not:"+str(non_memorised_count))
        StatisticsAbbre.act.setText("Act:"+str(active_count))
        abbreSchedText = ""
        if StatisticsAbbre.showSchedDay >=1:
            abbreSchedText += "Ft:[" + str(StatisticsAbbre.schedNum[0])
        sizePerGroup = StatisticsAbbre.sizePerGroup
        for i in range(2, StatisticsAbbre.showSchedDay+1):
            if i % sizePerGroup == 1:
                abbreSchedText += "["
            else:
                abbreSchedText += "/"
            abbreSchedText += str(StatisticsAbbre.schedNum[i-1])
            if i % sizePerGroup == 0:
                abbreSchedText += "]"
        if StatisticsAbbre.showSchedDay % sizePerGroup != 0:
            abbreSchedText += "]"
        StatisticsAbbre.abbreSched.setText(abbreSchedText)

    globalRun = staticmethod(globalRun)


class StatisticsAbbre(Plugin):
    
    name = "Statistics Abbreviation"
    version = "1.0"
    # you can modify the two numbers here
    showSchedDay = 15
    sizePerGroup = 5
    description = "Show statistics abbreviations on the right of the status bar. (v" + version + ")\n\n" + \
                  "All abbreviations are listed as follows:\n\n" + \
                  "In: The previously graded card will show up again IN how many days. Unavailable when there is no such card.\n" + \
                  "Ft: The numbers of scheduled cards in the FUTURE. The default will show " + str(showSchedDay) + " day(s) and make " + str(sizePerGroup) +  " day(s) a grounp.\n" + \
                  "Sched: The number of SCHEDULED cards today.\n" + \
                  "Not: The number of NOT memorized cards.\n" + \
                  "Act: The number of ACTIVE cards.\n\n" + \
                  "Limitation: The status bar is only displayed/updated after you grade a card or after the displayed fields (e.g. Q/A) is changed (due to appearance of a new card or changes made to the current card).\n\n" + \
                  "Note: Don't activate the plugin with Cramming Scheduler Plugin."
    components = [ShowStatsAbbreFilter, ShowStatsAbbreHook]
    activeCardNum = -1
    sched = None
    notmem = None
    act = None
    abbreSched = None
    cardPlannedTo = None
    firstHook = False
    schedNum = []
    supported_API_level = 2

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        self.parent = self.main_widget()
        StatisticsAbbre.sched = None
        StatisticsAbbre.notmem = None
        StatisticsAbbre.act = None
        StatisticsAbbre.abbreSched = None
        StatisticsAbbre.cardPlannedTo = None
        StatisticsAbbre.firstHook = False
        StatisticsAbbre.activeCardNum = -1

    def activate(self):
        Plugin.activate(self)
        StatisticsAbbre.schedNum = []
        for i in range(1,StatisticsAbbre.showSchedDay+1):
            StatisticsAbbre.schedNum.append(0)
        self.render_chain("default").\
            register_filter_at_front(ShowStatsAbbreFilter)
        if StatisticsAbbre.firstHook:
            ShowStatsAbbreHook.globalRun(self)

    def deactivate(self):
        Plugin.deactivate(self)
        self.parent.clear_status_bar()
        StatisticsAbbre.sched = None
        StatisticsAbbre.notmem = None
        StatisticsAbbre.act = None
        StatisticsAbbre.abbreSched = None
        StatisticsAbbre.cardPlannedTo = None
        StatisticsAbbre.activeCardNum = -1
        self.render_chain("default").\
            unregister_filter(ShowStatsAbbreFilter)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(StatisticsAbbre)

