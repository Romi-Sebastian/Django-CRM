from django.test import TestCase
from django.contrib.auth.models import User
from .models import Record, Note, Task


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

    def test_task_creation(self):
        self.client.login(username='testuser', password='testpass')

        task = Task.objects.create(
            record=self.record,
            user=self.user,
            title="Test title",
            due_date='2026-12-25 12:00:00'
        )

        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(task.record, self.record)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.title, 'Test title')
        self.assertEqual(task.due_date, '2026-12-25 12:00:00')

    def test_category_filter_works(self):
        # Create more records with different categories
        Record.objects.create(
            created_by=self.user, first_name='Alice', last_name='Smith', email='alice@example.com',
            phone='111', address='Addr1', city='CityA', state='SA', zipcode='10001', category='lead'
        )
        Record.objects.create(
            created_by=self.user, first_name='Bob', last_name='Johnson', email='bob@example.com',
            phone='222', address='Addr2', city='CityB', state='SB', zipcode='10002', category='client'
        )
        Record.objects.create(
            created_by=self.user, first_name='Charlie', last_name='Brown', email='charlie@example.com',
            phone='333', address='Addr3', city='CityC', state='SC', zipcode='10003', category='lead'
        )

        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/?category=lead')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 2) # Alice and Charlie
        self.assertEqual(response.context['selected_category'], 'lead')
        for record in response.context['records']:
            self.assertEqual(record.category, 'lead')
            self.assertEqual(record.created_by, self.user)

    def test_category_filter_with_search(self):
        Record.objects.create(
            created_by=self.user, first_name='Alice', last_name='Smith', email='alice@example.com',
            phone='111', address='Addr1', city='CityA', state='SA', zipcode='10001', category='lead'
        )
        Record.objects.create(
            created_by=self.user, first_name='Bob', last_name='Johnson', email='bob@example.com',
            phone='222', address='Addr2', city='CityB', state='SB', zipcode='10002', category='client'
        )
        Record.objects.create(
            created_by=self.user, first_name='Charlie', last_name='Lead', email='charlie@example.com', # Last name Lead
            phone='333', address='Addr3', city='CityC', state='SC', zipcode='10003', category='lead'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/?category=lead&q=Charlie') # Search for Charlie in lead category
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)
        self.assertEqual(response.context['records'][0].first_name, 'Charlie')
        self.assertEqual(response.context['records'][0].category, 'lead')
        self.assertEqual(response.context['selected_category'], 'lead')
        self.assertEqual(response.context['records'][0].created_by, self.user)

    def test_no_category_filter(self):
        Record.objects.create(
            created_by=self.user, first_name='Alice', last_name='Smith', email='alice@example.com',
            phone='111', address='Addr1', city='CityA', state='SA', zipcode='10001', category='lead'
        )
        Record.objects.create(
            created_by=self.user, first_name='Bob', last_name='Johnson', email='bob@example.com',
            phone='222', address='Addr2', city='CityB', state='SB', zipcode='10002', category='client'
        )
        # self.record from setUp is also present
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 3) # All records for the user
        self.assertIsNone(response.context['selected_category'])
        for record in response.context['records']:
            self.assertEqual(record.created_by, self.user)

    def test_category_filter_with_search_no_results(self):
        Record.objects.create(
            created_by=self.user, first_name='Alice', last_name='Smith', email='alice@example.com',
            phone='111', address='Addr1', city='CityA', state='SA', zipcode='10001', category='lead'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/?category=lead&q=NonExistent')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 0)
        self.assertEqual(response.context['selected_category'], 'lead')

    def test_category_filter_no_results(self):
        Record.objects.create(
            created_by=self.user, first_name='Alice', last_name='Smith', email='alice@example.com',
            phone='111', address='Addr1', city='CityA', state='SA', zipcode='10001', category='lead'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/?category=vendor') # No records with vendor category
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 0)
        self.assertEqual(response.context['selected_category'], 'vendor')


from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

class RecordFileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='filetestuser', password='testpassfile')
        self.record = Record.objects.create(
            created_by=self.user,
            first_name='FileTest',
            last_name='User',
            email='filetest@example.com',
            phone='987654321',
            address='456 File Ave',
            city='FileCity',
            state='FS',
            zipcode='54321'
        )
        self.dummy_file_content = b"This is a dummy file content."
        self.dummy_file = SimpleUploadedFile(
            name="test_file.txt",
            content=self.dummy_file_content,
            content_type="text/plain"
        )
        # Ensure media directory exists for the test
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)


    def tearDown(self):
        # Clean up created files
        # For simplicity, we're finding all files created by tests and deleting them.
        # A more robust solution would use a temporary MEDIA_ROOT.
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file_name in files:
                if file_name.startswith("test_") or "record_files" in root: # Basic check
                    try:
                        os.remove(os.path.join(root, file_name))
                    except OSError:
                        pass # Ignore if somehow already deleted or permission issue in test env

    def test_record_file_form_valid(self):
        from .forms import RecordFileForm
        form_data = {'description': 'Test file description'}
        file_data = {'file': self.dummy_file}
        form = RecordFileForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_record_file_form_invalid_no_file(self):
        from .forms import RecordFileForm
        form_data = {'description': 'Test file description without file'}
        form = RecordFileForm(data=form_data) # No file_data
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_file_upload_in_customer_record_view(self):
        self.client.login(username='filetestuser', password='testpassfile')
        response = self.client.post(
            f'/record/{self.record.pk}',
            {
                'description': 'Uploaded test file',
                'submit_file': 'Upload File' # Name of the submit button
            },
            files={'file': self.dummy_file}
        )
        self.assertEqual(response.status_code, 302) # Should redirect
        self.assertRedirects(response, f'/record/{self.record.pk}')
        
        from .models import RecordFile
        self.assertTrue(RecordFile.objects.filter(record=self.record).exists())
        uploaded_file_obj = RecordFile.objects.get(record=self.record)
        self.assertEqual(uploaded_file_obj.description, 'Uploaded test file')
        self.assertEqual(uploaded_file_obj.uploaded_by, self.user)
        self.assertTrue(os.path.exists(uploaded_file_obj.file.path))
        with open(uploaded_file_obj.file.path, 'rb') as f:
            self.assertEqual(f.read(), self.dummy_file_content)


    def test_display_attached_files(self):
        from .models import RecordFile
        # Create a file first
        test_file_obj = RecordFile.objects.create(
            record=self.record,
            uploaded_by=self.user,
            file=self.dummy_file,
            description="My test display file"
        )

        self.client.login(username='filetestuser', password='testpassfile')
        response = self.client.get(f'/record/{self.record.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('record_files', response.context)
        self.assertContains(response, test_file_obj.file.name.split('/')[-1]) # Check for filename
        self.assertContains(response, "My test display file") # Check for description

    def test_record_file_model_str(self):
        from .models import RecordFile
        file_obj = RecordFile(file=self.dummy_file, record=self.record)
        # The name includes the upload_to path initially, which is fine for __str__
        expected_str_part = self.dummy_file.name
        self.assertTrue(expected_str_part in str(file_obj))
