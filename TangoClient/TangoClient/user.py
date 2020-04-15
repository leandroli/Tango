class User:

    def __init__(self, username='DEFAULT', password='DEFAULT'):
        self.username = username
        self.password = password

    def __str__(self):
        return '{' + '\'username\':\'{}\', \'password\':\'{}\''.format(self.username, self.password) + '}'
