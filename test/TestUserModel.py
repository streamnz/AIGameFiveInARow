import unittest
from werkzeug.security import generate_password_hash, check_password_hash
from model.user import User


class TestUserModel(unittest.TestCase):

    def test_password_hashing(self):
        # 创建用户并生成密码哈希
        password = 'Pass1234'
        user = User(username='testuser', password=password, email='test@example.com')

        # 验证存储的密码不是明文
        self.assertNotEqual(user.password, password)

        print(user.__dict__)

        # 验证生成的哈希是否有效
        self.assertTrue(check_password_hash(user.password, password))

    def test_password_hash_consistency(self):
        # 创建两个用户，使用相同的密码
        password = 'samepassword'
        user1 = User(username='user1', password=password, email='user1@example.com')
        user2 = User(username='user2', password=password, email='user2@example.com')

        # 即使密码相同，哈希也应该不同（因为每次生成哈希时使用不同的盐）
        self.assertNotEqual(user1.password, user2.password)

        # 验证两者的密码都可以正确验证
        self.assertTrue(check_password_hash(user1.password, password))
        self.assertTrue(check_password_hash(user2.password, password))


if __name__ == '__main__':
    unittest.main()
