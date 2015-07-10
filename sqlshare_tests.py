# Tests for SQLShare
# - Matt Stone

from sqlshare_tests_c import *
from sqlshare_settings import *

import os
import sys
import unittest

class SQLShare(SQLShareTests):

    # View Tests
    def view_your_datasets(self):
        self.click_sidebar_link("Yours")
        self.get_datasets()

    def view_all_datasets(self):
        self.click_sidebar_link("All")
        self.get_datasets()

    def view_shared_datasets(self):
        self.click_sidebar_link("Shared")
        self.get_datasets()

    def view_recent_datasets(self):
        self.get_recent_datasets()

    def view_recent_queries(self):
        self.get_recent_queries()

    # Functional Tests
    def dataset_upload(self):
        for attr in ['filename', 'dataset_name', 'dataset_desc', 'dataset_public']:
            setattr(self, attr, getattr(self, 'upload_' + attr))

        self.upload_dataset()

        self.delete_and_assert(self.dataset_name)

    def save_new_query(self):
        self.query = self.working_query
        self.dataset_name = "New Query Save Dataset"
        self.dataset_desc = "Dataset resulting from new query save for automation testing."
        self.dataset_public = False
        self.new_query_action = "save"

        self.new_query()

        self.delete_and_assert("New Query Save Dataset")        

    def download_new_query(self):
        self.query = self.working_query
        self.new_query_action = "download"

        self.new_query()

        time.sleep(2)
        assert os.path.isfile("query_results.csv")
        os.remove("query_results.csv")

    def keyword_search(self):
        self.search_keyword(self.existing_dataset)
        datasets = self.get_datasets()

        for dataset in datasets:
            if dataset['name'].lower() == self.existing_dataset.lower():
                return

        raise AssertionError("Dataset not found in dataset list")

                         

    # Dataset Tests
    def dataset_details(self):
        self.open_dataset(self.existing_dataset)
        details = self.get_dataset_details()
        assert details['title'].lower() == self.existing_dataset.lower()
        assert details['owner'] == self.username
        
    def dataset_toggle_privacy(self):
        self.open_dataset(self.existing_dataset)
        self.private_public_toggle()

    def dataset_share(self):
        self.open_dataset(self.existing_dataset)
        self.share_dataset()

    def dataset_delete(self):
        self.delete_and_assert(self.to_delete_dataset)
        
    def dataset_download(self):
        self.open_dataset(self.existing_dataset)
        self.download_dataset()

        time.sleep(2)
        assert os.path.isfile("query_results.csv")
        os.remove("query_results.csv")

    def dataset_snapshot(self):
        self.dataset_name = "Snapshot Dataset"
        self.dataset_desc = "Snapshot of dataset for automation testing."
        self.dataset_public = False

        self.open_dataset(self.existing_dataset)
        self.snapshot_dataset()

        self.delete_and_assert("Snapshot Dataset")

    # To do new_dataset, derive, run, update
    def delete_and_assert(self, dataset_name):
        self.open_dataset(dataset_name)
        self.delete_dataset()
        time.sleep(3)
        
        self.assert_dataset_deleted(dataset_name)

    def assert_dataset_deleted(self, dataset_name):
        self.click_sidebar_link("All")
        datasets = self.get_datasets()

        names = []
        for dataset in datasets:
            names.append(dataset['name'].lower())

        assert dataset_name.lower() not in names

        
### Main Program

# Get Username and password from env if no settings file and from user if no env vars
username = None
password = None
if not ('username' in settings.keys()):
    try:
        settings['username'] = os.environ['SQLSHARE_USERNAME']
    except KeyError:
        settings['username'] = input("Username: ")

if not ('password' in settings.keys()):
    try:
        settings['password'] = os.environ['SQLSHARE_PASSWORD']
    except KeyError:    
        settings['password'] = getpass.getpass()


# Set settings as attributes
for setting_set in [test_config, settings]:
    for setting in setting_set:
        setattr(SQLShare, setting, setting_set[setting])


# Upload test datasets
if not settings['debug']:
    sql = SQLShare()
    sql.setUp()
    
    for dataset in to_upload:
        for attr in ['filename', 'dataset_name', 'dataset_desc', 'dataset_public']:
            setattr(sql, attr, dataset[attr])

        sql.upload_dataset()

    # Create and run suite
    suite = unittest.TestSuite()

    for test in to_run:
        suite.addTest(SQLShare(test))

    result = unittest.TestResult(verbosity=2)
    runner = unittest.TextTestRunner(stream=sys.stdout)
    runner.run(suite)

    for dataset in to_upload:
        dataset_name = dataset['dataset_name']
        if dataset_name is not sql.to_delete_dataset:
            sql.open_dataset(dataset_name)
            sql.delete_dataset()
    