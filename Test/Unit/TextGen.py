import unittest
import sys
sys.path.append("..")
sys.path.append("..\..")
from Pycasso.Core.Password_Manager import Password_Manager as PM
from Pycasso.Core.Process_Queue import Process_Job as Process_Job
from Pycasso.Core.Process_Queue import Process_Queue as Process_Queue
import uuid
import time
import random
import multiprocessing as mp
from Pycasso.Core.Text_Generator import Text_Generator as TG


class Test_Text_Generation(unittest.TestCase):

    def test_text_generation(self):
        text_sequence = 'Pretty Polly the Parrot wants a cracker.'
        print('Initializing Text Generator')
        tg = TG(text_sequence, 'GPT2')
        print('Text Generator Initialization Complete')
        print('Generating result text')
        result_text = tg.generate_text(100)
        print('Printing result text')
        print(result_text)
        self.assertTrue(len(result_text) > 0)

if __name__ == '__main__':
    unittest.main()
        