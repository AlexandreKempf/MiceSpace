from PySide.QtGui import *
import PySide.QtCore as QtCore
import os,sys
import pyqtgraph as pg
import datetime

import csv
import os
import numpy as np
import datetime
import glob as glob

###### USER READ
# os.listdir(d)

def ensure_dir(dir):
    """
    Test is DIR exist and if not create it
    """
    if not os.path.exists(dir):
        os.makedirs(dir)

# .strftime("%d %b %Y")
    # now=datetime.date.today()
    # daypostbirth = (now-birth).days

def returnmouseinfo(filepath):
    infofile = open(filepath,"r")
    infos = infofile.readlines()
    headers = ["USER","CAGE","NUMBER","NAME","GENOTYPE","DATE_ARR","DATE_CHIR","DATE_OUT","CHIR_LOC","COMMENTS"]
    returndico={}

    for irow in np.arange(len(headers)):
        idx = int(np.where([iheader in infos[irow] for iheader in headers])[0])
        returndico[headers[idx]] = infos[irow][len(headers[idx])+2:-1]

    if len(returndico["DATE_ARR"])>0:
        returndico["DATE_ARR"] = datetime.date(int(returndico["DATE_ARR"][-4:]),int(returndico["DATE_ARR"][3:5]),int(returndico["DATE_ARR"][0:2]))
    if len(returndico["DATE_CHIR"])>0:
        returndico["DATE_CHIR"] = datetime.date(int(returndico["DATE_CHIR"][-4:]),int(returndico["DATE_CHIR"][3:5]),int(returndico["DATE_CHIR"][0:2]))
    if len(returndico["DATE_OUT"])>0:
        returndico["DATE_OUT"] = datetime.date(int(returndico["DATE_OUT"][-4:]),int(returndico["DATE_OUT"][3:5]),int(returndico["DATE_OUT"][0:2]))

    returndico["WEIGHT"]=[]
    limit=int(np.where(["WEIGHT" in row for row in infos])[0])
    infos=infos[limit+1:]
    for date in infos:
        listweight = str.split(date, sep=""";""")[:-1]
        listweight[0] = datetime.date(int(listweight[0][-4:]),int(listweight[0][3:5]),int(listweight[0][0:2]))
        returndico["WEIGHT"].append(listweight)
    infofile.close()
    return returndico

# returnmouseinfo("""/home/alexandre/docs/servertest/micespace/Alexandre/Al001/01/mouseinfo.txt""")

def listmice(serverpath):
    filename="mouseinfo.txt"
    listofinfos=glob.glob(serverpath + 3*"*/" + filename)
    return listofinfos

# listmice("/home/alexandre/docs/servertest/micespace/")

def exist(dir,file,iter=10):
    """
    Is there FILE in DIR or in its ITER subfolder
    """
    answer = ""
    for i in np.arange(iter):
        if len(glob.glob(dir + i*"*/" + file))>0:
            answer = glob.glob(dir + i*"*/" + file)[0]
    return answer


