from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json


class BlogViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.generate_blog_url = reverse('generate_blog')

    @patch('core.views.yt_title')
    @patch('core.views.get_transcription')
    @patch('core.views.generate_blog_from_transcription')
    def test_generate_blog_success(self, mock_generate_blog_from_transcription, mock_get_transcription, mock_yt_title):
        mock_yt_title.return_value = 'Test Video Title'
        mock_get_transcription.return_value = 'This is a test transcription.'
        mock_generate_blog_from_transcription.return_value = 'This is a generated blog article.'

        response = self.client.post(self.generate_blog_url,
                                    json.dumps({'link': 'https://www.youtube.com/watch?v=6tNS--WetLI'}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'content': 'This is a generated blog article.'})

    def test_generate_blog_invalid_data(self):
        response = self.client.post(self.generate_blog_url,
                                    json.dumps({'wrong_key': 'https://www.youtube.com/watch?v=6tNS--WetLI'}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid data sent'})

    @patch('core.views.get_transcription')
    def test_generate_blog_transcription_failure(self, mock_get_transcription):
        mock_get_transcription.return_value = None

        response = self.client.post(self.generate_blog_url,
                                    json.dumps({'link': 'https://www.youtube.com/watch?v=6tNS--WetLI'}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {'error': 'Failed to get transcript'})

    @patch('core.views.yt_title')
    @patch('core.views.get_transcription')
    @patch('core.views.generate_blog_from_transcription')
    def test_generate_blog_generation_failure(self, mock_generate_blog_from_transcription, mock_get_transcription,
                                              mock_yt_title):
        mock_yt_title.return_value = 'Test Video Title'
        mock_get_transcription.return_value = 'This is a test transcription.'
        mock_generate_blog_from_transcription.return_value = None

        response = self.client.post(self.generate_blog_url,
                                    json.dumps({'link': 'https://www.youtube.com/watch?v=6tNS--WetLI'}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {'error': 'Failed to generate blog article'})

    def test_generate_blog_invalid_method(self):
        response = self.client.get(self.generate_blog_url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Invalid request method'})
