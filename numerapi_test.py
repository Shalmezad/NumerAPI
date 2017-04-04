import unittest
import os # Needed for getting environment variables, checking file exists
import numerapi
import numpy as np
from datetime import datetime, timedelta 
#NOTE: In order to run the tests,
# You will need to have the following environment variables set:
# NUMERAI_API_EMAIL - The email to use
# NUMERAI_API_PASSWORD - The password to use

class APITestCase(unittest.TestCase):
    def setUp(self):
        email = os.environ['NUMERAI_API_EMAIL']
        password = os.environ['NUMERAI_API_PASSWORD']
        self.napi = numerapi.NumerAPI(email, password)
        # Set up a directory to put files generated:
        self.test_directory = "./test_out"
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)


    '''
    # Temporarily removed since most of this is similar to test with unzip
    def test_download_current_dataset_without_unzip(self):
        #status = self.napi.download_current_dataset(dest_path=self.test_directory, unzip=False)
        status = 1
        # Should be successful:
        self.assertNotEqual(status, None)
        # Should result in a file along the lines of
        # "numerai_dataset_20170404.zip"
        now = datetime.now().strftime('%Y%m%d')
        expected_file_name = 'numerai_dataset_{0}.zip'.format(now)
        expected_file_path = '{0}/{1}'.format(self.test_directory,
                                              expected_file_name)
        self.assertTrue(os.path.exists(expected_file_path))
    '''
    # Test
    '''
    # Temporarily removed since upload does a download as well
    def test_download_current_dataset_with_unzip(self):
        status = self.napi.download_current_dataset(dest_path=self.test_directory, unzip=True)
        # Should be successful:
        self.assertNotEqual(status, None, "Should return a non-None value indicating success")
        # This leaves the zip file as well, so it should exist:
        # "numerai_dataset_20170404.zip"
        now = datetime.now().strftime('%Y%m%d')
        expected_file_name = 'numerai_dataset_{0}.zip'.format(now)
        expected_file_path = '{0}/{1}'.format(self.test_directory,
                                              expected_file_name)
        self.assertTrue(os.path.exists(expected_file_path), "Should download the zip file")
        # Should also create a folder "numerai_dataset"
        expected_file_path = '{0}/{1}'.format(self.test_directory,
                                              'numerai_datasets')
        self.assertTrue(os.path.exists(expected_file_path), "Should have extracted a folder called numerai_datasets")
        # Within that folder should be the following files:
        expected_files = ["example_model.py", 
                          "example_model.r",
                          "example_predictions.csv",
                          "numerai_tournament_data.csv",
                          "numerai_training_data.csv"]
        for expected_file in expected_files:
            expected_file_path = '{0}/{1}/{2}'.format(self.test_directory,
                                                      'numerai_datasets',
                                                      expected_file)
            self.assertTrue(os.path.exists(expected_file_path), "Should have a file extracted called: " + expected_file)
    '''
    # Test
    '''
    def test_upload_prediction(self):
        # So... in order to run this, we need a prediction.
        # There's one in the data set...
        # TODO: Put me back in
        #self.napi.download_current_dataset(dest_path=self.test_directory, unzip=True)
        prediction_file_path = '{0}/{1}/{2}'.format(self.test_directory,
                                                    'numerai_datasets',
                                                    'example_predictions.csv')
        # Alright, run it:
        status = self.napi.upload_prediction(prediction_file_path)
        # And we should get a good status:
        self.assertEqual(status, 200, "Should return a successful status")
    '''

# Test basic routes that don't requite too much info:
class APIBasicRoutesTestCase(unittest.TestCase):
    def setUp(self):
        email = os.environ['NUMERAI_API_EMAIL']
        password = os.environ['NUMERAI_API_PASSWORD']
        self.napi = numerapi.NumerAPI(email, password)


    # Not in the README, may want to update that.
    def test_get_leaderboard(self):
        (data, status) = self.napi.get_leaderboard()
        # Should get a good status:
        self.assertEqual(status, 200, "Should return a successful status")
        # For some reason, it returns a list:
        self.assertIsInstance(data, list)
        # Only one element on that list:
        self.assertTrue(len(data)==1)
        # Grab the main data:
        data = data[0]
        # It's a dictionary of metadata:
        self.assertIsInstance(data, dict)
        # Should have the following keys:
        keys = [u'updated',
                u'end_date',
                u'dataset_id',
                u'_id',
                u'start_date',
                u'leaderboard']
        for key in keys:
            self.assertIn(key, data.keys(), "Metadata should have key: " + key)

        # Main one we care about is the leaderboard:
        leaderboard = data[u'leaderboard']
        # Which should be a list:
        self.assertIsInstance(leaderboard,list)
        # And for testing, should have at least 1 element:
        self.assertTrue(len(leaderboard) > 0, "Leaderboard is empty. Please wait and try again later.")
        # Alright, let's grab somebody:
        user = leaderboard[0]
        # Should be a dictionary:
        self.assertIsInstance(user, dict)
        # Should have the following keys:
        keys = [u'earned',
                u'earnings',
                u'logloss',
                u'rank',
                u'submission_id',
                u'username']
        for key in keys:
            self.assertIn(key, user.keys(), "User leaderboard data should have key: " + key)
        # Alright, just a few more checks:
        # "earnings" should be a dictionary with career:{nmr:X,usd:Y}
        self.assertIsInstance(user[u'earnings'][u'career'][u'nmr'], unicode)
        self.assertIsInstance(user[u'earnings'][u'career'][u'usd'], unicode)
        # Logloss should have a public value:
        self.assertIsInstance(user[u'logloss'][u'public'], unicode)
        # Rank should have a public value:
        self.assertIsInstance(user[u'rank'][u'public'], int)
        # And that covers the main things.

    def test_get_current_competition(self):
        (dataset_id, comp_id, status) = self.napi.get_current_competition()
        # Should be good:
        self.assertEqual(status, 200, "Should return a successful status")


# Test routes that requite a given username. 
# REQUIRES THAT THERE'S DATA ON THE LEADERBOARD (polls first user)
class APIUsernameBasedTestCase(unittest.TestCase):
    def setUp(self):
        email = os.environ['NUMERAI_API_EMAIL']
        password = os.environ['NUMERAI_API_PASSWORD']
        self.napi = numerapi.NumerAPI(email, password)
        # Get a username:
        (data, status) = self.napi.get_leaderboard()
        self.username = data[0][u'leaderboard'][0][u'username']

    def test_get_earnings_per_round(self):
        (earnings,status) = self.napi.get_earnings_per_round(self.username)
        # Should be good:
        self.assertEqual(status, 200, "Should return a successful status")
        # Should get a numpy array:
        self.assertIsInstance(earnings, np.ndarray)
        # Which should have at least 1 element for the leader:
        self.assertTrue(len(earnings) > 0, "Leader has no earnings")

    def test_get_scores(self):
        (scores,status) = self.napi.get_earnings_per_round(self.username)
        # Should be good:
        self.assertEqual(status, 200, "Should return a successful status")
        # Should get a numpy array:
        self.assertIsInstance(scores, np.ndarray)
        # Which should have at least 1 element for the leader:
        self.assertTrue(len(scores) > 0, "Leader has no scores")

    def test_get_user(self):
        (username, logloss, rank, earned, status) = self.napi.get_user(self.username)
        # Should be good:
        self.assertEqual(status, 200, "Should return a successful status")


if __name__ == '__main__':
    unittest.main()