class MiceSpace(QWidget):

    def __init__(self):
        super(MiceSpace, self).__init__()
        self.initUI()
        self.save()

    def initUI(self):
        self.setGeometry(50,50,1000,1000)
        self.setWindowTitle('MiceSpace')
        self.serverpath = "/home/alexandre/docs/servertest/micespace/"
        # self.setWindowIcon(QIcon('icon.png'))

        self.mainwin()

        self.show()

    def mainwin(self):
        self.welcometxt = QLabel(u"Welcome in MiceSpace \n" + datetime.date.today().strftime("%d %b %Y"), self)

        # Criteria
        self.activebutton = QCheckBox(u"Active Mice",self)
        self.activebutton.stateChanged.connect(self.refreshtable)

        self.userbutton = QCheckBox(u"",self)
        self.userbutton.stateChanged.connect(self.refreshtable)
        self.userselect = QComboBox(self)
        self.userselect.addItems(os.listdir(self.serverpath))
        self.userselect.activated.connect(self.userselectfun)

        self.cagebutton = QCheckBox(u"",self)
        self.cagebutton.stateChanged.connect(self.refreshtable)
        self.cageselect = QComboBox(self);
        self.cageselect.activated.connect(self.cageselectfun)



        #Table
        self.table = QTableWidget(100, 4, self)
        self.table.setHorizontalHeaderLabels(["Cage","Index","Weight","Add event"])
        listoffile = listmice(self.serverpath)
        self.miceinfos = []
        for i in listoffile:
            idico = returnmouseinfo(i)
            iname = idico["NAME"]
            inumber = idico["NUMBER"]
            icage = idico["CAGE"]
            iuser = idico["USER"]
            idate_arr = idico["DATE_ARR"]
            idate_chir = idico["DATE_CHIR"]
            igenotype = idico["GENOTYPE"]
            icomments = idico["COMMENTS"]
            idate_out = idico["DATE_OUT"]
            if not idico["DATE_OUT"]:
                ialive = True
            else:
                ialive = False
            iweight = idico["WEIGHT"]
            self.miceinfos.append([iuser,icage,inumber,iname,ialive,iweight,idate_arr,idate_chir,igenotype,icomments,idate_out])
        # to refresh the table with only active mice
        self.activebutton.setCheckState(QtCore.Qt.Checked)

        self.table.cellChanged.connect(self.cellchangeddate)

        self.table.cellClicked.connect(self.cellchangeinfos)

        #################### LEFT PART
        self.tableuser = "None"
        self.tablecage = "None"
        self.tablename = "None"
        self.tablenumber = "None"
        self.tablegenotype = "None"
        self.tabledate_arr = "None"
        self.tabledate_chir = "None"
        self.tabledate_out = "None"
        self.tablecomments = "None"
        self.infostxt = QLabel(u"user : " + self.tableuser +
                                              "\ncage : " + self.tablecage +
                                              "\nname : " + self.tablenumber + "_" + self.tablename +
                                              "\ngenotype : " + self.tablegenotype +
                                              "\ndate of arrival : " + self.tabledate_arr +
                                              "\ndate of surgery : " + self.tabledate_chir +
                                              "\ndate of death : " + self.tabledate_out +
                                              "\ncomments : " + self.tablecomments, self)

        self.refreshinfos()


        self.graphic = QWidget(self)
        self.graphic.setMinimumSize(500,500)
        self.plotwid = pg.PlotWidget(name="weight",parent=self.graphic)
        self.plotwid.setMinimumSize(500,500)
        self.plotwid.showGrid(x=True,y=True)
        self.plot = self.plotwid.plot(symbol='o')
        self.plot.setData(x=[], y=[])


        self.newmousebut = QPushButton(u"Add a mouse",self)
        self.newmousebut.clicked.connect(self.addmousefunction)

        ########################################################################
        ############################   LAYOUT   ################################
        ########################################################################

        # CRITERIA BOX
        self.lay_criteria = QGroupBox("Criteria")

        crit_usr = QHBoxLayout()
        crit_usr.addWidget(self.userbutton)
        crit_usr.addWidget(self.userselect)
        crit_usr.addStretch(1)

        crit_cage = QHBoxLayout()
        crit_cage.addWidget(self.cagebutton)
        crit_cage.addWidget(self.cageselect)
        crit_cage.addStretch(1)

        crit_box = QVBoxLayout()
        crit_box.addWidget(self.activebutton)
        crit_box.addLayout(crit_usr)
        crit_box.addLayout(crit_cage)
        self.lay_criteria.setLayout(crit_box)


        self.layout_left = QVBoxLayout()
        self.layout_left.addWidget(self.lay_criteria)
        self.layout_left.addWidget(self.table)

        self.layout_Hnewmouse = QHBoxLayout()
        self.layout_Hnewmouse.addStretch(1)
        self.layout_Hnewmouse.addWidget(self.newmousebut)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(self.infostxt)
        self.layout_right.addWidget(self.graphic)
        self.layout_right.addStretch(1)
        self.layout_right.addLayout(self.layout_Hnewmouse)


        self.layout_split = QHBoxLayout()
        self.layout_split.addLayout(self.layout_left)
        self.layout_split.addLayout(self.layout_right)


        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.welcometxt)
        self.layout_main.addLayout(self.layout_split)


        self.setLayout(self.layout_main)


    def selectinfos(self):
        # ACTIVE STATE
        self.miceinfoscurrent = self.miceinfos
        if self.activebutton.isChecked():
            isalivebool = [mouse[4] for mouse in self.miceinfos]
            self.miceinfoscurrent = [self.miceinfos[i] for i in np.where(np.array(isalivebool)==True)[0]]
        # USER
        if self.userbutton.isChecked():
            user = self.userselect.currentText()
            mouseusers = [mouse[0] for mouse in self.miceinfoscurrent]
            self.miceinfoscurrent = [self.miceinfoscurrent[i] for i in np.where(np.array(mouseusers)==user)[0]]
        # CAGE
        if self.cagebutton.isChecked():
            cage = self.cageselect.currentText()
            mousecage = [mouse[1] for mouse in self.miceinfoscurrent]
            self.miceinfoscurrent = [self.miceinfoscurrent[i] for i in np.where(np.array(mousecage)==cage)[0]]
        return self

    def refreshtable(self):
        self.selectinfos()
        nrow = len(self.miceinfoscurrent)
        self.table.setRowCount(nrow)
        # sort the row for alphabetical order
        self.miceinfoscurrent = [self.miceinfoscurrent[i] for i in np.argsort([mouse[1]+mouse[2] for mouse in self.miceinfoscurrent])]
        for i in np.arange(nrow):
            mouse = self.miceinfoscurrent[i]
            cage = QTableWidgetItem(mouse[1])
            idx = QTableWidgetItem(mouse[2] + """_"""+ mouse[3])
            self.table.setItem(i,0,cage)
            self.table.setItem(i,1,idx)
            # Color
            listuser = os.listdir(self.serverpath)
            colors = [[255,85,85],[255,127,42],[255,221,85],[85,255,85],[95,188,211],[170,135,222]]
            useridx = int(np.where(np.array([user == mouse[0] for user in listuser]))[0])
            # set color for the user
            color = colors[useridx]
            # variant for the cages
            cages = os.listdir(self.serverpath+mouse[0])
            alphavect = np.linspace(255,100,len(cages)).astype("int")
            color = QColor(color[0],color[1],color[2],alphavect[int(mouse[1][2:])-1])
            self.table.item(i, 0).setBackground(color)


            date = [element[0] for element in mouse[5]]
            if len(date)>0:
                if date[-1] == datetime.date.today():
                    if len(mouse[5][-1][1]) != 0:
                        weight = QTableWidgetItem(str(int(mouse[5][-1][1])))
                        self.table.setItem(i,2,weight)

            event = QTableWidgetItem("            +            ")
            self.table.setItem(i,3,event)
        return self

    def userselectfun(self):
        self.user = self.userselect.currentText()
        self.userbutton.setCheckState(QtCore.Qt.Checked)
        self.cageselect.clear()
        self.cageselect.addItems(os.listdir(self.serverpath+self.user))
        self.refreshtable()
        return self

    def cageselectfun(self):
        self.cage = self.cageselect.currentText()
        self.cagebutton.setCheckState(QtCore.Qt.Checked)
        self.refreshtable()
        return self


    def cellchangeddate(self,irow,icol):
        if icol == 2:
            # modify miceinfocurrent
            newdatum = [datetime.date.today(),self.table.item(irow,icol).text(),'']
            # self.miceinfoscurrent[irow][5].append(newdatum)

            # modify miceinfo
            iuser,icage,inumber,iname = self.miceinfoscurrent[irow][0:4]
            userbool = [mouse[0]==iuser for mouse in self.miceinfos]
            cagebool = [mouse[1]==icage for mouse in self.miceinfos]
            numberbool = [mouse[2]==inumber for mouse in self.miceinfos]
            idx = int(np.where(np.array(userbool) & np.array(cagebool) & np.array(numberbool))[0])
            self.miceinfos[idx][5].append(newdatum)

            weightchange_file_read = open(self.serverpath+iuser+"/"+icage+"/"+inumber+"_"+iname+"/"+"mouseinfo.txt","r")
            weightchange_file = weightchange_file_read.readlines()
            weightchange_file_read.close()

            idx_weight_limit = int(np.where(["WEIGHT" in row for row in weightchange_file])[0])
            # idx_weight = np.arange(idx_weight_limit,len(event_file))
            days = [datetime.date(int(i[6:10]),int(i[3:5]),int(i[0:2])) for i in weightchange_file[idx_weight_limit+1:]]
            if datetime.date.today() in days:
                elements = weightchange_file[-1].split(";")
                weightchange_file[-1] = str.join(";",(elements[0],self.table.item(irow,icol).text(),elements[2]))+";\n"
            else:
                day = str(datetime.date.today().day)
                if len(day)==1:
                    day = "0"+day
                month = str(datetime.date.today().month)
                if len(month)==1:
                    month = "0"+month
                year = str(datetime.date.today().year)
                event = day + "/" + month + "/" + year + ";" + self.table.item(irow,icol).text() + ";;\n"
                weightchange_file.append(event)

            weightchange_file_write = open(self.serverpath+iuser+"/"+icage+"/"+inumber+"_"+iname+"/"+"mouseinfo.txt","w")
            for i in weightchange_file:
                weightchange_file_write.write(i)
            weightchange_file_write.close()
        return self

    def cellchangeinfos(self,irow,icol):
        if icol == 0:
            iuser,icage,inumber,iname,ialive,iweight,idate_arr,idate_chir,igenotype,icomments,idate_out = self.miceinfoscurrent[irow]
            self.tableuser = iuser
            self.tablecage = icage[2:]
            self.tablename = iname
            self.tablenumber = inumber
            self.tablegenotype = igenotype
            self.tabledate_arr = idate_arr.strftime("%d %b %Y")
            if idate_chir:
                self.tabledate_chir = idate_chir.strftime("%d %b %Y")
            else:
                self.tabledate_chir = "None"
            if idate_out:
                self.tabledate_out = idate_out.strftime("%d %b %Y")
            else:
                self.tabledate_out = "None"
            self.tablecomments = icomments
            self.refreshinfos()

            # Plot weight
            weight = np.array([listdate[1] for listdate in iweight])
            length = np.array([len(i) for i in weight])
            if 0 in length:
                weight = np.where(length == 0, np.zeros(len(weight)), weight)
                weight = weight.astype(np.float)
                weight = np.where(weight == 0, np.repeat(np.nan,len(weight)),weight )
            else:
                weight = weight.astype(np.float)
            datex = np.array([listdate[0].toordinal() for listdate in iweight])
            datelabel = [listdate[0] for listdate in iweight]
            event = [listdate[2] for listdate in iweight]
            if len(datex)>0:
                datex -= datex[0]
            else:
                datex=[]
                weight=[]
                event=[]

            self.plotwid.clear()
            self.plot = self.plotwid.plot(symbol='o')
            self.plot.setData(x=datex, y=weight)

            anchorlvl = -2
            for i,txt in enumerate(event):
                if len(txt) > 0:
                    text = pg.TextItem(txt, anchor=(0,anchorlvl), border='w', fill=(50, 50, 100, 200))
                    self.plotwid.addItem(text)
                    text.setPos(datex[i], np.nanmax(weight))
                    line = pg.InfiniteLine(datex[i],angle=90, movable=False)
                    self.plotwid.addItem(line)
                    if anchorlvl == -2:
                        anchorlvl = -4
                    else:
                        anchorlvl = -2
        if icol==3:
            self.event_user = self.miceinfoscurrent[irow][0]
            self.event_cage = self.miceinfoscurrent[irow][1]
            self.event_idx = self.miceinfoscurrent[irow][2]
            self.event_name = self.miceinfoscurrent[irow][3]
            self.calendarwin = QWidget(None)
            self.calendarwin.setGeometry(50,50,600,300)
            self.eventline = QLineEdit(self.calendarwin)
            self.calendarwid = QCalendarWidget(self.calendarwin)
            self.saveevent = QPushButton(u"Create",self.calendarwin)
            self.saveevent.clicked.connect(self.createevent)
            self.layout_calendarwin = QVBoxLayout()
            self.layout_calendarwin.addWidget(self.eventline)
            self.layout_calendarwin.addWidget(self.calendarwid)
            self.layout_calendarwin.addWidget(self.saveevent)
            self.calendarwin.setLayout(self.layout_calendarwin)
            self.calendarwin.show()
            self.irow = irow
        return self

    def createevent(self):
        self.event_date = datetime.date(self.calendarwid.selectedDate().year(),self.calendarwid.selectedDate().month(),self.calendarwid.selectedDate().day())
        self.event_str = self.eventline.text()

        event_file_read = open(self.serverpath+self.event_user+"/"+self.event_cage+"/"+self.event_idx+"_"+self.event_name+"/"+"mouseinfo.txt","r")
        event_file = event_file_read.readlines()
        event_file_read.close()

        idx_weight_limit = int(np.where(["WEIGHT" in row for row in event_file])[0])
        # idx_weight = np.arange(idx_weight_limit,len(event_file))
        days = [datetime.date(int(i[6:10]),int(i[3:5]),int(i[0:2])) for i in event_file[idx_weight_limit+1:]]
        if self.event_date in days:
            idx_date = int(np.where(np.array(days) == self.event_date)[0]) + int(np.where(["WEIGHT" in row for row in event_file])[0]) + 1
            event_file[idx_date] = event_file[idx_date][:-2] + self.event_str + ";\n"
        else:
            day = str(self.event_date.day)
            if len(day)==1:
                day = "0"+day
            month = str(self.event_date.month)
            if len(month)==1:
                month = "0"+month
            year = str(self.event_date.year)
            event = day + "/" + month + "/" + year + ";;" + self.event_str + ";\n"

            if len(np.where(np.array(days) > self.event_date)[0]) > 0:
                idx_date = int(np.where(np.array(days) > self.event_date)[0][0]) + int(np.where(["WEIGHT" in row for row in event_file])[0]) + 1
                event_file.insert(idx_date,event)
            else:
                event_file.append(event)

        event_file_write = open(self.serverpath+self.event_user+"/"+self.event_cage+"/"+self.event_idx+"_"+self.event_name+"/"+"mouseinfo.txt","w")

        for i in np.arange(len(event_file)):
            event_file_write.write(event_file[i])
        event_file_write.close()

        listoffile = listmice(self.serverpath)
        self.miceinfos = []
        for i in listoffile:
            idico = returnmouseinfo(i)
            iname = idico["NAME"]
            inumber = idico["NUMBER"]
            icage = idico["CAGE"]
            iuser = idico["USER"]
            idate_arr = idico["DATE_ARR"]
            idate_chir = idico["DATE_CHIR"]
            igenotype = idico["GENOTYPE"]
            icomments = idico["COMMENTS"]
            idate_out = idico["DATE_OUT"]
            if not idico["DATE_OUT"]:
                ialive = True
            else:
                ialive = False
            iweight = idico["WEIGHT"]
            self.miceinfos.append([iuser,icage,inumber,iname,ialive,iweight,idate_arr,idate_chir,igenotype,icomments,idate_out])

        self.refreshtable()
        self.cellchangeinfos(self.irow,0)
        self.calendarwin.close()

    def refreshinfos(self):
        self.infostxt.setText(u"user : " + self.tableuser +
                                              "\ncage : " + self.tablecage +
                                              "\nname : " + self.tablenumber + "_" + self.tablename +
                                              "\ngenotype : " + self.tablegenotype +
                                              "\ndate of arrival : " + self.tabledate_arr +
                                              "\ndate of surgery : " + self.tabledate_chir +
                                              "\ndate of death : " + self.tabledate_out +
                                              "\ncomments : " + self.tablecomments)
        return self


    def addmousefunction(self):
        self.newmousewindow = QWidget()
        self.newmousewindow.setGeometry(50,50,300,300)
        self.newmousewindow.show()
        self.ADFtitle = QLabel(u"Fill the form to add a new mouse to the database", self.newmousewindow )
        self.ADFline1 = QLabel(u"user : ", self.newmousewindow)
        self.ADFline2 = QLabel(u"cage number : ", self.newmousewindow)
        self.ADFline3 = QLabel(u"mouse number : ", self.newmousewindow)
        self.ADFline4 = QLabel(u"mouse name : ", self.newmousewindow)
        self.ADFline5 = QLabel(u"genotype : ", self.newmousewindow)
        self.ADFline6 = QLabel(u"date of arrival (dd/mm/yyyy) : ", self.newmousewindow)
        self.ADFline7 = QLabel(u"date of surgery (dd/mm/yyyy) : ", self.newmousewindow)
        self.ADFline8 = QLabel(u"surgery localization :", self.newmousewindow)
        self.ADFline9 = QLabel(u"comments : ", self.newmousewindow)

        self.ADFline1fill = QLineEdit(self.newmousewindow)
        self.ADFline2fill = QLineEdit(self.newmousewindow)
        self.ADFline3fill = QLineEdit(self.newmousewindow)
        self.ADFline4fill = QLineEdit(self.newmousewindow)
        self.ADFline5fill = QLineEdit(self.newmousewindow)
        self.ADFline6fill = QLineEdit(self.newmousewindow)
        self.ADFline7fill = QLineEdit(self.newmousewindow)
        self.ADFline8fill = QLineEdit(self.newmousewindow)
        self.ADFline9fill = QLineEdit(self.newmousewindow)

        self.ADFsavebutton = QPushButton(u"Save",self.newmousewindow)
        self.ADFsavebutton.clicked.connect(self.ADFsavefunction)


        self.layout_ADFline1 = QHBoxLayout()
        self.layout_ADFline1.addWidget(self.ADFline1)
        self.layout_ADFline1.addWidget(self.ADFline1fill)

        self.layout_ADFline2 = QHBoxLayout()
        self.layout_ADFline2.addWidget(self.ADFline2)
        self.layout_ADFline2.addWidget(self.ADFline2fill)

        self.layout_ADFline3 = QHBoxLayout()
        self.layout_ADFline3.addWidget(self.ADFline3)
        self.layout_ADFline3.addWidget(self.ADFline3fill)

        self.layout_ADFline4 = QHBoxLayout()
        self.layout_ADFline4.addWidget(self.ADFline4)
        self.layout_ADFline4.addWidget(self.ADFline4fill)

        self.layout_ADFline5 = QHBoxLayout()
        self.layout_ADFline5.addWidget(self.ADFline5)
        self.layout_ADFline5.addWidget(self.ADFline5fill)

        self.layout_ADFline6 = QHBoxLayout()
        self.layout_ADFline6.addWidget(self.ADFline6)
        self.layout_ADFline6.addWidget(self.ADFline6fill)

        self.layout_ADFline7 = QHBoxLayout()
        self.layout_ADFline7.addWidget(self.ADFline7)
        self.layout_ADFline7.addWidget(self.ADFline7fill)

        self.layout_ADFline8 = QHBoxLayout()
        self.layout_ADFline8.addWidget(self.ADFline8)
        self.layout_ADFline8.addWidget(self.ADFline8fill)

        self.layout_ADFline9 = QHBoxLayout()
        self.layout_ADFline9.addWidget(self.ADFline9)
        self.layout_ADFline9.addWidget(self.ADFline9fill)

        self.layout_ADFall = QVBoxLayout()
        self.layout_ADFall.addWidget(self.ADFtitle)
        self.layout_ADFall.addLayout(self.layout_ADFline1)
        self.layout_ADFall.addLayout(self.layout_ADFline2)
        self.layout_ADFall.addLayout(self.layout_ADFline3)
        self.layout_ADFall.addLayout(self.layout_ADFline4)
        self.layout_ADFall.addLayout(self.layout_ADFline5)
        self.layout_ADFall.addLayout(self.layout_ADFline6)
        self.layout_ADFall.addLayout(self.layout_ADFline7)
        self.layout_ADFall.addLayout(self.layout_ADFline8)
        self.layout_ADFall.addLayout(self.layout_ADFline9)
        self.layout_ADFall.addWidget(self.ADFsavebutton)
        self.newmousewindow.setLayout(self.layout_ADFall)

    def ADFsavefunction(self):
        NEWuser = self.ADFline1fill.text()
        NEWcage = self.ADFline2fill.text()
        NEWidx = self.ADFline3fill.text()
        NEWname = self.ADFline4fill.text()
        NEWgenotype = self.ADFline5fill.text()
        NEWdate_arr = self.ADFline6fill.text()
        NEWdate_chir = self.ADFline7fill.text()
        NEWchir_loc = self.ADFline8fill.text()
        NEWcomment = self.ADFline9fill.text()

        if len(NEWcage)>3:
            NEWcage = NEWcage[-3:]
        elif len(NEWcage) == 2:
            NEWcage = "0" + NEWcage
        elif len(NEWcage) == 1:
            NEWcage = "00" + NEWcage

        NEWcage = NEWuser.title()[0:2] + NEWcage

        if len(NEWidx) == 1:
            NEWidx = "0" + NEWidx

        ensure_dir(self.serverpath+(NEWuser).title())
        ensure_dir(self.serverpath+(NEWuser).title()+"/"+NEWcage)
        ensure_dir(self.serverpath+(NEWuser).title()+"/"+NEWcage+"/"+NEWidx+"_"+(NEWname).title())
        NEWfile = open(self.serverpath+(NEWuser).title()+"/"+NEWcage+"/"+NEWidx+"_"+(NEWname).title()+"/"+"mouseinfo.txt","w")

        if len(NEWdate_arr)==8:
            NEWdate_arr = NEWdate_arr[:-2] + "20" + NEWdate_arr[-2:]
        if len(NEWdate_chir)==8:
            NEWdate_chir = NEWdate_chir[:-2] + "20" + NEWdate_chir[-2:]

        headers = ["USER","CAGE","NUMBER","NAME","GENOTYPE","DATE_ARR","DATE_CHIR","DATE_OUT","CHIR_LOC","COMMENTS", "WEIGHT"]
        info = [NEWuser.title(),NEWcage,NEWidx,NEWname.title(),NEWgenotype.title(),NEWdate_arr,NEWdate_chir,"",NEWchir_loc,NEWcomment,""]
        for i in np.arange(len(headers)):
            NEWfile.write(headers[i] + ": " + info[i] + "\n")

        NEWfile.close()
        self.newmousewindow.close()

        # refresh the table
        listoffile = listmice(self.serverpath)
        self.miceinfos = []
        for i in listoffile:
            idico = returnmouseinfo(i)
            iname = idico["NAME"]
            inumber = idico["NUMBER"]
            icage = idico["CAGE"]
            iuser = idico["USER"]
            idate_arr = idico["DATE_ARR"]
            idate_chir = idico["DATE_CHIR"]
            igenotype = idico["GENOTYPE"]
            icomments = idico["COMMENTS"]
            idate_out = idico["DATE_OUT"]
            if not idico["DATE_OUT"]:
                ialive = True
            else:
                ialive = False
            iweight = idico["WEIGHT"]
            self.miceinfos.append([iuser,icage,inumber,iname,ialive,iweight,idate_arr,idate_chir,igenotype,icomments,idate_out])

        self.refreshtable()

    def save(self):
        # attention a ne pas supprimer les evenements sans poids en ecrivant le fichier
        pass

def main():

    app = QApplication(sys.argv)
    ex = MiceSpace()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
