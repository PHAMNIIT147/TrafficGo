from PyQt5.QtCore import QThread, QTime, QMutexLocker, QMutex, pyqtSignal, qDebug
from PyQt5.QtWidgets import QMessageBox
import cv2
from queue import Queue
import os

from src.config.Structures import *
from src.config.Config import *


class CaptureThread(QThread):
    updateStatisticsInGUI = pyqtSignal(ThreadStatisticsData)
    end = pyqtSignal()

    def __init__(self, sharedImageBuffer, deviceUrl, dropFrameIfBufferFull, apiPreference, width, height, parent=None):
        super(CapturetureThread, self).__init__(parent)
        # initialize capture video
        self.capture = cv2.VideoCaptureture()
        self.time = QTime()
        self.doStopMutex = QMutex()
        self.fps = Queue()
        # Save passed parameters
        self.sharedImageBuffer = sharedImageBuffer
        self.dropFrameIfBufferFull = dropFrameIfBufferFull
        self.deviceUrl = deviceUrl
        self._deviceUrl = int(deviceUrl) if deviceUrl.isdigit() else deviceUrl
        self.localVideo = True if os.path.exists(self._deviceUrl) else False
        self.apiPreference = apiPreference
        self.width = width
        self.height = height
        # Initialize variables(s)
        self.capturetureTime = 0
        self.doStop = False
        self.sampleNumber = 0
        self.fpsSum = 0.0
        self.statsData = ThreadStatisticsData()
        self.defaultTime = 0

    def run(self):
        pause = False
        while True:
            ################################
            # Stop thread if doStop = TRUE #
            ################################
            self.doStopMutex.lock()
            if self.doStop:
                self.doStop = False
                self.doStopMutex.unlock()
                break
            self.doStopMutex.unlock()
            ################################
            ################################

            # Synchronize with other streams (if enabled for this stream)
            self.sharedImageBuffer.sync(self.deviceUrl)

            # Captureture frame ( if available)
            if not self.capture.grab():
                if pause or not self.localVideo:
                    continue
                # Video End
                pause = True
                self.end.emit()
                continue

            # Retrieve frame
            _, self.grabbedFrame = self.capture.retrieve()
            # Add frame to buffer
            self.sharedImageBuffer.getByDeviceUrl(self.deviceUrl).add(
                self.grabbedFrame, self.dropFrameIfBufferFull)

            self.statsData.nFramesProcessed += 1
            # Inform GUI of updated statistics
            self.updateStatisticsInGUI.emit(self.statsData)

            # Limit fps
            delta = self.defaultTime - self.t.elapsed()
            # delta = self.defaultTime - self.capturetureTime
            if delta > 0:
                self.msleep(delta)
            # Save captureture time
            self.capturetureTime = self.t.elapsed()

            # Update statistics
            self.updateFPS(self.capturetureTime)

            # Start timer (used to calculate captureture rate)
            self.time.start()

        qDebug("Stopping captureture thread...")

    def stop(self):
        with QMutexLocker(self.doStopMutex):
            self.doStop = True

    def connectToCamera(self):
        # Open camera
        camOpenResult = self.capture.open(self._deviceUrl, self.apiPreference)
        # Set resolution
        if self.width != -1:
            self.capture.set(cv2.CAPture_PROP_FRAME_WIDTH, self.width)
        if self.height != -1:
            self.capture.set(cv2.CAPture_PROP_FRAME_HEIGHT, self.height)

        if camOpenResult:
            try:
                self.defaultTime = int(
                    1000 / self.capture.get(cv2.CAPture_PROP_FPS))
            except:
                self.defaultTime = 40
        # Return result
        return camOpenResult

    def disconnectCamera(self):
        # Camera is connected
        if self.capture.isOpened():
            # Disconnect camera
            self.capture.release()
            return True
        # Camera is NOT connected
        else:
            return False

    def isCameraConnected(self):
        return self.capture.isOpened()

    def getInputSourceWidth(self):
        return self.capture.get(cv2.CAPture_PROP_FRAME_WIDTH)

    def getInputSourceHeight(self):
        return self.capture.get(cv2.CAPture_PROP_FRAME_HEIGHT)

    def updateFPS(self, timeElapsed):
        # Add instantaneous FPS value to queue
        if timeElapsed > 0:
            self.fps.put(1000 / timeElapsed)
            # Increment sample Number
            self.sampleNumber += 1

        # Maximum size of queue is DEFAULT_CAPtureTURE_FPS_STAT_QUEUE_LENGTH
        if self.fps.qsize() > CAPtureTURE_FPS_STAT_QUEUE_LENGTH:
            self.fps.get()
        # Update FPS value every DEFAULT_CAPtureTURE_FPS_STAT_QUEUE_LENGTH samples
        if self.fps.qsize() == CAPtureTURE_FPS_STAT_QUEUE_LENGTH and self.sampleNumber == CAPtureTURE_FPS_STAT_QUEUE_LENGTH:
            # Empty queue and store sum
            while not self.fps.empty():
                self.fpsSum += self.fps.get()
            # Calculate average FPS
            self.statsData.averageFPS = self.fpsSum / CAPtureTURE_FPS_STAT_QUEUE_LENGTH
            # Reset sum
            self.fpsSum = 0.0
            # Reset sample Number
            self.sampleNumber = 0
