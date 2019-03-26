import unittest
import sys
sys.path.append("..")
sys.path.append("..\..")
from Pycasso.Core.Password_Manager import Password_Manager as PM

#Fixtures
TEST_PASSWORD = "Password!"
def get_password_manager():
    manager = PM(salt = "salt")
    return manager

#Test Password Manager
class TestPasswordManager(unittest.TestCase):

    def test_crypt(self):
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")

    def test_verifyhash(self):
        #hash password and then verify hash works
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")
        #assert hash verification
        self.assertTrue(manager.sha512_verify(TEST_PASSWORD, hash))

    def test_failhash(self):
        #hash password and then verify hash fails with different password
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")
        #assert hash failure
        self.assertFalse(manager.sha512_verify("Another Password", hash))

if __name__ == '__main__':
    unittest.main()
        