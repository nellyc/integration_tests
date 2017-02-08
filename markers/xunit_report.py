"""
This module adds the polarion marker to xunit-results,
which allows polarion importer to read polarion info & tests ids from this file.
In the future this can be extended to add information from other markers
"""

import pytest


class JunitExtension(object):
    """
    Add custom properties into junit report.
    """

    markers = (
        ('polarion','polarion-testcase-id'),
    )

    polarion_importer_properties = {
        'polarion-project-id': None,
        'polarion-user-id': 'ci-user',
        'polarion-response-myproduct': None,
    }

    polarion_execution_properties = {
        'polarion-custom-plannedin': None,
        'polarion-custom-isautomated': 'True',
    }

    def __init__(self, config):
        super(JunitExtension, self).__init__()
        self._conf = config

    @property
    def junit(self):
        return getattr(self._conf, '_xml', None)

    def _add_property(self, item, name, value):
        reporter = self.junit.node_reporter(item.nodeid)
        reporter.add_property(name, value)

    def _add_marks(self, item):
        for id, name in self.markers:
            mark_info = item.get_marker(id)
            if mark_info:
                for value in mark_info.args:
                    self._add_property(item, name, value)

    def _add_global_properties(self):
        # junit.add_global_property(k, v) will be available in pytest 3.0
        # If this method doesnt exist we simply won't add global properties node
        if getattr(self.junit, 'add_global_property', None):
            all_properties = dict(
                self.polarion_execution_properties, **self.polarion_importer_properties
            )
            for k, v in all_properties.iteritems():
                self.junit.add_global_property(k, v)

    def pytest_runtest_setup(self, item):
        self._add_marks(item)

    def pytest_sessionstart(self, session):
        self.polarion_execution_properties['polarion-custom-plannedin'] = (
             "CFME_" +
             session.config.getoption('polarion-cfme-version').replace(".", "_")
        )
        self.polarion_importer_properties['polarion-project-id'] = (
            session.config.getoption("polarion-project")
        )
        self.polarion_importer_properties['polarion-response-myproduct'] = (
            session.config.getoption("polarion-project") # for msg bus
        )
        self.polarion_importer_properties['polarion-testrun-id'] = (
            "CFME_{0}_OSE_{1}".format(
                session.config.getoption('polarion-cfme-version'),
                session.config.getoption('polarion-ose-version')
            ).replace(".", "_")
        )
        self._add_global_properties()


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        '--polarion-cfme-version',
        action="store",
        dest="polarion-cfme-version",
        default='',
        help="CFME version for polarion")
    group.addoption(
        '--polarion-ose-version',
        action="store",
        dest="polarion-ose-version",
        default='',
        help="OSE version for polarion")
    group.addoption(
        '--polarion-project',
        action="store",
        dest="polarion-project",
        default='',
        help="Polarion project ID")


def pytest_configure(config):
    if config.pluginmanager.hasplugin('junitxml'):
        config.pluginmanager.register(JunitExtension(config))
