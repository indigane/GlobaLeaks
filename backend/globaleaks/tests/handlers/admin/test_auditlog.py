# -*- coding: utf-8 -*-
from twisted.internet.defer import inlineCallbacks

from globaleaks import anomaly
from globaleaks.handlers.admin import auditlog
from globaleaks.jobs.anomalies import Anomalies
from globaleaks.jobs.statistics import Statistics
from globaleaks.tests import helpers


class TestStatsCollection(helpers.TestHandler):
    _handler = auditlog.StatsCollection

    @inlineCallbacks
    def test_get(self):
        handler = self.request({}, role='admin')
        response = yield handler.get(0)

        self.assertEqual(len(response), 3)
        self.assertEqual(len(response['heatmap']), 7 * 24)

        self.pollute_events(10)

        yield Anomalies().run()
        yield Statistics().run()

        for i in range(2):
            handler = self.request({}, role='admin')
            response = yield handler.get(i)
            self.assertEqual(len(response), 3)
            self.assertEqual(len(response['heatmap']), 7 * 24)


class TestAnomalyCollection(helpers.TestHandler):
    _handler = auditlog.AnomalyCollection

    @inlineCallbacks
    def test_get(self):
        self.pollute_events(10)

        yield Anomalies().run()
        yield Statistics().run()

        handler = self.request({}, role='admin')
        response = yield handler.get()

        # be sure that AnomalyHistory is populated
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 1)


class TestRecentEventsCollection(helpers.TestHandler):
    _handler = auditlog.RecentEventsCollection

    @inlineCallbacks
    def test_get(self):
        self.pollute_events(3)

        yield Statistics().run()

        handler = self.request({}, role='admin')

        response = yield handler.get()
        self.assertTrue(isinstance(response, list))

        for k in ['id', 'duration', 'event', 'creation_date']:
            for elem in response:
                self.assertTrue(k in elem)


class TestJobsTiming(helpers.TestHandler):
    _handler = auditlog.JobsTiming

    @inlineCallbacks
    def test_get(self):
        # TODO: start job mocking the reactor

        handler = self.request({}, role='admin')

        yield handler.get()
