"""
Author: Peter Chen
Date: 7/22/2015
Purpose:  Confusion Matrix plot for SURI poster 2015
Source: https://www.snip2code.com/Snippet/67328/Plot-Confusion-Matrix-%28Full-Code%29
"""
import os
from matplotlib import pylab
import numpy as np

def plot_confusion_matrix(cm, classes, title):
    pylab.clf()
    pylab.matshow(cm, fignum=False, cmap='Reds')
    ax = pylab.axes()
    ax.set_xticks(range(len(classes)))
    ax.xaxis.set_ticks_position("bottom")
    ax.set_xticklabels(classes, fontsize = 24, color='black')
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize = 24, color='black')
    pylab.title(title, fontsize = 24, color='black')

    pylab.grid(True)
    pylab.xlabel('Predicted class',fontsize = 24, color = "black")
    pylab.ylabel('Actual Class',fontsize = 24, color = "black")
    pylab.text(0, 0, "0.579", fontsize = 24, horizontalalignment = 'center', \
               color='white')
    pylab.text(0, 1, "0.246", fontsize = 24, horizontalalignment = 'center', \
               color='white')
    pylab.text(1, 0, "0.175", fontsize = 24, horizontalalignment = 'center', \
               color='white')
    pylab.text(1, 1, "0.0", fontsize = 24, horizontalalignment = 'center', \
               color='black')
    pylab.show()

cm = np.array([
	[0.5789473684,0.2456140351],
	[0.1754385965,0.0]])

classes = np.array(['True Neuron', 'False Neuron'])
plot_confusion_matrix(cm, classes, "Confusion Matrix for Cell Finder")
