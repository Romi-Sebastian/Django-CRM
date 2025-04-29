from django.test import TestCase
from django.contrib.auth.models import User
from .models import Record, Note


class RecordTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a record owned by this user
        self.record = Record.objects.create(
            created_by=self.user,
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            phone='123456789',
            address='123 Test St',
            city='TestCentral',
            state='TS',
            zipcode='12345'
        )

    def test_record_creation(self):
        # Check if record exists
        record_count = Record.objects.count()
        self.assertEqual(record_count, 1)

    def test_record_owner(self):
        # Check if record is correctly linked
        self.assertEqual(self.record.created_by.username, 'testuser')

    def test_user_login(self):
        # Check if login works
        self.client.cookies.clear()
        login_successful = self.client.login(username='testuser', password='testpass')
        print(self.client)
        self.assertTrue(login_successful)

    def test_search_feature(self):
        # Check if searching works
        response = self.client.get('/?q=Test')
        self.assertEqual(response.status_code, 200)

    def test_note_creation(self):
        self.client.login(username='testuser', password='testpass')

        note = Note.objects.create(
            record=self.record,
            author=self.user,
            content="Test note"
        )

        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.record, self.record)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.content, "Test note")
