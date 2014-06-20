import unittest
from mock import patch
from canvas_sdk.methods import sections

BASE_API_URL = 'http://hostname/api'
MAX_RESULTS = 60  # used for setting the per_page and LIMIT_PER_PAGE values
COURSE_ID = 5956  # set a fake course id for the tests


class TestSections(unittest.TestCase):

    @patch('canvas_sdk.utils.build_url')
    @patch('canvas_sdk.utils.validate_attr_is_acceptable')
    @patch('canvas_sdk.client.get')
    def test_sections_list_course_sections_returns_result_from_client(self, mock_client, mock_util, mock_build_url):
        """
        Assert that list_course_sections returned the dictionary object defined in the client mock
        """
        mock_build_url.return_value = BASE_API_URL
        mock_client.return_value = {'ok'}
        results = sections.list_course_sections(COURSE_ID)
        self.assertEquals(results, {'ok'}, 'The client call did not return the correct result.')

    @patch('canvas_sdk.utils.build_url')
    @patch('canvas_sdk.utils.validate_attr_is_acceptable')
    @patch('canvas_sdk.client.get')
    def test_sections_list_course_sections_client_called_with_include_value(self, mock_client, mock_util, mock_build_url):
        """
        Assert that list_course_sections called the client with user specified values
        for include and per_page
        """
        sections.list_course_sections(COURSE_ID, include='students', per_page=MAX_RESULTS)
        mock_client.assert_called_once_with(
            mock_build_url.return_value, {'include': 'students', 'per_page': MAX_RESULTS})

    @patch('canvas_sdk.utils.build_url')
    @patch('canvas_sdk.client.get')
    def test_sections_list_course_sections_build_url_called_with(self, mock_client, mock_build_url):
        """
        Assert that build_url is called with the expected parameters
        """
        sections.list_course_sections(COURSE_ID)
        mock_build_url.assert_called_once_with('/v1/courses/%d/sections' % COURSE_ID)

    @patch('canvas_sdk.config.LIMIT_PER_PAGE', MAX_RESULTS)
    @patch('canvas_sdk.utils.build_url')
    @patch('canvas_sdk.utils.validate_attr_is_acceptable')
    @patch('canvas_sdk.client.get')
    def test_sections_list_course_sections_using_config_base_api_url(self, mock_client, validate_mock, mock_build_url):
        """
        Assert that list_course_sections is called with the base url value from
        the config file if none is given. 
        """
        with patch.object(sections.list_course_sections, '__defaults__', (None, sections.config.LIMIT_PER_PAGE,)):
            sections.list_course_sections(COURSE_ID)

        mock_client.assert_called_once_with(
            mock_build_url.return_value, {'include': None, 'per_page': MAX_RESULTS})

