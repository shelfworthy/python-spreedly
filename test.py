# -*- coding: utf-8 -*-
import unittest

from api import Client

SPREEDLY_AUTH_TOKEN = '59f064f450af88df24f54281f3d78ad8ee0eb8f0'
SPREEDLY_SITE_NAME = 'shelfworthytest'

class  TestCase(unittest.TestCase):
    def setUp(self):
        self.sclient = Client(SPREEDLY_AUTH_TOKEN, SPREEDLY_SITE_NAME)

        # Remove all subscribers
        self.sclient.cleanup()

    def tearDown(self):
        # Remove all subscribers
        self.sclient.cleanup()

    def test_get_plans(self):
        keys = [
            'date_changed', 'terms', 'name', 'force_recurring', 'feature_level',
            'price', 'enabled', 'plan_type', 'force_renew', 'duration_units',
            'version', 'speedly_site_id', 'duration', 'date_created',
            'speedly_id', 'return_url', 'description'
        ]

        for plan in self.sclient.get_plans():
            self.assertEquals(plan.keys(), keys)

    def test_create_subscriber(self):
        keys = [
            'token', 'date_expiration', 'trial_active', 'date_created',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan'
        ]

        subscriber = self.sclient.create_subscriber(1, 'test')
        self.assertEquals(subscriber.keys(), keys)

        # Delete subscriber
        self.sclient.delete_subscriber(1)

    def test_subscribe(self):
        keys = [
            'token', 'date_expiration', 'trial_active', 'date_created',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan'
        ]

        # Create a subscriber first
        subscriber = self.sclient.create_subscriber(1, 'test')

        # Subscribe to a free trial
        subscription = self.sclient.subscribe(1, 1824, True)
        self.assertEquals(subscriber.keys(), keys)
        assert subscription['trial_active']

        # Delete subscriber
        #self.sclient.delete_subscriber(1)

    def test_delete_subscriber(self):
        self.sclient.create_subscriber(1, 'test')
        self.failUnlessEqual(self.sclient.delete_subscriber(1), 200)

    def test_get_info(self):
        keys = [
            'token', 'date_expiration', 'trial_active', 'date_created',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan'
        ]

        self.sclient.create_subscriber(1, 'test')
        subscriber = self.sclient.get_info(1)
        self.assertEquals(subscriber.keys(), keys)

if __name__ == '__main__':
    unittest.main()

