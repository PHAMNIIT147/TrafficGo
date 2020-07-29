'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-06 23:05:57
 # @ Modified by: VAA Ai Go!
 # @ Modified time: 2020-07-08 15:27:25
 # @ Description:
 '''
import qdarkstyle
from PyQt5.QtCore import Qt, QSize, qDebug, QFile, QTextStream
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QDialog, QTabWidget, QAbstractButton, qApp
from src.views.ui.ui_MainWindow import Ui_MainWindow
from src.model.SharedImageBufferModel import SharedImageBufferModel
from src.views.CameraConnectDialogView import CameraConnectDialogView
from src.views.CameraView import CameraView
from src.model.BufferModel import *
from src.utils.Config import *
import sys

APP_VERSION = "1.0.0"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Setup UI
        self.setupUi(self)
        # Create dict instead of QMapz
        self.deviceUrlDict = dict()
        self.cameraViewDict = dict()
        # Set start tab as blank
        newTab = QLabel(self.tabWidget)
        newTab.setText("No camera connected.")
        newTab.setAlignment(Qt.AlignCenter)
        self.tabWidget.addTab(newTab, "")
        self.tabWidget.setTabsClosable(False)
        # Add "Connect to Camera" button to tab
        self.connectToCameraButton = QPushButton()
        self.connectToCameraButton.setText("Connect to Camera...")
        self.tabWidget.setCornerWidget(
            self.connectToCameraButton, Qt.TopLeftCorner)
        self.connectToCameraButton.released.connect(self.connectToCamera)
        self.tabWidget.tabCloseRequested.connect(self.disconnectCamera)
        # Set focus on button
        self.connectToCameraButton.setFocus()
        # Connect other signals/slots
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(self.close)
        self.actionFullScreen.toggled.connect(self.setFullScreen)
        ## settings -> theme -> option_theme
        ## return: default theme app is white
        self.actionDark.triggered.connect(lambda: self.toggleStylesheet(DARK_STYLE))
        self.actionWhite.triggered.connect(lambda: self.toggleStylesheet(LIGHT_STYLE))
        # Create SharedImageBufferModel object
        self.sharedImageBufferModel = SharedImageBufferModel()
        # Camera number
        self.cameraNum = 0

    def connectToCamera(self):
        # Cannot connect to a camera if devices are already connected and stream synchronization is in progress
        if (self.actionSynchronizeStreams.isChecked()
                and len(self.deviceUrlDict) > 0
                and self.sharedImageBufferModel.getSyncEnabled()):
            # Prompt user
            QMessageBox.warning(self, "vehicle speed estimation and error detection",
                                "Stream synchronization is in progress.\n\n"
                                "Please close all currently open streams "
                                "before attempting to open a new stream.",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # Attempt to connect to cam
        else:
            # Get next tab index
            nextTabIndex = 0 if len(
                self.deviceUrlDict) == 0 else self.tabWidget.count()
            # Show dialog
            CameraConnectDialogView = CameraConnectDialogView(
                self, self.actionSynchronizeStreams.isChecked())
            if CameraConnectDialogView.exec() == QDialog.Accepted:
                # Save user-defined device deviceUrl
                deviceUrl = cameraConnectDialogView.getDeviceUrl()
                # Check if this camera is already connected
                if deviceUrl not in self.deviceUrlDict:
                    # Create ImageBuffer with user-defined size
                    imageBuffer = Buffer(
                        cameraConnectDialogView.gzetImageBufferSize())
                    # Add created ImageBuffer to SharedImageBufferModel object
                    self.sharedImageBufferModel.add(
                        deviceUrl, imageBuffer, self.actionSynchronizeStreams.isChecked())
                    # Create CameraView
                    cameraView = CameraView(
                        self.tabWidget, deviceUrl, self.sharedImageBufferModel, self.cameraNum)

                    # Check if stream synchronization is enabled
                    if self.actionSynchronizeStreams.isChecked():
                        # Prompt user
                        ret = QMessageBox.question(self, "vehicle speed estimation and error detection",
                                                   "Stream synchronization is enabled.\n\n"
                                                   "Do you want to start processing?\n\n"
                                                   "Choose 'No' if you would like to open "
                                                   "additional streams.",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                        # Start processing
                        if ret == QMessageBox.Yes:
                            self.sharedImageBufferModel.setSyncEnabled(True)
                        # Defer processing
                        else:
                            self.sharedImageBufferModel.setSyncEnabled(False)

                    # Attempt to connect to camera
                    if cameraView.connectToCamera(
                            cameraConnectDialogView.getDropFrameCheckBoxState(),
                            cameraConnectDialogView.getApiPreference(),
                            cameraConnectDialogView.getCaptureThreadPrio(),
                            cameraConnectDialogView.getProcessingThreadPrio(),
                            cameraConnectDialogView.getEnableFrameProcessingCheckBoxState(),
                            cameraConnectDialogView.getResolutionWidth(),
                            cameraConnectDialogView.getResolutionHeight()):

                        self.cameraNum += 1
                        # Save tab label
                        tabLabel = cameraConnectDialogView.getTabLabel()
                        # Allow tabs to be closed
                        self.tabWidget.setTabsClosable(True)
                        # If start tab, remove
                        if nextTabIndex == 0:
                            self.tabWidget.removeTab(0)
                        # Add tab
                        self.tabWidget.addTab(
                            cameraView, 'Live %s [%s]' % (tabLabel, deviceUrl))
                        self.tabWidget.setCurrentWidget(cameraView)
                        # Set tooltips
                        self.setTabCloseToolTips(
                            self.tabWidget, "Disconnect Camera")
                        # Prevent user from enabling/disabling stream synchronization
                        # after a camera has been connected
                        self.actionSynchronizeStreams.setEnabled(False)
                        # Add to map
                        self.cameraViewDict[deviceUrl] = cameraView
                        self.deviceUrlDict[deviceUrl] = nextTabIndex
                    # Could not connect to camera
                    else:
                        # Display error message
                        QMessageBox.warning(self,
                                            "ERROR:",
                                            "Could not connect to camera. "
                                            "Please check device deviceUrl.")
                        # Explicitly delete widget
                        cameraView.delete()
                        # Remove from shared buffer
                        self.sharedImageBufferModel.removeByDeviceUrl(deviceUrl)
                        # Explicitly delete ImageBuffer object
                        del imageBuffer
                # Display error message
                else:
                    QMessageBox.warning(self,
                                        "ERROR:",
                                        "Could not connect to camera. Already connected.")

    def disconnectCamera(self, index):
        # Local variable(s)
        doDisconnect = True 

        # Check if stream synchronization is enabled,
        # more than 1 camera connected,
        # and frame processing is not in progress
        if (self.actionSynchronizeStreams.isChecked()
                and len(self.cameraViewDict) > 1
                and not self.sharedImageBufferModel.getSyncEnabled()):
            # Prompt user
            ret = QMessageBox.question(self,
                                       "vehicle speed estimation and error detection",
                                       "Stream synchronization is enabled.\n\n"
                                       "Disconnecting this camera will cause frame "
                                       "processing to begin on other streams.\n\n"
                                       "Do you wish to proceed?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            # Do not disconnect
            if ret == QMessageBox.No:
                doDisconnect = False

        # Disconnect camera
        if doDisconnect:
            # Save deviceUrl of tabs
            nTabs = self.tabWidget.count()

            # Close tab
            self.tabWidget.removeTab(index)

            # get deviceUrl (key of dict)
            deviceUrl = self.getFromDictByTabIndex(self.deviceUrlDict, index)

            # Delete widget (CameraView) contained in tab
            self.cameraViewDict[deviceUrl].delete()

            # Remove from dict
            self.cameraViewDict.pop(deviceUrl)
            self.deviceUrlDict.pop(deviceUrl)

            # Update map (if tab closed is not last)
            if index != (nTabs - 1):
                self.updateDictValues(self.deviceUrlDict, index)

            # If start tab, set tab as blank
            if nTabs == 1:
                newTab = QLabel(self.tabWidget)
                newTab.setText("No camera connected.")
                newTab.setAlignment(Qt.AlignCenter)
                self.tabWidget.addTab(newTab, "")
                self.tabWidget.setTabsClosable(False)
                self.actionSynchronizeStreams.setEnabled(True)

    def showAboutDialog(self):
        QMessageBox.information(self, "About",
                                "Created by @VAA TEAM\n\n"
                                "Contact: phongpham663@gmail.com\n"
                                "Website: https://zik-iot-software-9bcf6.web.app/\n"
                                "Version: %s\n\n"
                                "Refactoring by Github@PHAMNIIT147\n\n" % APP_VERSION)

    def getFromDictByTabIndex(self, dictionary, tabIndex):
        for k, v in dictionary.items():
            if v == tabIndex:
                return k

    def updateDictValues(self, dictionary, tabIndex):
        for k, v in dictionary.items():
            if v > tabIndex:
                dictionary[k] = v - 1

    # when user button F11 or trigger full screen
    def setFullScreen(self, flag):
        if flag:
            self.showFullScreen()
        else:
            self.showNormal()

    def setTabCloseToolTips(self, tabs, tooltip):
        for item in tabs.findChildren(QAbstractButton):
            if item.inherits("CloseButton"):
                item.setToolTip(tooltip)

    def toggleStylesheet(self, path):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on system).
        :path: A full path to a resource or file on system
        '''
        if qApp is None:
            raise RuntimeError("No Qt Application found")
        file = QFile(path)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        qApp.setStyleSheet(stream.readAll())
            


