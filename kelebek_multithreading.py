from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import requests
import traceback
import sys
import random
import time
from functools import partial

# https://forum.learnpyqt.com/t/pause-a-running-worker-thread/147/4

# Note if shit really goes down hill, can call self.thread() to locate thread? The QRunnable class and the
# QtConcurrent::run() function are well suited to situations where we want to perform some background processing in
# one or more secondary threads without needing the full power and flexibility provided by QThread. QThread can run
# an event loop, asks that don’t need the event loop. Specifically, the tasks that are not using signal/slot
# mechanism during the task execution. Use: QtConcurrent and QThreadPool + QRunnable.
# QtConcurrent == new bae on the block?


def run_threaded_process(threadpool: QThreadPool, cb_func=None, progress_fn=None, on_complete=None, return_output=None, *args, **kwargs):
    """
    :parameter threadpool: The threadpool object you hopefully instantiated in the class.
    :parameter cb_func: the (callback) function you want to run, which must include a 'process_callback' parameter.
    Which is a signal that gets emitted back.
    :parameter progress_fn: is what you receive incrementally each time, the func sound have a param.
    :parameter on_complete: when completed exec this func without any params.
    :parameter return_output: the shit you want to return when your callback function finishes running.
    """

    worker = Worker(cb_func, *args, **kwargs)  # Any other args, kwargs are passed to the run function
    if progress_fn:
        worker.signals.progress.connect(progress_fn)
    if on_complete:
        worker.signals.result.connect(return_output)  # all signals other than finished return values.
    if return_output:
        worker.signals.finished.connect(on_complete)
    threadpool.start(worker)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exact_type, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and kwargs will be passed
    through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function :
    """

    def __init__(self, callback, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        kwargs['progress_callback'] = self.signals.progress
        # There is actually nothing in args and kwargs other than progress_callback.wtf is the point of args.
        # especially when they are immutable.

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.callback(*self.args, **self.kwargs)  # could call spinner in self.fn?
        except:
            traceback.print_exc()
            exact_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exact_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        # what is the difference this and super(Dialog, self).__init__(self, *args, **kwargs)

        self.setGeometry(QRect(200, 200, 500, 500))
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Makes Qt delete this widget when the widget has accepted the close event (see QWidget::closeEvent()).
        # Do not call int QDialog::result() const if you use this? This shit might lead to silent memory leaks

        self.threadpool = QThreadPool()
        self.worker = partial(Worker, )

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        # self.startbutton = QPushButton('Start')
        self.startbutton = QPushButton('Start', clicked=self.run)  # another way for connecting
        self.stopbutton = QPushButton('Stop')

        self.progressbar = QProgressBar()  # seems to work fine without self
        self.progressbar.setRange(0, 1)

        self.textedit = QTextEdit()
        self.textedit.append('Some Info Here')

        layout.addWidget(self.startbutton)
        layout.addWidget(self.stopbutton)
        layout.addWidget(self.progressbar)
        layout.addWidget(self.textedit)

        # self.startbutton.clicked.connect(self.run)
        self.stopbutton.clicked.connect(self.stop)

    def run_threaded_process(self, threadpool: QThreadPool, cb_func, progress_fn=None, on_complete=None, return_output=None):
        """
        threadpool: The threadpool object you hopefully instantiated in the class.
        cb_func: the (callback) function you want to run.
        progress_fn: is what you receive incrementally each time, the func sound have a param.
        on_complete: when completed exec this func without any params.
        return_output: the shit you want to return when your callback function finishes running.
        """
        # so the last two params just return optional info?

        worker = Worker(cb_func, 'http://books.toscrape.com/')  # Any other args, kwargs are passed to the run function
        if progress_fn: worker.signals.progress.connect(progress_fn)
        if on_complete: worker.signals.result.connect(return_output)  # all signals other than finished return values.
        if return_output: worker.signals.finished.connect(on_complete)
        threadpool.start(worker)

    def run(self):
        """call process"""
        self.stopped = False

        run_threaded_process(
            threadpool=self.threadpool,
            cb_func=self.execute_this_fn,
            progress_fn=self.progression_function,
            on_complete=self.completed,
            return_output=self.print_output,
            page='http://books.toscrape.com/',
        )
        # run_threaded_process(
        #     self.threadpool,
        #     self.execute_this_fn,
        #     self.progression_function,
        #     self.completed,
        #     self.print_output,
        #     'http://books.toscrape.com/',
        # )
        self.progressbar.setRange(0, 0)

    def stop(self):
        self.stopped = True
        return

    def completed(self):
        self.progressbar.setRange(0, 1)
        return

    def progression_function(self, msg):
        self.textedit.append(str(msg))
        return

    def print_output(self, s):
        print('OUTPUT: ', s)
        return s

    def execute_this_fn(self, page, progress_callback):
        # is called. Which means self.progress_fn = progress_callback
        """Do some process here"""
        resp = requests.get(page)
        # 'http://books.toscrape.com/'
        total = 50
        for i in range(0, total):
            time.sleep(.2)
            x = random.randint(1, 1000)
            progress_callback.emit(x)
            if self.stopped:
                return
        return resp.content
        # return 'The function has finished executing'  # or emit the completed.


if __name__ == '__main__':

    app = QApplication(sys.argv)
    # app.aboutToQuit.connect(worker.stop) Stopping the thread when app is closed also,
    # If you have many workers, you might prefer to connect this to a handler that will clean
    # up all the workers in one go. If you have per-window workers, you could also catch the
    # window closeEvent and stop the workers there. https://forum.learnpyqt.com/t/pause-a-running-worker-thread/147/4
    # there are also more to this.

    dial = Dialog()
    dial.show()
    sys.exit(app.exec_())
